"""Blog posts: Markdown files with YAML front matter in content/posts/.

    ---
    title: "A title"
    date: 2026-11-13
    summary: "One or two sentences for the index, the feed and link previews."
    cover: blog/some-image.webp      # optional, relative to images/
    cover_alt: "What the image shows" # needed when there's a cover
    tags: [studio, design]
    draft: true                       # optional
    ---
    Body in Markdown.

The slug is the file name without .md (a leading YYYY-MM-DD- is dropped).
Drafts never go in the feed and only render when BLOG_SHOW_DRAFTS=1.
Files are re-read when they change, so there's no restart to publish.
"""
import math
import os
import re
from datetime import date, datetime
from pathlib import Path

import frontmatter
import markdown

POSTS_DIR = Path(__file__).resolve().parent / "posts"
WORDS_PER_MINUTE = 220
_TRUE = {"1", "true", "yes", "on"}

_cache = {}  # path -> (mtime, post)


def show_drafts():
    return os.environ.get("BLOG_SHOW_DRAFTS", "").strip().lower() in _TRUE


def _as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _load(path):
    raw = frontmatter.load(path)
    day = _as_date(raw.get("date"))
    title = str(raw.get("title") or "").strip()
    if not day or not title:
        return None  # not publishable: no title or no date
    tags = raw.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    md = markdown.Markdown(extensions=["fenced_code", "tables", "footnotes", "toc", "smarty"])
    html = md.convert(raw.content)
    words = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", html)))
    cover = str(raw.get("cover") or "").strip().lstrip("/")
    return {
        "slug": re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem),
        "title": title,
        "date": day,
        "date_text": f"{day.day} {day:%B %Y}",
        "summary": str(raw.get("summary") or "").strip(),
        "cover": cover.removeprefix("images/") or None,
        "cover_alt": str(raw.get("cover_alt") or "").strip(),
        "tags": [str(t).strip() for t in tags if str(t).strip()],
        "draft": bool(raw.get("draft", False)),
        "html": html,
        "minutes": max(1, math.ceil(words / WORDS_PER_MINUTE)),
    }


def all_posts(include_drafts=None):
    """Newest first."""
    if include_drafts is None:
        include_drafts = show_drafts()
    posts = []
    for path in POSTS_DIR.glob("*.md"):
        try:
            mtime = path.stat().st_mtime
            if _cache.get(path, (None,))[0] != mtime:
                _cache[path] = (mtime, _load(path))
            post = _cache[path][1]
        except Exception:  # one broken file shouldn't take the blog down
            post = None
        if post and (include_drafts or not post["draft"]):
            posts.append(post)
    return sorted(posts, key=lambda p: (p["date"], p["slug"]), reverse=True)


def get_post(slug, include_drafts=None):
    return next((p for p in all_posts(include_drafts) if p["slug"] == slug), None)


def giscus():
    """Giscus settings from the environment, or None when comments are off."""
    cfg = {
        "repo": os.environ.get("GISCUS_REPO", "").strip(),
        "repo_id": os.environ.get("GISCUS_REPO_ID", "").strip(),
        "category": os.environ.get("GISCUS_CATEGORY", "").strip(),
        "category_id": os.environ.get("GISCUS_CATEGORY_ID", "").strip(),
    }
    if not (cfg["repo"] and cfg["repo_id"] and cfg["category_id"]):
        return None
    return cfg
