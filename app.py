"""SkyeNova portfolio (skyenova.dev).

Dev:   .venv/bin/python app.py            ->  http://localhost:8420  (override with PORT=...)
Prod:  .venv/bin/gunicorn -w 2 -b 127.0.0.1:8420 app:app

Layout:
  content/    plain Python data (projects, roles, studio, press, links)
              and content/posts/*.md, the blog posts
  sections/   one blueprint per page: work, news, blog, about, press, activity
  studionews/ news pulled from the Solaris, Callisto and Astrofox sites (cached)
  ghactivity/ GitHub activity (cached, private work redacted)
  templates/  base.html + one template (or folder) per page
  static/css/ site.css (shared) + one stylesheet per page
"""
import os
from datetime import date
from pathlib import Path

from flask import Flask, abort, render_template, send_from_directory

from content.core import DISCORD_URL, LINKS, ROLES, TAGLINE, TITLE
from content.studio import COMPANY, DIVISIONS, STILLS
from content.projects import ALSO, PROJECTS
from sections import about, activity, blog, news, press, work

ROOT = Path(__file__).resolve().parent

app = Flask(__name__)
for section in (work, news, blog, about, press, activity):
    app.register_blueprint(section.bp)

NAV = [
    {"label": "Work", "endpoint": "work.index", "section": "work"},
    {"label": "News", "endpoint": "news.index", "section": "news"},
    {"label": "Blog", "endpoint": "blog.index", "section": "blog"},
    {"label": "About", "endpoint": "about.index", "section": "about"},
    {"label": "Press", "endpoint": "press.index", "section": "press"},
    {"label": "Activity", "endpoint": "activity.index", "section": "activity"},
]


@app.context_processor
def inject_globals():
    return {"year": date.today().year, "discord_url": DISCORD_URL, "nav": NAV, "links": LINKS,
            "skye_title": TITLE, "skye_tagline": TAGLINE}


@app.route("/")
def index():
    return render_template(
        "index.html",
        roles=ROLES,
        projects=PROJECTS,
        also=ALSO,
        company=COMPANY,
        divisions=DIVISIONS,
        stills=STILLS,
    )


@app.route("/images/<path:filename>")
def images(filename):
    return send_from_directory(ROOT / "images", filename)


@app.route("/<name>.<ext>")
def root_files(name, ext):
    # Favicons and manifest, which browsers request from the site root.
    if ext not in {"png", "ico", "svg", "webmanifest", "xml"}:
        abort(404)
    return send_from_directory(ROOT, f"{name}.{ext}")


# Design drafts and the old site, kept around for comparison.
DRAFTS = [
    {"slug": "orbit", "name": "Orbit", "blurb": "Callisto-style direction (not picked)."},
    {"slug": "index", "name": "Index", "blurb": "The picked direction, as a single static draft."},
]


@app.route("/drafts/")
def drafts():
    return render_template("preview.html", designs=DRAFTS)


@app.route("/drafts/<slug>/")
def draft(slug):
    if not any(d["slug"] == slug for d in DRAFTS):
        abort(404)
    return send_from_directory(ROOT / "redesigns" / slug, "index.html")


@app.route("/drafts/current/")
def current():
    return send_from_directory(ROOT, "index.html")


@app.route("/drafts/current/<any('index.css', 'index.js'):filename>")
def current_assets(filename):
    return send_from_directory(ROOT, filename)


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8420)), debug=True)
