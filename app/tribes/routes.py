from flask import abort, flash, redirect, render_template, request, session, url_for

from app.auth.routes import login_required
from app.db import get_db, placeholder
from app.tribes import tribes_bp


def _get_user_city_id(cur, ph):
    """Looks up the city the logged-in user is currently in, via their zone."""
    cur.execute(
        f"SELECT z.city_id, c.name as city_name FROM users u "
        f"JOIN zones z ON u.current_zone_id = z.id "
        f"JOIN cities c ON z.city_id = c.id "
        f"WHERE u.id = {ph}",
        (session["user_id"],),
    )
    return cur.fetchone()


@tribes_bp.route("/")
@login_required
def list_tribes():
    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    city = _get_user_city_id(cur, ph)
    if city is None:
        flash("Pick your zone first before browsing tribes.")
        return redirect(url_for("onboarding.select_city"))

    cur.execute(
        f"SELECT t.id, t.name, t.description, "
        f"(SELECT COUNT(*) FROM tribe_members tm WHERE tm.tribe_id = t.id) as member_count, "
        f"(SELECT COUNT(*) FROM tribe_members tm WHERE tm.tribe_id = t.id AND tm.user_id = {ph}) as joined "
        f"FROM tribes t WHERE t.city_id = {ph} ORDER BY t.name",
        (session["user_id"], city["city_id"]),
    )
    tribes = cur.fetchall()

    return render_template("tribes/list.html", tribes=tribes, city_name=city["city_name"])


@tribes_bp.route("/<int:tribe_id>/join", methods=["POST"])
@login_required
def join_tribe(tribe_id):
    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    cur.execute(f"SELECT id FROM tribes WHERE id = {ph}", (tribe_id,))
    if cur.fetchone() is None:
        abort(404)

    cur.execute(
        f"SELECT id FROM tribe_members WHERE user_id = {ph} AND tribe_id = {ph}",
        (session["user_id"], tribe_id),
    )
    if cur.fetchone() is None:
        cur.execute(
            f"INSERT INTO tribe_members (user_id, tribe_id) VALUES ({ph}, {ph})",
            (session["user_id"], tribe_id),
        )
        db.commit()

    return redirect(url_for("tribes.list_tribes"))


@tribes_bp.route("/<int:tribe_id>/leave", methods=["POST"])
@login_required
def leave_tribe(tribe_id):
    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    cur.execute(
        f"DELETE FROM tribe_members WHERE user_id = {ph} AND tribe_id = {ph}",
        (session["user_id"], tribe_id),
    )
    db.commit()

    return redirect(url_for("tribes.list_tribes"))


@tribes_bp.route("/<int:tribe_id>/feed")
@login_required
def feed(tribe_id):
    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    cur.execute(
        f"SELECT t.id, t.name, t.description, c.name as city_name "
        f"FROM tribes t JOIN cities c ON t.city_id = c.id WHERE t.id = {ph}",
        (tribe_id,),
    )
    tribe = cur.fetchone()
    if tribe is None:
        abort(404)

    cur.execute(
        f"SELECT id FROM tribe_members WHERE user_id = {ph} AND tribe_id = {ph}",
        (session["user_id"], tribe_id),
    )
    is_member = cur.fetchone() is not None

    sort = request.args.get("sort", "recent")
    order_by = "p.like_count DESC, p.created_at DESC" if sort == "trending" else "p.created_at DESC"

    cur.execute(
        f"SELECT p.id, p.content, p.image_url, p.tag, p.is_anonymous, "
        f"p.like_count, p.created_at, u.pseudonym "
        f"FROM posts p JOIN users u ON p.author_id = u.id "
        f"WHERE p.tribe_id = {ph} AND p.is_hidden = {ph} "
        f"ORDER BY {order_by}",
        (tribe_id, 0),
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

    return render_template(
        "tribes/feed.html", tribe=tribe, posts=posts, sort=sort, is_member=is_member
    )