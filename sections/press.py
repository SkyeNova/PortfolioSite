"""Press kit: /press/. Bio, facts, portraits, logos and screenshots to download."""
from flask import Blueprint, render_template

from content import press
from content.core import PRESS_EMAIL, TIMELINE
from content.studio import COMPANY, DIVISIONS

bp = Blueprint("press", __name__, url_prefix="/press")


@bp.route("/")
def index():
    return render_template(
        "press.html",
        press=press,
        facts=[f for f in press.FACTS if f["v"]],
        company=COMPANY,
        divisions=DIVISIONS,
        timeline=TIMELINE,
        press_email=PRESS_EMAIL,
    )
