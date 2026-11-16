"""About: /about/."""
from flask import Blueprint, render_template

from content.about import HATS, ME, PORTRAIT, SKILL_GROUPS, STILLS, TEAM_GROUPS, team_count
from content.core import TIMELINE
from content.studio import STILLS as STUDIO_STILLS

bp = Blueprint("about", __name__, url_prefix="/about")

# Timeline path geometry: the SVG is 120 units wide and 100 units per entry,
# stretched over the list with preserveAspectRatio="none". The line weaves
# between x=30 and x=90, crossing each row's centre where the year sits.
PATH_W, PATH_ROW, PATH_LEFT, PATH_RIGHT = 120, 100, 30, 90


def timeline_path(n):
    xs = [PATH_LEFT if i % 2 == 0 else PATH_RIGHT for i in range(n)]
    d = [f"M{xs[0]} 0 V{PATH_ROW // 2}"]
    for i in range(1, n):
        y0 = i * PATH_ROW - PATH_ROW // 2
        y1 = y0 + PATH_ROW
        mid = (y0 + y1) / 2
        d.append(f"C{xs[i - 1]} {mid} {xs[i]} {mid} {xs[i]} {y1}")
    d.append(f"V{n * PATH_ROW}")
    return " ".join(d)


@bp.route("/")
def index():
    n = len(TIMELINE)
    return render_template(
        "about.html",
        timeline=TIMELINE,
        path_d=timeline_path(n),
        path_box=f"0 0 {PATH_W} {n * PATH_ROW}",
        hats=HATS,
        team_groups=TEAM_GROUPS,
        team_count=team_count(),
        me=ME,
        skill_groups=SKILL_GROUPS,
        portrait=PORTRAIT,
        stills=STILLS,
        hero=STUDIO_STILLS.get("sunset"),
    )
