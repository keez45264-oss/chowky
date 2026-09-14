from functools import wraps

from flask import abort, flash, redirect, render_template, session, url_for

from app.auth.routes import login_required
from app.db import get_db, placeholder
from app.admin import admin_bp


def admin_required(view):
    """Decorator for routes that only admins may access."""

    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            flash("You don't have access to that page.")
            return redirect(url_for("home"))
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/")
@admin_required
def dashboard():
    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    cur.execute(
        f"SELECT p.id, p.content, p.image_url, p.tag, p.is_anonymous, "
        f"p.report_count, p.created_at, u.pseudonym, u.email, "
        f"z.name as zone_name, t.name as tribe_name "
        f"FROM posts p "
        f"JOIN users u ON p.author_id = u.id "
        f"LEFT JOIN zones z ON p.zone_id = z.id "
        f"LEFT JOIN tribes t ON p.tribe_id = t.id "
        f"WHERE p.is_hidden = {ph} "
        f"ORDER BY p.report_count DESC, p.created_at DESC",
        (1,),
    )
    raw_posts = cur.fetchall()

    posts = []
    for post in raw_posts:
        post = dict(post)
        cur.execute(
            f"SELECT reason, created_at FROM reports WHERE post_id = {ph} ORDER BY created_at DESC",
            (post["id"],),
        )
        post["reports"] = cur.fetchall()
        posts.append(post)

    return render_template("admin/dashboard.html", posts=posts)


@admin_bp.route("/post/<int:post_id>/restore", methods=["POST"])
@admin_required
def restore_post(post_id):
    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    cur.execute(f"SELECT id FROM posts WHERE id = {ph}", (post_id,))
    if cur.fetchone() is None:
        abort(404)

    cur.execute(
        f"UPDATE posts SET is_hidden = {ph}, report_count = {ph} WHERE id = {ph}",
        (0, 0, post_id),
    )
    cur.execute(f"DELETE FROM reports WHERE post_id = {ph}", (post_id,))
    db.commit()

    flash("Post restored.")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/post/<int:post_id>/remove", methods=["POST"])
@admin_required
def remove_post(post_id):
    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    cur.execute(f"SELECT id FROM posts WHERE id = {ph}", (post_id,))
    if cur.fetchone() is None:
        abort(404)

    cur.execute(f"DELETE FROM posts WHERE id = {ph}", (post_id,))
    db.commit()

    flash("Post permanently removed.")
    return redirect(url_for("admin.dashboard"))