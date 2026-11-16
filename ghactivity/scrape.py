"""No-token path: the public contributions fragment and the public REST API.

The calendar fragment at github.com/users/<login>/contributions is unofficial
markup, so everything here parses defensively and raises FetchError rather
than guessing when the shape has changed.
"""
import logging
import re
from datetime import date, datetime, timedelta, timezone
from html import unescape

from . import config, redact
from .http import API, FetchError, get_json, get_text

log = logging.getLogger("ghactivity")

CALENDAR_URL = "https://github.com/users/{login}/contributions?from={year}-01-01&to={year}-12-31"

_TD = re.compile(r"<td\b[^>]*\bContributionCalendar-day\b[^>]*>", re.I)
_ATTR = re.compile(r'([\w-]+)="([^"]*)"')
_TIP = re.compile(r"<tool-tip\b([^>]*)>(.*?)</tool-tip>", re.I | re.S)
_COUNT = re.compile(r"^\s*(No|\d[\d,]*)\s+contributions?\b", re.I)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Languages that are build glue or data packs rather than something I write in.
LANGUAGE_DENYLIST = {
    "Batchfile", "mcfunction", "Dockerfile", "Makefile", "CMake", "Shell", "PowerShell",
    "Roff", "Procfile", "Nix", "Smarty", "Rich Text Format", "Jupyter Notebook", "Text",
}

MAX_PUBLIC_REPOS = 12
COMMITS_PER_REPO = 8


def parse_calendar(html):
    """-> [(date, count, level)] sorted. Raises FetchError if the markup has moved."""
    tips = {}
    for attrs, text in _TIP.findall(html):
        a = dict(_ATTR.findall(attrs))
        target = a.get("for")
        m = _COUNT.match(unescape(re.sub(r"<[^>]+>", "", text)))
        if target and m:
            word = m.group(1)
            tips[target] = 0 if word.lower() == "no" else int(word.replace(",", ""))

    days, missing = [], 0
    for tag in _TD.findall(html):
        a = dict(_ATTR.findall(tag))
        raw = a.get("data-date", "")
        if not _DATE.match(raw):
            continue
        try:
            d = date.fromisoformat(raw)
        except ValueError:
            continue
        level_raw = a.get("data-level", "0")
        level = int(level_raw) if level_raw.isdigit() else 0
        count = tips.get(a.get("id"))
        if count is None:
            if level == 0:
                count = 0
            else:
                missing += 1
                continue
        days.append((d, count, min(level, 4)))

    if not days:
        raise FetchError("calendar markup changed: no day cells found")
    if missing > max(3, len(days) // 20):
        raise FetchError(f"calendar markup changed: {missing} days without counts")
    return sorted(days)


def fetch_year(login, year):
    html = get_text(CALENDAR_URL.format(login=login, year=year))
    days = [(d, c) for d, c, _ in parse_calendar(html) if d.year == year]
    if not days:
        raise FetchError(f"calendar for {year} came back empty")
    return days


def fetch_calendar():
    login = config.login()
    today = datetime.now(config.tz()).date()
    years = {}
    for year in range(config.first_year(), today.year + 1):
        days = fetch_year(login, year)
        years[str(year)] = {
            "days": [[d.isoformat(), c] for d, c in days],
            "total": sum(c for _, c in days),
        }
    return {"login": login, "years": years, "recent_repos": []}


# ---------- public REST ----------

def public_repos(login):
    """Public, non-fork, non-archived repos the login owns. Hidden ones are dropped."""
    hidden = config.hidden_repos()
    items = get_json(f"{API}/users/{login}/repos?per_page=100&type=owner&sort=pushed")
    if not isinstance(items, list):
        raise FetchError("unexpected /users/<login>/repos payload")
    repos = []
    for item in items:
        if not isinstance(item, dict) or item.get("private") or item.get("fork") or item.get("archived"):
            continue
        name = item.get("full_name")
        if not name or redact.is_hidden(name, hidden):
            continue
        repos.append({
            "name": name,
            "language": item.get("language"),
            "url": item.get("html_url"),
            "pushed_at": item.get("pushed_at") or "",
        })
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)
    return repos[:MAX_PUBLIC_REPOS]


def fetch_languages():
    login = config.login()
    totals = {}
    repos = public_repos(login)
    for repo in repos:
        try:
            langs = get_json(f"{API}/repos/{repo['name']}/languages")
        except FetchError as e:
            log.info("ghactivity: languages for %s skipped (%s)", repo["name"], e)
            continue
        if not isinstance(langs, dict):
            continue
        for name, size in langs.items():
            if name in LANGUAGE_DENYLIST or not isinstance(size, int):
                continue
            totals[name] = totals.get(name, 0) + size
    languages = sorted(({"name": n, "bytes": b} for n, b in totals.items()), key=lambda x: -x["bytes"])
    return {"scope": "public", "languages": languages, "repo_count": len(repos)}


def fetch_feed():
    """Recent public commits by the login. No line counts (that needs a call per commit)."""
    login = config.login()
    hidden = config.hidden_repos()
    since = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    commits = []
    for repo in public_repos(login):
        view = redact.repo_view(repo["name"], False, repo.get("language"), repo.get("url"), hidden)
        try:
            items = get_json(
                f"{API}/repos/{repo['name']}/commits?author={login}&per_page={COMMITS_PER_REPO}&since={since}"
            )
        except FetchError as e:
            log.info("ghactivity: commits for %s skipped (%s)", repo["name"], e)
            continue
        if not isinstance(items, list):
            continue
        for item in items:
            meta = (item or {}).get("commit") or {}
            when = ((meta.get("committer") or {}).get("date")) or ((meta.get("author") or {}).get("date"))
            if not when:
                continue
            commits.append(redact.commit_view(view, when, meta.get("message"), item.get("html_url")))
    commits.sort(key=lambda c: c["date"], reverse=True)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    recent_languages = {}
    for c in commits:
        if c["language"] and c["date"] >= cutoff:
            recent_languages[c["language"]] = recent_languages.get(c["language"], 0) + 1
    return {
        "scope": "public",
        "commits": commits[:20],
        "times": [c["date"] for c in commits],
        "recent_languages": recent_languages,
    }
