"""Blog: /blog/, /blog/<slug>/ and /blog/feed.xml. Posts live in content/posts/."""
from datetime import datetime, time, timezone
from email.utils import format_datetime

from flask import Blueprint, Response, abort, render_template, request, url_for

from content import blog
from content.core import SITE_URL

bp = Blueprint("blog", __name__, url_prefix="/blog")


@bp.route("/")
def index():
    tag = request.args.get("tag", "").strip().lower() or None
    posts = blog.all_posts()
    tags = sorted({t for p in posts for t in p["tags"]}, key=str.lower)
    if tag:
        posts = [p for p in posts if tag in (t.lower() for t in p["tags"])]
    return render_template("blog/index.html", posts=posts, tags=tags, tag=tag)


@bp.route("/feed.xml")
def feed():
    posts = blog.all_posts(include_drafts=False)[:30]
    for p in posts:
        p["pub"] = format_datetime(datetime.combine(p["date"], time(9, 0), tzinfo=timezone.utc))
    xml = render_template("blog/feed.xml", posts=posts, site=SITE_URL,
                          built=format_datetime(datetime.now(timezone.utc)))
    return Response(xml, mimetype="application/rss+xml")


@bp.route("/<slug>/")
def post(slug):
    item = blog.get_post(slug)
    if item is None:
        abort(404)
    posts = blog.all_posts()
    i = posts.index(item)
    return render_template(
        "blog/post.html",
        post=item,
        newer=posts[i - 1] if i > 0 else None,
        older=posts[i + 1] if i + 1 < len(posts) else None,
        giscus=blog.giscus(),
        canonical=SITE_URL + url_for("blog.post", slug=slug),
    )


@bp.app_context_processor
def inject_latest_posts():
    if request.endpoint != "index":
        return {}
    return {"posts": blog.all_posts()[:3]}
