"""News: /news/, everything the studio's sites have published, newest first.

Data comes from the `studionews` package (live fetch, disk cache, fixture
fallback). The homepage strip is fed through an app-wide context processor,
the same way the GitHub card is.
"""
from flask import Blueprint, render_template, request

import studionews

bp = Blueprint("news", __name__, url_prefix="/news")

PAGE = 60


@bp.route("/")
def index():
    view = studionews.news_view(source=request.args.get("source"))
    show_all = request.args.get("all") == "1"
    shown = view["items"] if show_all else view["items"][:PAGE]
    years = []
    for item in shown:
        year = item["date_obj"].year
        if not years or years[-1]["year"] != year:
            years.append({"year": year, "items": []})
        years[-1]["items"].append(item)
    return render_template("news.html", news=view, years=years, hidden=len(view["items"]) - len(shown))


@bp.app_context_processor
def inject_news_strip():
    if request.endpoint != "index":
        return {}
    return {"news": studionews.news_view(limit=7)}
