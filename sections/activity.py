"""Activity: /activity/, GitHub contributions and commits (private work redacted).

Data comes from the `ghactivity` package, which caches and redacts before
anything reaches a template. The homepage card is fed through an app-wide
context processor so index.html can `{% include %}` it without app.py changes.
"""
import logging

from flask import Blueprint, render_template, request

import ghactivity

log = logging.getLogger("ghactivity")

bp = Blueprint("activity", __name__, url_prefix="/activity")


@bp.route("/")
def index():
    return render_template("activity.html", act=ghactivity.activity_view(year=request.args.get("year")))


@bp.app_context_processor
def inject_github_card():
    # Only the homepage renders the partial; everyone else pays nothing for it.
    if request.endpoint != "index":
        return {}
    return {"gh": ghactivity.card_view()}
