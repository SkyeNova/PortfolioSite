"""Redaction and streak maths for ghactivity. Run: .venv/bin/python -m unittest tests.test_ghactivity"""
import json
import os
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ghactivity import fixture, graphql, redact, scrape, service, stats  # noqa: E402

# Strings that must never reach a view-model when they belong to private work.
SECRET_NAME = "Secret-Org/Unannounced-Game"
SECRET_ORG = "Secret-Org"
SECRET_MSG = "Add the final boss to Unannounced-Game"
SECRET_OID = "deadbeefcafe0000111122223333444455556666"
SECRET_URL = f"https://github.com/{SECRET_NAME}/commit/{SECRET_OID}"
SECRETS = (SECRET_NAME, SECRET_ORG, "Unannounced", SECRET_MSG, SECRET_OID, SECRET_URL, "final boss")


def leaks(obj):
    blob = json.dumps(obj, default=str)
    return [s for s in SECRETS if s in blob]


class RedactTests(unittest.TestCase):
    def test_private_repo_loses_everything_but_language(self):
        view = redact.repo_view(SECRET_NAME, True, "Java", f"https://github.com/{SECRET_NAME}", set())
        self.assertEqual(view, {"name": None, "private": True, "language": "Java", "url": None})
        self.assertEqual(leaks(view), [])

    def test_hidden_public_repo_is_treated_as_private(self):
        view = redact.repo_view("SkyeNova/voxy", False, "Java", None, {"skyenova/voxy"})
        self.assertTrue(view["private"])
        self.assertIsNone(view["name"])

    def test_public_repo_keeps_name_and_github_url(self):
        view = redact.repo_view("SkyeNova/thinktank", False, "HTML", "https://github.com/SkyeNova/thinktank", set())
        self.assertEqual(view["name"], "SkyeNova/thinktank")
        self.assertEqual(view["url"], "https://github.com/SkyeNova/thinktank")

    def test_private_commit_has_no_message_or_url(self):
        repo = redact.repo_view(SECRET_NAME, True, "Java", None, set())
        c = redact.commit_view(repo, "2026-10-01T12:00:00Z", SECRET_MSG, SECRET_URL, 10, 2)
        self.assertEqual(leaks(c), [])
        self.assertIsNone(c["message"])
        self.assertIsNone(c["url"])
        self.assertEqual((c["additions"], c["deletions"]), (10, 2))

    def test_message_cleaning(self):
        self.assertEqual(redact.clean_message("Fix thing\n\nCo-authored-by: X <x@y.z>"), "Fix thing")
        self.assertEqual(redact.clean_message("Co-authored-by: X <x@y.z>"), None)
        self.assertEqual(redact.clean_message("ping me at someone@example.com please"), "ping me at please")
        self.assertEqual(redact.clean_message(""), None)
        long = "x" * 100
        self.assertEqual(len(redact.clean_message(long)), redact.MAX_MESSAGE)
        self.assertTrue(redact.clean_message(long).endswith("…"))

    def test_hide_list_applies_at_render_time(self):
        commits = [{"repo": "SkyeNova/voxy", "private": False, "message": "hi", "url": "https://github.com/SkyeNova/voxy/commit/1", "date": "2026-01-01T00:00:00Z", "language": None}]
        out = redact.apply_hide_list(commits, {"skyenova/voxy"})
        self.assertTrue(out[0]["private"])
        self.assertIsNone(out[0]["repo"])
        self.assertIsNone(out[0]["message"])
        self.assertIsNone(out[0]["url"])


class GraphQLRedactionTests(unittest.TestCase):
    """Mocked API payloads with a private repo: nothing identifying may survive."""

    def _calendar_payload(self):
        return {
            "user": {
                "id": "U_1",
                "y2026": {"contributionCalendar": {"totalContributions": 5, "weeks": [
                    {"contributionDays": [{"date": "2026-10-14", "contributionCount": 2}, {"date": "2026-10-15", "contributionCount": 3}]}]}},
                "recent": {"restrictedContributionsCount": 40, "commitContributionsByRepository": [
                    {"repository": {"id": "R_priv", "nameWithOwner": SECRET_NAME, "isPrivate": True, "isFork": False,
                                    "primaryLanguage": {"name": "Java"}, "url": f"https://github.com/{SECRET_NAME}"},
                     "contributions": {"nodes": [{"occurredAt": "2026-10-15T00:00:00Z", "commitCount": 4}]}},
                    {"repository": {"id": "R_pub", "nameWithOwner": "SkyeNova/thinktank", "isPrivate": False, "isFork": False,
                                    "primaryLanguage": {"name": "HTML"}, "url": "https://github.com/SkyeNova/thinktank"},
                     "contributions": {"nodes": [{"occurredAt": "2026-10-14T00:00:00Z", "commitCount": 1}]}},
                ]},
            },
            "rateLimit": {"cost": 1, "remaining": 4999},
        }

    def _feed_payload(self):
        return {
            "r0": {"nameWithOwner": SECRET_NAME, "isPrivate": True, "primaryLanguage": {"name": "Java"}, "url": f"https://github.com/{SECRET_NAME}",
                   "defaultBranchRef": {"target": {"history": {"nodes": [
                       {"oid": SECRET_OID, "committedDate": "2026-10-15T19:00:00Z", "messageHeadline": SECRET_MSG, "additions": 120, "deletions": 8, "url": SECRET_URL}]}}}},
            "r1": {"nameWithOwner": "SkyeNova/thinktank", "isPrivate": False, "primaryLanguage": {"name": "HTML"}, "url": "https://github.com/SkyeNova/thinktank",
                   "defaultBranchRef": {"target": {"history": {"nodes": [
                       {"oid": "abc", "committedDate": "2026-10-14T18:00:00Z", "messageHeadline": "Tidy the board", "additions": 3, "deletions": 1,
                        "url": "https://github.com/SkyeNova/thinktank/commit/abc"}]}}}},
        }

    def test_calendar_and_feed_are_redacted(self):
        env = {"GITHUB_TOKEN": "x", "GITHUB_LOGIN": "SkyeNova", "SITE_TZ": "Europe/London"}
        with mock.patch.dict(os.environ, env), mock.patch("ghactivity.graphql.graphql", return_value=self._calendar_payload()):
            calendar = graphql.fetch_calendar()
        self.assertEqual(leaks(calendar), [])
        self.assertEqual(calendar["years"]["2026"]["total"], 5)
        private = [r for r in calendar["recent_repos"] if r["private"]]
        self.assertEqual(len(private), 1)
        self.assertIsNone(private[0]["name"])
        self.assertEqual(private[0]["language"], "Java")

        with mock.patch.dict(os.environ, env), mock.patch("ghactivity.graphql.graphql", return_value=self._feed_payload()) as gql:
            feed = graphql.fetch_feed(calendar)
        self.assertEqual(leaks(feed), [])
        self.assertEqual(len(feed["commits"]), 2)
        private_commit = feed["commits"][0]
        self.assertTrue(private_commit["private"])
        self.assertIsNone(private_commit["message"])
        self.assertIsNone(private_commit["url"])
        self.assertEqual(private_commit["additions"], 120)
        # node ids are passed as variables, never spliced into the query text
        query_text = gql.call_args[0][0]
        self.assertNotIn("R_priv", query_text)

        # And through the full view-model, with the hide list covering the public repo too.
        with mock.patch.dict(os.environ, dict(env, GITHUB_HIDE_REPOS="SkyeNova/thinktank")), \
                mock.patch("ghactivity.service._collect", return_value={
                    "calendar": (calendar, "github", 0), "feed": (feed, "github", 0),
                    "languages": ({"scope": "all", "languages": [], "repo_count": 0}, "github", 0)}):
            view = service.activity_view(year=2026)
            card = service.card_view()
        self.assertEqual(leaks(view), [])
        self.assertEqual(leaks(card), [])
        self.assertNotIn("thinktank", json.dumps(view))
        self.assertTrue(all(c["private"] for c in view["commits"]))


class ScrapeTests(unittest.TestCase):
    HTML = """
    <table><tbody><tr>
    <td tabindex="0" data-date="2026-01-05" id="contribution-day-component-0-1" data-level="2" class="ContributionCalendar-day"></td>
    <td data-date="2026-01-06" id="contribution-day-component-1-1" data-level="0" class="ContributionCalendar-day"></td>
    <td class="ContributionCalendar-day" style="width: 11px"></td>
    </tr></tbody></table>
    <tool-tip for="contribution-day-component-0-1">3 contributions on January 5th.</tool-tip>
    <tool-tip for="contribution-day-component-1-1">No contributions on January 6th.</tool-tip>
    """

    def test_parses_counts_and_skips_padding(self):
        days = scrape.parse_calendar(self.HTML)
        self.assertEqual(days, [(date(2026, 1, 5), 3, 2), (date(2026, 1, 6), 0, 0)])

    def test_rejects_changed_markup(self):
        with self.assertRaises(scrape.FetchError):
            scrape.parse_calendar("<html><body>nothing here</body></html>")
        # Levels without tooltip counts: refuse to guess.
        html = '<td data-date="2026-01-05" id="a" data-level="3" class="ContributionCalendar-day"></td>' * 10
        with self.assertRaises(scrape.FetchError):
            scrape.parse_calendar(html)


class StreakTests(unittest.TestCase):
    def days(self, mapping):
        return {date.fromisoformat(k): v for k, v in mapping.items()}

    def test_current_streak_counts_from_yesterday_when_today_is_zero(self):
        d = self.days({"2026-10-13": 1, "2026-10-14": 2, "2026-10-15": 1, "2026-10-16": 0})
        s = stats.streaks(d, date(2026, 10, 16))
        self.assertEqual(s["current"], 3)

    def test_current_streak_includes_today_when_active(self):
        d = self.days({"2026-10-15": 1, "2026-10-16": 4})
        self.assertEqual(stats.streaks(d, date(2026, 10, 16))["current"], 2)

    def test_streak_breaks_on_zero(self):
        d = self.days({"2026-10-12": 5, "2026-10-13": 0, "2026-10-14": 1, "2026-10-15": 1, "2026-10-16": 0})
        self.assertEqual(stats.streaks(d, date(2026, 10, 16))["current"], 2)

    def test_longest_streak_respects_missing_days(self):
        d = self.days({"2026-01-01": 1, "2026-01-02": 1, "2026-01-03": 1, "2026-01-06": 1, "2026-01-07": 1})
        s = stats.streaks(d, date(2026, 1, 10))
        self.assertEqual(s["longest"], 3)
        self.assertEqual((s["longest_start"], s["longest_end"]), (date(2026, 1, 1), date(2026, 1, 3)))

    def test_no_activity(self):
        s = stats.streaks({}, date(2026, 10, 16))
        self.assertEqual((s["current"], s["longest"]), (0, 0))
        self.assertIsNone(stats.last_active({}, date(2026, 10, 16)))

    def test_this_week_is_monday_to_today(self):
        d = self.days({"2026-10-11": 9, "2026-10-12": 1, "2026-10-14": 2, "2026-10-16": 3})  # 11th is a Sunday
        self.assertEqual(stats.this_week(d, date(2026, 10, 16)), 6)

    def test_year_grid_shape(self):
        d = self.days({"2026-03-01": 4})
        grid = stats.year_grid(d, 2026, date(2026, 10, 16))
        self.assertTrue(all(len(w) == 7 for w in grid["weeks"]))
        self.assertEqual(sum(m["span"] for m in grid["months"]), len(grid["weeks"]))
        self.assertEqual(grid["weeks"][0][0]["date"], "2025-12-29")  # Monday before 1 Jan
        self.assertEqual(grid["total"], 4)
        future = [c for w in grid["weeks"] for c in w if c["future"]]
        self.assertTrue(future and all(c["count"] == 0 and c["level"] == 0 for c in future))

    def test_level_scale_keeps_top_level_rare(self):
        level = stats.level_scale([1, 1, 2, 2, 3, 3, 4, 10])
        self.assertEqual(level(0), 0)
        self.assertEqual(level(1), 1)
        self.assertEqual(level(10), 4)

    def test_punch_card_uses_site_timezone(self):
        tz = ZoneInfo("Europe/London")
        grid = stats.punch_card([datetime(2026, 7, 1, 23, 30, tzinfo=timezone.utc)], tz)  # BST: 00:30 Thursday
        self.assertEqual(grid[3][0], 1)

    def test_relative_wording(self):
        today = date(2026, 10, 16)
        self.assertEqual(stats.relative_day(today, today), "today")
        self.assertEqual(stats.relative_day(date(2026, 10, 15), today), "yesterday")
        self.assertEqual(stats.relative_day(date(2026, 10, 2), today), "2 weeks ago")
        self.assertEqual(stats.relative_day(date(2025, 3, 2), today), "on 2 Mar 2025")


class FixtureTests(unittest.TestCase):
    def test_fixture_is_redacted_and_shifts_to_today(self):
        today = date(2027, 2, 3)
        data = fixture.load(today)
        blob = json.dumps(data)
        for c in data["feed"]["commits"]:
            if c["private"]:
                self.assertIsNone(c["repo"])
                self.assertIsNone(c["message"])
                self.assertIsNone(c["url"])
        days = stats.days_from_years(data["calendar"]["years"])
        self.assertEqual(max(days), today)

    def test_view_renders_from_fixture_without_network(self):
        with mock.patch("ghactivity.service.config.force_fixture", return_value=True):
            view = service.activity_view(year="2025")
        self.assertTrue(view["demo"])
        self.assertEqual(view["year"], 2025)
        self.assertEqual(len(view["grid"]["weeks"]), 53)
        self.assertLessEqual(len(view["languages"]), 6)

    def test_homepage_card_hides_itself_on_sample_data(self):
        sample = fixture.load(date(2026, 10, 16))
        with mock.patch("ghactivity.service._collect", return_value={k: (v, "sample", None) for k, v in sample.items()}):
            self.assertIsNone(service.card_view(force_fixture=False))
            self.assertIsNotNone(service.card_view(force_fixture=True))


if __name__ == "__main__":
    unittest.main()
