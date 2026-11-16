"""Compose cached resources into the two view-models the templates render.

Fallback per resource: fresh cache -> stale cache -> (short wait for a cold
fetch) -> committed fixture. A fixture-backed page is marked `demo` and the
homepage card hides itself rather than show sample numbers.
"""
import logging
from datetime import datetime, timedelta

from . import config, fixture, graphql, redact, scrape, stats
from .cache import Resource
from .http import FetchError

log = logging.getLogger("ghactivity")

PROFILE_URL = "https://github.com/{login}"

# How long a request may wait for a cold fetch (nothing cached at all), in seconds.
COLD_WAIT = {"calendar": 6.0, "feed": 3.0, "languages": 2.0}
MINUTE, HOUR = 60, 3600


def _fetch_calendar(mode):
    return graphql.fetch_calendar() if mode == "token" else scrape.fetch_calendar()


def _fetch_feed(mode):
    if mode != "token":
        return scrape.fetch_feed()
    entry = CALENDAR.peek()
    if not entry or entry.get("mode") != "token":
        raise FetchError("feed waits for the token calendar")
    return graphql.fetch_feed(entry["data"])


def _fetch_languages(mode):
    return graphql.fetch_languages() if mode == "token" else scrape.fetch_languages()


CALENDAR = Resource("calendar", _fetch_calendar, {"token": 30 * MINUTE, "public": 24 * HOUR})
FEED = Resource("feed", _fetch_feed, {"token": 30 * MINUTE, "public": HOUR})
LANGUAGES = Resource("languages", _fetch_languages, {"token": 24 * HOUR, "public": 24 * HOUR})
RESOURCES = {"calendar": CALENDAR, "feed": FEED, "languages": LANGUAGES}


def _now():
    return datetime.now(config.tz())


def _collect(force_fixture):
    """-> {name: (data, source, fetched_at)} where source is github|public|sample."""
    today = _now().date()
    sample = None
    out = {}
    if force_fixture:
        sample = fixture.load(today)
        return {name: (sample[name], "sample", None) for name in RESOURCES}

    mode = config.mode()
    entries = {name: res.get(mode, cold_wait=0) for name, res in RESOURCES.items()}
    # Cold start: wait a little for whatever is still missing (the fetches run in parallel).
    for name, res in RESOURCES.items():
        if entries[name] is None:
            res.wait(COLD_WAIT[name])
            entries[name] = res.peek()
    for name, entry in entries.items():
        if entry is None:
            if sample is None:
                sample = fixture.load(today)
            out[name] = (sample[name], "sample", None)
        else:
            out[name] = (entry["data"], "github" if entry.get("mode") == "token" else "public", entry["fetched_at"])
    return out


def _updated_label(fetched_at, now):
    if fetched_at is None:
        return None
    age = max(0, now.timestamp() - fetched_at)
    if age < 2 * MINUTE:
        return "updated just now"
    if age < HOUR:
        return f"updated {int(age // MINUTE)} min ago"
    if age < 2 * HOUR:
        return "updated an hour ago"
    if age < 48 * HOUR:
        return f"updated {int(age // HOUR)} h ago"
    return f"updated {int(age // (24 * HOUR))} days ago"


def _languages_view(data):
    items = [l for l in data.get("languages", []) if isinstance(l.get("bytes"), int) and l["bytes"] > 0]
    total = sum(l["bytes"] for l in items)
    if not items or total <= 0:
        return []
    top, rest = items[:5], items[5:]
    view = []
    for i, lang in enumerate(top):
        pct = 100 * lang["bytes"] / total
        view.append({"name": lang["name"], "pct": pct, "pct_label": f"{pct:.0f}%" if pct >= 1 else "<1%", "tone": i})
    other = sum(l["bytes"] for l in rest)
    if other:
        pct = 100 * other / total
        view.append({"name": "Other", "pct": pct, "pct_label": f"{pct:.0f}%" if pct >= 1 else "<1%", "tone": 5})
    # Rounded widths add up: hand the leftover to the biggest segment.
    widths = [round(v["pct"], 1) for v in view]
    widths[0] += round(100 - sum(widths), 1)
    for v, w in zip(view, widths):
        v["width"] = round(max(w, 0), 1)
    return view


def _commits_view(feed, now, hidden):
    commits = redact.apply_hide_list(feed.get("commits", []), hidden)[:10]
    biggest = max((c["additions"] or 0) + (c["deletions"] or 0) for c in commits) if commits else 0
    rows = []
    for c in commits:
        try:
            when = stats.parse_datetime(c["date"])
        except (ValueError, TypeError):
            continue
        adds, dels = c.get("additions"), c.get("deletions")
        has_bar = isinstance(adds, int) and isinstance(dels, int) and (adds + dels) > 0 and biggest > 0
        size = adds + dels if has_bar else 0
        # Square-root scale so one big commit doesn't flatten the rest.
        scale = (size / biggest) ** 0.5 if has_bar else 0
        rows.append({
            "repo": c["repo"] if not c["private"] else None,
            "private": c["private"],
            "language": c.get("language"),
            "message": c.get("message") if not c["private"] else None,
            "url": c.get("url") if not c["private"] else None,
            "when": stats.relative_time(when, now),
            "when_iso": when.isoformat(),
            "when_full": when.astimezone(now.tzinfo).strftime("%-d %b %Y, %H:%M"),
            "has_bar": has_bar,
            "add_w": round(scale * adds / size * 100, 1) if has_bar else 0,
            "del_w": round(scale * dels / size * 100, 1) if has_bar else 0,
            "adds": adds if has_bar else None,
            "dels": dels if has_bar else None,
        })
    return rows


def _rhythm_view(feed, days, now):
    times = []
    for t in feed.get("times", []):
        try:
            times.append(stats.parse_datetime(t))
        except (ValueError, TypeError):
            continue
    if len(times) >= 10:
        grid = stats.punch_card(times, now.tzinfo)
        peak = max(max(row) for row in grid) or 1
        rows = []
        for i, row in enumerate(grid):
            cells = []
            for h, n in enumerate(row):
                cells.append({"n": n, "size": round((n / peak) ** 0.5, 2) if n else 0,
                              "label": f"{n} commit{'s' if n != 1 else ''} on {stats.WEEKDAYS_FULL[i]}s around {h:02d}:00"})
            rows.append({"label": stats.WEEKDAYS[i], "cells": cells})
        return {
            "kind": "hours",
            "rows": rows,
            "hours": [f"{h:02d}" if h % 6 == 0 else "" for h in range(24)],
            "caption": stats.rhythm_caption_hours(grid),
            "total": len(times),
        }
    counts = stats.weekday_counts(days, now.date())
    peak = max(counts) or 1
    rows = [{"label": stats.WEEKDAYS[i], "full": stats.WEEKDAYS_FULL[i], "n": n, "pct": round(100 * n / peak, 1)}
            for i, n in enumerate(counts)]
    return {"kind": "weekdays", "rows": rows, "caption": stats.rhythm_caption_weekdays(counts), "total": sum(counts)}


def _top_language(feed, calendar, today):
    """Language with the most commits in the last 30 days, or None."""
    counts = dict(feed.get("recent_languages") or {})
    if not counts:
        cutoff = today - timedelta(days=30)
        for repo in calendar.get("recent_repos") or []:
            lang = repo.get("language")
            if not lang:
                continue
            for d, c in repo.get("days", []):
                try:
                    if stats.parse_date(d) >= cutoff:
                        counts[lang] = counts.get(lang, 0) + int(c)
                except (ValueError, TypeError):
                    continue
    counts = {k: v for k, v in counts.items() if k and v > 0}
    return max(counts, key=counts.get) if counts else None


def activity_view(year=None, force_fixture=None):
    now = _now()
    today = now.date()
    hidden = config.hidden_repos()
    if force_fixture is None:
        force_fixture = config.force_fixture()
    got = _collect(force_fixture)
    calendar, cal_source, cal_at = got["calendar"]
    feed, feed_source, _ = got["feed"]
    languages, lang_source, _ = got["languages"]

    days = stats.days_from_years(calendar.get("years"))
    years = list(range(config.first_year(), today.year + 1))
    try:
        year = int(year) if year is not None else today.year
    except (TypeError, ValueError):
        year = today.year
    if year not in years:
        year = today.year

    totals = stats.totals_by_year(days)
    streak = stats.streaks(days, today)
    last = stats.last_active(days, today)
    busiest = stats.busiest(days, year)
    grid = stats.year_grid(days, year, today)
    login = config.login()

    return {
        "login": login,
        "profile_url": PROFILE_URL.format(login=login),
        "source": cal_source,
        "demo": cal_source == "sample",
        "token_data": feed_source == "github" or (cal_source == "sample" and feed.get("scope") == "all"),
        "updated": _updated_label(cal_at, now),
        "year": year,
        "years": [{"year": y, "total": totals.get(y, 0), "current": y == year} for y in years],
        "grid": grid,
        "all_time": sum(totals.values()),
        "now": {
            "last_active": stats.relative_day(last, today),
            "last_active_date": last.isoformat() if last else None,
            "streak": streak["current"],
            "longest": streak["longest"],
            "longest_range": stats.date_range_label(streak["longest_start"], streak["longest_end"]),
            "this_week": stats.this_week(days, today),
            "year_total": totals.get(today.year, 0),
            "top_language": _top_language(feed, calendar, today),
            "busiest": {"count": busiest["count"], "when": f"{busiest['date'].day} {stats.MONTHS[busiest['date'].month - 1]} {busiest['date'].year}"} if busiest else None,
        },
        "commits": _commits_view(feed, now, hidden),
        "commits_scope": "all" if feed.get("scope") == "all" else "public",
        "rhythm": _rhythm_view(feed, days, now),
        "languages": _languages_view(languages),
        "languages_scope": "all" if languages.get("scope") == "all" else "public",
        "today": today.isoformat(),
    }


def card_view(force_fixture=None):
    """Compact homepage card. None when there is nothing real to show."""
    try:
        now = _now()
        today = now.date()
        if force_fixture is None:
            force_fixture = config.force_fixture()
        got = _collect(force_fixture)
        calendar, cal_source, _ = got["calendar"]
        feed, _, _ = got["feed"]
        if cal_source == "sample" and not force_fixture:
            return None
        days = stats.days_from_years(calendar.get("years"))
        if not days:
            return None
        totals = stats.totals_by_year(days)
        streak = stats.streaks(days, today)
        last = stats.last_active(days, today)
        return {
            "year": today.year,
            "year_total": totals.get(today.year, 0),
            "last_active": stats.relative_day(last, today),
            "streak": streak["current"],
            "this_week": stats.this_week(days, today),
            "top_language": _top_language(feed, calendar, today),
            "grid": stats.mini_grid(days, today, weeks=20),
            "demo": cal_source == "sample",
        }
    except Exception:  # the homepage must never break because of this card
        log.exception("ghactivity: card failed")
        return None
