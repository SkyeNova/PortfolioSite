"""Rebuild data/news_fixture.json and images/news/ from the sibling repos.

    .venv/bin/python -m studionews.build_fixture

Reads (never writes) ../Solaris-Landing-Page-changelog, ../Callisto-Site and
../AstroFoxStudios-Website. Needs ImageMagick's `convert` for the thumbnails;
without it the JSON is still written. Drafts, archived posts, help and legal
documents are skipped, and so is anything in SKIP.
"""
import os
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote

import frontmatter

from .config import FIXTURE_PATH, THUMB_DIR
from .sources import CALLISTO_FOLDERS, _item

REPOS = FIXTURE_PATH.parent.parent.parent

# In a repo but not on the live site when the fixture was last built. Keep
# these out: the fixture must never publish something the real sites haven't.
# Unannounced posts are listed in .env as FIXTURE_SKIP=source/slug,... so their
# slugs stay out of this public repo.
SKIP = {
    ("callisto", "full-orbit"),           # not on callisto.host/api/news (2026-11-13)
} | {tuple(x.strip().split("/", 1)) for x in os.environ.get("FIXTURE_SKIP", "").split(",") if "/" in x}


def _date(value):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    try:
        return date.fromisoformat(str(value)[:10]).isoformat()
    except ValueError:
        return ""


def _thumb(source, slug, image_path):
    """640px webp next to the fixture. Returns True when one exists afterwards."""
    out = THUMB_DIR / f"{source}-{slug}.webp"
    if out.is_file():
        return True
    if not image_path or not image_path.is_file():
        return False
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["convert", str(image_path), "-resize", "640x400^", "-gravity", "center", "-extent", "640x400",
             "-strip", "-quality", "78", str(out)],
            check=True, capture_output=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return out.is_file()


def _static(repo, url_path):
    """'/static/images/x%20y.png' -> repo/static/images/x y.png"""
    if not url_path or not str(url_path).startswith("/static/"):
        return None
    return repo / unquote(str(url_path)).lstrip("/")


def _loose(path):
    """Callisto's front matter is `key: value` lines, not strict YAML."""
    text = path.read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---"):
        for line in text.split("---", 2)[1].splitlines():
            key, sep, value = line.partition(":")
            if sep and key.strip() and not key.startswith((" ", "-", "#")):
                meta[key.strip()] = value.strip().strip("\"'")
    return meta


def solaris():
    repo = REPOS / "Solaris-Landing-Page-changelog"
    for path in sorted((repo / "content" / "blog").glob("*.md")):
        post = frontmatter.load(path)
        if post.get("draft"):
            continue
        slug = path.stem
        changelog = str(post.get("type", "")).lower() == "changelog"
        version = str(post.get("version", "")).strip()
        image = post.get("header_image", "")
        if ("solaris", slug) in SKIP:
            continue
        _thumb("solaris", slug, _static(repo, image))
        yield _item(
            "solaris", slug, str(post.get("title", "")), str(post.get("summary", "")), _date(post.get("date")),
            f"https://playsolaris.net/blog/{slug}",
            f"https://playsolaris.net{image}" if image else (f"https://playsolaris.net/blog/thumb/{slug}.webp" if changelog else ""),
            "changelog" if changelog else "news", f"v{version}" if changelog and version else "",
        )


def callisto():
    repo = REPOS / "Callisto-Site"
    for path in sorted((repo / "content").glob("*.md")):
        post = _loose(path)
        folder = str(post.get("folder", "")).lower()
        if folder not in CALLISTO_FOLDERS or str(post.get("archive", "")).lower() == "true":
            continue
        slug = path.stem
        image = post.get("image", "")
        if ("callisto", slug) in SKIP:
            continue
        _thumb("callisto", slug, _static(repo, image))
        yield _item(
            "callisto", slug, str(post.get("large_title") or post.get("small_title") or ""),
            str(post.get("description", "")), _date(post.get("date")),
            f"https://callisto.host/documents/news/{slug}.html",
            f"https://callisto.host{image}" if image else "",
            "changelog" if folder == "system update" else "news",
        )


def astrofox():
    repo = REPOS / "AstroFoxStudios-Website"
    for path in sorted((repo / "content" / "blog").glob("*.md")):
        post = frontmatter.load(path)
        if post.get("draft"):
            continue
        slug = path.stem
        image = post.get("header_image", "")
        if ("astrofox", slug) in SKIP:
            continue
        _thumb("astrofox", slug, _static(repo, image))
        yield _item(
            "astrofox", slug, str(post.get("title", "")), str(post.get("summary", "")), _date(post.get("date")),
            f"https://astrofoxstudios.com/blog/{slug}",
            f"https://astrofoxstudios.com{image}" if image else "",
        )


def main():
    items = [
        i for gen in (solaris, callisto, astrofox) for i in gen()
        if (i["source"], i["slug"]) not in SKIP and i["title"] and i["date"]
    ]
    items.sort(key=lambda i: i["date"], reverse=True)
    FIXTURE_PATH.write_text(
        json.dumps({"built": date.today().isoformat(), "items": items}, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    thumbs = len(list(THUMB_DIR.glob("*.webp"))) if THUMB_DIR.is_dir() else 0
    print(f"{len(items)} items, {thumbs} thumbnails -> {FIXTURE_PATH}")


if __name__ == "__main__":
    sys.exit(main())
