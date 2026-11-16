"""One fetcher per site. Each returns a list of items:

    {source, slug, title, summary, date (YYYY-MM-DD), url, image, kind, version}

`kind` is "changelog" or "news". `image` is an absolute URL or "". Parsers take
text and are pure, so tests can feed them saved pages. None of these sites has
a feed: Callisto has a JSON endpoint, the other two are scraped from their blog
listing pages, so a markup change there means an empty parse, which raises and
leaves the cached copy (or the fixture) in place.
"""
import html
import json
import re
import urllib.error
import urllib.request
from datetime import datetime
from urllib.parse import urljoin

TIMEOUT = 8
USER_AGENT = "skyenova.dev (studionews; +https://skyenova.dev)"

SOLARIS_URL = "https://playsolaris.net/blog"
CALLISTO_URL = "https://callisto.host/api/news"
ASTROFOX_URL = "https://astrofoxstudios.com/blog"

# Callisto folders that are real news. Help and legal documents, and anything
# without a folder, are left out.
CALLISTO_FOLDERS = {"announcement", "blog", "feature", "news", "system update"}


class FetchError(Exception):
    pass


def get_text(url, accept="text/html"):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read(2_000_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code} for {url}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise FetchError(f"{type(e).__name__} for {url}") from None


def _text(fragment):
    """Inner HTML to plain text."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment or "")).split())


def _first(pattern, block):
    m = re.search(pattern, block, re.S)
    return m.group(1) if m else ""


def _long_date(value):
    """'November 10, 2026' -> '2026-11-10'; '' when it doesn't parse."""
    try:
        return datetime.strptime(value.strip(), "%B %d, %Y").date().isoformat()
    except ValueError:
        return ""


def _iso_date(value):
    try:
        return datetime.strptime(str(value).strip()[:10], "%Y-%m-%d").date().isoformat()
    except ValueError:
        return ""


def _item(source, slug, title, summary, date, url, image="", kind="news", version=""):
    return {
        "source": source, "slug": slug, "title": title, "summary": summary, "date": date,
        "url": url, "image": image, "kind": kind, "version": version,
    }


# ---------- Solaris: blog listing cards ----------

def parse_solaris(page, base=SOLARIS_URL):
    items = []
    for m in re.finditer(r'<a href="(/blog/([^"/?#]+))" class="blog-card([^"]*)"[^>]*>(.*?)</a>', page, re.S):
        path, slug, classes, body = m.groups()
        title = _text(_first(r'class="blog-card-title">(.*?)</h3>', body))
        date = _long_date(_text(_first(r'class="blog-card-date">(.*?)</span>', body)))
        if not title or not date:
            continue
        image = html.unescape(_first(r'<img[^>]+src="([^"]+)"', body))
        version = _text(_first(r'class="chip-ver">(.*?)</span>', body))
        items.append(_item(
            "solaris", slug, title,
            _text(_first(r'class="blog-card-summary">(.*?)</p>', body)),
            date, urljoin(base, path), urljoin(base, image) if image else "",
            "changelog" if "blog-card-changelog" in classes else "news", version,
        ))
    return items


# ---------- Astrofox: blog listing rows ----------

def parse_astrofox(page, base=ASTROFOX_URL):
    items = []
    for m in re.finditer(r'<a href="(/blog/([^"/?#]+))" class="post-row[^"]*"[^>]*>(.*?)</a>', page, re.S):
        path, slug, body = m.groups()
        title = _text(_first(r'class="post-row-title">(.*?)</h3>', body))
        date = _long_date(_text(_first(r'class="post-row-date">(.*?)</span>', body)))
        if not title or not date:
            continue
        image = html.unescape(_first(r'<img[^>]+src="([^"]+)"', body))
        items.append(_item(
            "astrofox", slug, title,
            _text(_first(r'class="post-row-summary">(.*?)</p>', body)),
            date, urljoin(base, path), urljoin(base, image) if image else "",
        ))
    return items


# ---------- Callisto: /api/news ----------

def parse_callisto(payload, base=CALLISTO_URL):
    try:
        rows = json.loads(payload)
    except ValueError:
        raise FetchError("bad JSON from Callisto") from None
    items = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        folder = str(row.get("folder", "")).strip()
        date = _iso_date(row.get("date", ""))
        title = str(row.get("title", "")).strip()
        link = str(row.get("link", "")).strip()
        if folder.lower() not in CALLISTO_FOLDERS or not (date and title and link):
            continue
        image = str(row.get("image", "")).strip()
        items.append(_item(
            "callisto", str(row.get("slug", "")), title, str(row.get("description", "")).strip(),
            date, urljoin(base, link), urljoin(base, image) if image else "",
            "changelog" if folder.lower() == "system update" else "news",
        ))
    return items


def _fetch(url, parse, accept="text/html"):
    items = parse(get_text(url, accept))
    if not items:
        raise FetchError(f"nothing parsed from {url}")
    return items


FETCHERS = {
    "solaris": lambda: _fetch(SOLARIS_URL, parse_solaris),
    "callisto": lambda: _fetch(CALLISTO_URL, parse_callisto, "application/json"),
    "astrofox": lambda: _fetch(ASTROFOX_URL, parse_astrofox),
}
