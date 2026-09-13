from flask import abort, render_template, request, session

from app.auth.routes import login_required
from app.db import get_db, placeholder
from app.zones import zones_bp


@zones_bp.route("/<int:zone_id>/feed")
@login_required
def feed(zone_id):
    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    cur.execute(
        f"SELECT z.id, z.name as zone_name, c.name as city_name "
        f"FROM zones z JOIN cities c ON z.city_id = c.id WHERE z.id = {ph}",
        (zone_id,),
    )
    zone = cur.fetchone()
    if zone is None:
        abort(404)

    sort = request.args.get("sort", "recent")
    order_by = "p.like_count DESC, p.created_at DESC" if sort == "trending" else "p.created_at DESC"

    cur.execute(
        f"SELECT p.id, p.content, p.image_url, p.tag, p.is_anonymous, "
        f"p.like_count, p.created_at, u.pseudonym "
        f"FROM posts p JOIN users u ON p.author_id = u.id "
        f"WHERE p.zone_id = {ph} AND p.is_hidden = {ph} "
        f"ORDER BY {order_by}",
        (zone_id, 0),
    )
    raw_posts = cur.fetchall()

    posts = []
    for post in raw_posts:
        post = dict(post)

        cur.execute(
            f"SELECT id FROM likes WHERE post_id = {ph} AND user_id = {ph}",
            (post["id"], session["user_id"]),
        )
        post["user_liked"] = cur.fetchone() is not None

        cur.execute(
            f"SELECT c.content, c.created_at, u.pseudonym "
            f"FROM comments c JOIN users u ON c.author_id = u.id "
            f"WHERE c.post_id = {ph} ORDER BY c.created_at ASC",
            (post["id"],),
        )
        post["comments"] = cur.fetchall()

        posts.append(post)

    return render_template("zones/feed.html", zone=zone, posts=posts, sort=sort)