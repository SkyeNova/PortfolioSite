"""Cache, fixture fallback and the view-model.

Each source has its own Resource, so one site being down doesn't cost the
others. A request never waits on the network: with nothing cached yet it gets
the fixture for that source while the first fetch runs in the background.
"""
import json
import logging
from datetime import date

from ghactivity.cache import Resource

from . import config
from .sources import FETCHERS

log = logging.getLogger("studionews")

MODE = "live"


class NewsResource(Resource):
    @property
    def path(self):
        return self._dir / f"news_{self.name}.json"


_resources = {
    name: NewsResource(name, (lambda mode, f=fetch: f()), {MODE: config.ttl(), "public": config.ttl()}, config.CACHE_DIR)
    for name, fetch in FETCHERS.items()
}

_fixture = None


def fixture():
    global _fixture
    if _fixture is None:
        try:
            with open(config.FIXTURE_PATH, encoding="utf-8") as f:
                _fixture = json.load(f)
        except (OSError, ValueError):
            log.warning("studionews: no usable fixture at %s", config.FIXTURE_PATH)
            _fixture = {"built": None, "items": []}
    return _fixture


def _source_items(name):
    """(items, live) for one source."""
    if not config.force_fixture():
        entry = _resources[name].get(MODE)
        if entry and entry.get("data"):
            return entry["data"], True
    return [i for i in fixture()["items"] if i.get("source") == name], False


def _decorate(item):
    out = dict(item)
    meta = config.SOURCES[item["source"]]
    out["source_label"] = meta["label"]
    try:
        d = date.fromisoformat(item["date"])
        out["date_obj"] = d
        out["date_text"] = f"{d.day} {d:%b %Y}"
    except ValueError:
        out["date_obj"], out["date_text"] = date.min, ""
    # A local thumbnail (made by build_fixture.py) beats hot-linking a 2 MB PNG.
    thumb = config.THUMB_DIR / f"{item['source']}-{item['slug']}.webp"
    out["thumb"] = f"news/{thumb.name}" if thumb.is_file() else None
    return out


def news_view(source=None, limit=None):
    """Everything a template needs. `source` filters to one site."""
    items, live = [], {}
    for name in config.SOURCES:
        got, is_live = _source_items(name)
        live[name] = is_live
        items.extend(_decorate(i) for i in got if i.get("title") and i.get("url"))
    items.sort(key=lambda i: (i["date_obj"], i["source"] == "solaris"), reverse=True)
    counts = {name: sum(1 for i in items if i["source"] == name) for name in config.SOURCES}
    total = len(items)
    if source in config.SOURCES:
        items = [i for i in items if i["source"] == source]
    else:
        source = None
    if limit:
        items = items[:limit]
    return {
        "items": items,
        "source": source,
        "sources": [
            {"key": k, "label": v["label"], "index": v["index"], "count": counts[k], "live": live[k]}
            for k, v in config.SOURCES.items()
        ],
        "total": total,
        "offline": not any(live.values()),
        "partial": any(live.values()) and not all(live.values()),
    }
