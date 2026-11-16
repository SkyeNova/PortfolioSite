"""The committed sample data, shifted so its last day is today.

data/github_fixture.json has the same three resources the cache holds
(calendar, feed, languages), already in redacted form, plus an `anchor` date.
On load every date moves forward by (today - anchor) so streaks, "this week"
and relative dates read sensibly whenever the sample is shown.
"""
import json
import logging
from datetime import date, datetime, timedelta, timezone

from .config import FIXTURE_PATH
from .stats import parse_date, parse_datetime

log = logging.getLogger("ghactivity")

EMPTY = {
    "calendar": {"login": "SkyeNova", "years": {}, "recent_repos": []},
    "feed": {"scope": "all", "commits": [], "times": [], "recent_languages": {}},
    "languages": {"scope": "all", "languages": [], "repo_count": 0},
}


def _shift_date(value, offset):
    try:
        return (parse_date(value) + offset).isoformat()
    except (ValueError, TypeError):
        return value


def _shift_datetime(value, offset):
    try:
        return (parse_datetime(value) + offset).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except (ValueError, TypeError):
        return value


def load(today, path=FIXTURE_PATH):
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError) as e:
        log.warning("ghactivity: fixture unreadable (%s)", type(e).__name__)
        return {k: json.loads(json.dumps(v)) for k, v in EMPTY.items()}

    try:
        anchor = parse_date(raw.get("anchor"))
    except (ValueError, TypeError):
        anchor = today
    offset = today - anchor

    calendar = raw.get("calendar") or {}
    flat = []
    for block in (calendar.get("years") or {}).values():
        for d, c in block.get("days", []):
            flat.append((parse_date(d) + offset, int(c)))
    years = {}
    for d, c in sorted(flat):
        if d > today:
            continue
        years.setdefault(str(d.year), {"days": [], "total": 0})
        years[str(d.year)]["days"].append([d.isoformat(), c])
        years[str(d.year)]["total"] += c
    recent_repos = []
    for repo in calendar.get("recent_repos") or []:
        repo = dict(repo)
        repo["days"] = [[_shift_date(d, offset), c] for d, c in repo.get("days", [])]
        recent_repos.append(repo)
    calendar = dict(calendar, years=years, recent_repos=recent_repos)

    feed = dict(raw.get("feed") or EMPTY["feed"])
    feed["commits"] = [dict(c, date=_shift_datetime(c.get("date"), offset)) for c in feed.get("commits", [])]
    feed["times"] = [_shift_datetime(t, offset) for t in feed.get("times", [])]

    languages = dict(raw.get("languages") or EMPTY["languages"])
    return {"calendar": calendar, "feed": feed, "languages": languages}
