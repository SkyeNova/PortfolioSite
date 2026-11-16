"""News from Skye's other sites, for the homepage strip and /news/.

Public surface:
    news_view(source=None, limit=None) -> view-model for templates

Three sources (see sources.py): the Solaris blog and changelogs, the Callisto
news API and the Astrofox blog. Each is fetched from the live site, cached on
disk with a TTL (ghactivity's stale-while-revalidate Resource) and falls back
to data/news_fixture.json, which build_fixture.py makes from the sibling repos.
"""
from .service import news_view

__all__ = ["news_view"]
