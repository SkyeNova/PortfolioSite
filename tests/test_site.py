"""Smoke tests for the pages, the blog and the news aggregator.

    .venv/bin/python -m unittest discover -s tests

Nothing here touches the network: NEWS_FORCE_FIXTURE keeps studionews on the
committed fixture and the parsers are fed inline markup.
"""
import os
import unittest
import xml.etree.ElementTree as ET

os.environ["NEWS_FORCE_FIXTURE"] = "1"
os.environ["GITHUB_FORCE_FIXTURE"] = "1"

from pathlib import Path  # noqa: E402

from app import app  # noqa: E402
from content import blog  # noqa: E402

# Tests run against their own posts, so the real blog can be empty.
blog.POSTS_DIR = Path(__file__).resolve().parent / "fixtures" / "posts"

# Names that must never appear on the site. Kept out of this public repo:
# set UNANNOUNCED_NAMES (comma separated) in .env.
UNANNOUNCED = [n.strip().lower() for n in os.environ.get("UNANNOUNCED_NAMES", "").split(",") if n.strip()]
from studionews import news_view, sources  # noqa: E402

GISCUS_KEYS = ("GISCUS_REPO", "GISCUS_REPO_ID", "GISCUS_CATEGORY", "GISCUS_CATEGORY_ID")


class Pages(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()
        os.environ["BLOG_SHOW_DRAFTS"] = "1"
        for k in GISCUS_KEYS:
            os.environ.pop(k, None)

    def test_pages_render(self):
        for path in ("/", "/work/", "/work/solaris/", "/news/", "/news/?source=callisto", "/blog/",
                     "/blog/hello/", "/press/", "/about/", "/activity/"):
            with self.subTest(path=path):
                self.assertEqual(self.c.get(path).status_code, 200)
        self.assertEqual(self.c.get("/blog/not-a-post/").status_code, 404)

    def test_unannounced_game_is_not_named(self):
        if not UNANNOUNCED:
            self.skipTest("UNANNOUNCED_NAMES not set")
        for path in ("/", "/news/?all=1", "/press/", "/about/", "/work/unannounced/", "/blog/"):
            with self.subTest(path=path):
                page = self.c.get(path).get_data(as_text=True).lower()
                for name in UNANNOUNCED:
                    self.assertNotIn(name, page)

    def test_drafts_hidden_by_default_and_never_in_feed(self):
        feed = self.c.get("/blog/feed.xml")
        self.assertEqual(feed.status_code, 200)
        root = ET.fromstring(feed.data)
        drafts = {p["title"] for p in blog.all_posts(True) if p["draft"]}
        self.assertFalse(drafts & {i.findtext("title") for i in root.iter("item")})
        os.environ["BLOG_SHOW_DRAFTS"] = ""
        self.assertEqual(self.c.get("/blog/hello/").status_code, 404)

    def test_giscus_only_when_configured(self):
        self.assertNotIn("giscus.app", self.c.get("/blog/hello/").get_data(as_text=True))
        os.environ.update(GISCUS_REPO="someone/repo", GISCUS_REPO_ID="R_x", GISCUS_CATEGORY_ID="DIC_x")
        page = self.c.get("/blog/hello/").get_data(as_text=True)
        self.assertIn("giscus.app/client.js", page)
        self.assertIn('data-repo="someone/repo"', page)


class News(unittest.TestCase):
    def test_fixture_view(self):
        view = news_view()
        self.assertTrue(view["offline"])
        self.assertGreater(len(view["items"]), 10)
        dates = [i["date"] for i in view["items"]]
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertEqual({i["source"] for i in news_view(source="astrofox")["items"]}, {"astrofox"})

    def test_parse_solaris(self):
        page = '''<a href="/blog/2026-11-10-changelog-v0-6-1" class="blog-card fade-in blog-card-changelog" style="x">
            <img src="/blog/thumb/a.webp?v=1" alt="x"><span class="blog-card-date">November 10, 2026</span>
            <span class="chip-ver">v0.6.1</span><h3 class="blog-card-title">Cosmetics &amp; Voice</h3>
            <p class="blog-card-summary">It&#39;s in.</p></a>'''
        (item,) = sources.parse_solaris(page)
        self.assertEqual((item["title"], item["date"], item["kind"], item["version"], item["summary"]),
                         ("Cosmetics & Voice", "2026-11-10", "changelog", "v0.6.1", "It's in."))
        self.assertEqual(item["image"], "https://playsolaris.net/blog/thumb/a.webp?v=1")

    def test_parse_astrofox(self):
        page = '''<a href="/blog/welcome" class="post-row reveal"><img src="/static/a%20b.png" alt="">
            <h3 class="post-row-title">Welcome</h3><p class="post-row-summary">Hi.</p>
            <span class="post-row-date">July 25, 2026</span></a>'''
        (item,) = sources.parse_astrofox(page)
        self.assertEqual((item["slug"], item["date"], item["url"]),
                         ("welcome", "2026-07-25", "https://astrofoxstudios.com/blog/welcome"))

    def test_parse_callisto_drops_help_legal_and_blank_rows(self):
        payload = '''[{"title":"Aurora 1.4","date":"2026-08-01","folder":"System Update","slug":"a","link":"/documents/news/a.html","image":"","description":"d"},
            {"title":"","date":"","folder":"","slug":"plan","link":"/documents/news/plan.html"},
            {"title":"Terms","date":"2026-01-01","folder":"Legal","slug":"tos","link":"/x"}]'''
        items = sources.parse_callisto(payload)
        self.assertEqual([i["slug"] for i in items], ["a"])
        self.assertEqual(items[0]["kind"], "changelog")


if __name__ == "__main__":
    unittest.main()
