"""Work: /work/ (all projects) and /work/<slug>/ (one project)."""
from flask import Blueprint, abort, render_template

from content.projects import ALSO, PROJECTS, get_project, neighbours

bp = Blueprint("work", __name__, url_prefix="/work")


@bp.route("/")
def index():
    return render_template("work/index.html", projects=PROJECTS, also=ALSO)


@bp.route("/<slug>/")
def detail(slug):
    project = get_project(slug)
    if project is None:
        abort(404)
    prev, nxt = neighbours(slug)
    return render_template(
        "work/detail.html",
        project=project,
        prev=prev,
        next=nxt,
        number=PROJECTS.index(project) + 1,
        total=len(PROJECTS),
    )
