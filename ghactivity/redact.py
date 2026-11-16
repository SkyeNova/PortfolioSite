"""Decide what a repo or commit is allowed to say about itself.

Rule: a repo keeps its name and URL only if GitHub says it is public AND it is
not in GITHUB_HIDE_REPOS. Everything else collapses to "a private repo" plus,
at most, a language. Private commits keep a timestamp and line counts only.
"""
import re

PRIVATE_LABEL = "a private repo"
MAX_MESSAGE = 72

_EMAIL = re.compile(r"<?[\w.+-]+@[\w-]+(?:\.[\w-]+)+>?")
_TRAILER = re.compile(
    r"^\s*(co-authored-by|signed-off-by|reviewed-by|acked-by|tested-by|reported-by|"
    r"change-id|fixes|closes|refs?)\s*:",
    re.I,
)
_GITHUB_URL = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(/|$)")


def is_hidden(name, hidden):
    return bool(name) and name.lower() in hidden


def clean_message(text):
    """First line only, no emails or trailers, ~72 chars. None if nothing is left."""
    if not text:
        return None
    lines = [line for line in str(text).strip().splitlines() if line.strip()]
    if not lines:
        return None
    first = lines[0]
    if _TRAILER.match(first):
        return None
    first = _EMAIL.sub("", first)
    first = re.sub(r"\s+", " ", first).strip(" \t-:")
    if not first:
        return None
    if len(first) > MAX_MESSAGE:
        first = first[: MAX_MESSAGE - 1].rstrip() + "…"
    return first


def repo_view(name, private, language=None, url=None, hidden=()):
    """The shareable shape of a repo. Private or hidden: no name, no URL."""
    if private or not name or is_hidden(name, hidden):
        return {"name": None, "private": True, "language": language or None, "url": None}
    url = url if url and _GITHUB_URL.match(url) else f"https://github.com/{name}"
    return {"name": name, "private": False, "language": language or None, "url": url}


def commit_view(repo, date_iso, message=None, url=None, additions=None, deletions=None):
    """`repo` must already have been through repo_view()."""
    private = bool(repo.get("private")) or not repo.get("name")
    if private:
        message, url = None, None
    elif url and not _GITHUB_URL.match(url):
        url = None
    return {
        "repo": None if private else repo["name"],
        "private": private,
        "language": repo.get("language") or None,
        "date": date_iso,
        "message": clean_message(message) if message else None,
        "url": url,
        "additions": additions if isinstance(additions, int) else None,
        "deletions": deletions if isinstance(deletions, int) else None,
    }


def apply_hide_list(commits, hidden):
    """Second pass at render time, so a newly hidden repo vanishes without a refetch."""
    out = []
    for c in commits:
        if not c.get("private") and is_hidden(c.get("repo"), hidden):
            c = dict(c, repo=None, private=True, message=None, url=None)
        out.append(c)
    return out
