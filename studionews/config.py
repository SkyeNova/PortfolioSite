"""Settings for the news aggregator (see .env.example).

    NEWS_TTL_MINUTES    how long a fetched copy counts as fresh (default 30)
    NEWS_FORCE_FIXTURE  1 to skip the network and serve data/news_fixture.json
"""
import os

from ghactivity.config import CACHE_DIR, ROOT  # also loads .env

FIXTURE_PATH = ROOT / "data" / "news_fixture.json"
THUMB_DIR = ROOT / "images" / "news"

_TRUE = {"1", "true", "yes", "on"}

# Display order, labels and where "all posts" lives on each site.
SOURCES = {
    "solaris": {"label": "Solaris", "site": "https://playsolaris.net", "index": "https://playsolaris.net/blog"},
    "callisto": {"label": "Callisto", "site": "https://callisto.host", "index": "https://callisto.host/news"},
    "astrofox": {"label": "Astrofox", "site": "https://astrofoxstudios.com", "index": "https://astrofoxstudios.com/blog"},
}


def ttl():
    try:
        return max(1, int(os.environ.get("NEWS_TTL_MINUTES", "30"))) * 60
    except ValueError:
        return 1800


def force_fixture():
    return os.environ.get("NEWS_FORCE_FIXTURE", "").strip().lower() in _TRUE


__all__ = ["CACHE_DIR", "FIXTURE_PATH", "THUMB_DIR", "SOURCES", "ttl", "force_fixture"]
