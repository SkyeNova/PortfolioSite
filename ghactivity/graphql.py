"""Token path: three GraphQL queries, normalised and redacted before they return.

Query 1  calendar per year (aliased, each span <= 1 year) + the last 90 days'
         commitContributionsByRepository, which seeds query 2.
Query 2  commit history on the default branch of the top repos, filtered to me.
Query 3  language bytes across every repo I own or belong to.
"""
import logging
import re
from datetime import datetime, timedelta, timezone

from . import config, redact
from .http import FetchError, graphql
from .scrape import LANGUAGE_DENYLIST

log = logging.getLogger("ghactivity")

FEED_REPOS = 12
FEED_DAYS = 90
FEED_PER_REPO = 30
FEED_KEEP = 20

_YEAR_BLOCK = """
    y{year}: contributionsCollection(from: "{start}", to: "{end}") {{
        contributionCalendar {{
            totalContributions
            weeks {{ contributionDays {{ date contributionCount }} }}
        }}
    }}"""

_CALENDAR_QUERY = """
query Calendar($login: String!, $recentFrom: DateTime!, $now: DateTime!) {{
    user(login: $login) {{
        id
        {years}
        recent: contributionsCollection(from: $recentFrom, to: $now) {{
            totalCommitContributions
            restrictedContributionsCount
            commitContributionsByRepository(maxRepositories: 25) {{
                repository {{ id nameWithOwner isPrivate isFork primaryLanguage {{ name }} url }}
                contributions(first: 100) {{ nodes {{ occurredAt commitCount }} }}
            }}
        }}
    }}
    rateLimit {{ cost remaining }}
}}"""

_REPO_BLOCK = """
    r{i}: node(id: $id{i}) {{
        ... on Repository {{
            nameWithOwner isPrivate primaryLanguage {{ name }} url
            defaultBranchRef {{ target {{ ... on Commit {{
                history(first: {per_repo}, since: $since, author: {{ id: $uid }}) {{
                    nodes {{ oid committedDate authoredDate messageHeadline additions deletions url }}
                }}
            }} }} }}
        }}
    }}"""

_LANGUAGES_QUERY = """
query Languages {
    viewer {
        login
        repositories(first: 100, isFork: false, ownerAffiliations: [OWNER, ORGANIZATION_MEMBER, COLLABORATOR],
                     orderBy: { field: PUSHED_AT, direction: DESC }) {
            nodes {
                nameWithOwner isPrivate isArchived
                languages(first: 10, orderBy: { field: SIZE, direction: DESC }) {
                    edges { size node { name } }
                }
            }
        }
    }
    rateLimit { cost remaining }
}"""

_NODE_ID = re.compile(r"^[A-Za-z0-9_=:-]{4,200}$")


def _iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_calendar():
    token, login = config.token(), config.login()
    hidden = config.hidden_repos()
    now = datetime.now(timezone.utc)
    this_year = datetime.now(config.tz()).year

    blocks = []
    for year in range(config.first_year(), this_year + 1):
        end = f"{year}-12-31T23:59:59Z" if year < this_year else _iso(now)
        blocks.append(_YEAR_BLOCK.format(year=year, start=f"{year}-01-01T00:00:00Z", end=end))
    query = _CALENDAR_QUERY.format(years="".join(blocks))
    variables = {"login": login, "recentFrom": _iso(now - timedelta(days=FEED_DAYS)), "now": _iso(now)}

    data = graphql(query, variables, token)
    user = data.get("user") or {}
    if not user.get("id"):
        raise FetchError("user not found")

    years = {}
    for key, value in user.items():
        if not key.startswith("y") or not key[1:].isdigit():
            continue
        calendar = (value or {}).get("contributionCalendar") or {}
        days = []
        for week in calendar.get("weeks") or []:
            for day in week.get("contributionDays") or []:
                if day.get("date"):
                    days.append([str(day["date"])[:10], int(day.get("contributionCount") or 0)])
        years[key[1:]] = {"days": days, "total": int(calendar.get("totalContributions") or sum(c for _, c in days))}
    if not years:
        raise FetchError("no calendar years in response")

    recent_repos = []
    recent = user.get("recent") or {}
    for item in recent.get("commitContributionsByRepository") or []:
        repo = item.get("repository") or {}
        node_id = repo.get("id")
        if not node_id or not _NODE_ID.match(str(node_id)):
            continue
        view = redact.repo_view(
            repo.get("nameWithOwner"), bool(repo.get("isPrivate")),
            (repo.get("primaryLanguage") or {}).get("name"), repo.get("url"), hidden,
        )
        nodes = ((item.get("contributions") or {}).get("nodes")) or []
        view["node_id"] = node_id
        view["fork"] = bool(repo.get("isFork"))
        view["days"] = [[str(n.get("occurredAt"))[:10], int(n.get("commitCount") or 0)] for n in nodes if n.get("occurredAt")]
        view["commits"] = sum(c for _, c in view["days"])
        recent_repos.append(view)
    recent_repos.sort(key=lambda r: -r["commits"])

    return {
        "login": login,
        "user_id": user["id"],
        "years": years,
        "recent_repos": recent_repos,
        "restricted_recent": int(recent.get("restrictedContributionsCount") or 0),
    }


def fetch_feed(calendar):
    """Needs the calendar resource (for the user id and repo node ids)."""
    token = config.token()
    hidden = config.hidden_repos()
    if not calendar or not calendar.get("user_id"):
        raise FetchError("feed needs the calendar first")
    repos = [r for r in calendar.get("recent_repos") or [] if r.get("node_id") and not r.get("fork")][:FEED_REPOS]
    if not repos:
        return {"scope": "all", "commits": [], "times": [], "recent_languages": {}}

    blocks = "".join(_REPO_BLOCK.format(i=i, per_repo=FEED_PER_REPO) for i in range(len(repos)))
    declared = " ".join(f"$id{i}: ID!" for i in range(len(repos)))
    query = f"query Feed($uid: ID!, $since: GitTimestamp!, {declared}) {{{blocks}\n    rateLimit {{ cost remaining }}\n}}"
    now = datetime.now(timezone.utc)
    variables = {"uid": calendar["user_id"], "since": _iso(now - timedelta(days=FEED_DAYS))}
    for i, repo in enumerate(repos):
        variables[f"id{i}"] = repo["node_id"]

    data = graphql(query, variables, token)
    commits = []
    for i, _ in enumerate(repos):
        node = data.get(f"r{i}") or {}
        view = redact.repo_view(
            node.get("nameWithOwner"), bool(node.get("isPrivate", True)),
            (node.get("primaryLanguage") or {}).get("name"), node.get("url"), hidden,
        )
        history = ((((node.get("defaultBranchRef") or {}).get("target")) or {}).get("history")) or {}
        for c in history.get("nodes") or []:
            when = c.get("committedDate") or c.get("authoredDate")
            if not when:
                continue
            commits.append(redact.commit_view(
                view, when, c.get("messageHeadline"), c.get("url"), c.get("additions"), c.get("deletions"),
            ))
    commits.sort(key=lambda c: c["date"], reverse=True)

    cutoff = (now - timedelta(days=30)).isoformat()
    recent_languages = {}
    for c in commits:
        if c["language"] and c["date"] >= cutoff:
            recent_languages[c["language"]] = recent_languages.get(c["language"], 0) + 1
    return {
        "scope": "all",
        "commits": commits[:FEED_KEEP],
        "times": [c["date"] for c in commits],
        "recent_languages": recent_languages,
    }


def fetch_languages():
    token = config.token()
    hidden = config.hidden_repos()
    data = graphql(_LANGUAGES_QUERY, {}, token)
    nodes = (((data.get("viewer") or {}).get("repositories")) or {}).get("nodes") or []
    totals, count = {}, 0
    for repo in nodes:
        if not repo or repo.get("isArchived") or redact.is_hidden(repo.get("nameWithOwner"), hidden):
            continue
        count += 1
        for edge in ((repo.get("languages") or {}).get("edges")) or []:
            name = ((edge.get("node") or {}).get("name"))
            size = edge.get("size")
            if not name or name in LANGUAGE_DENYLIST or not isinstance(size, int):
                continue
            totals[name] = totals.get(name, 0) + size
    languages = sorted(({"name": n, "bytes": b} for n, b in totals.items()), key=lambda x: -x["bytes"])
    return {"scope": "all", "languages": languages, "repo_count": count}
