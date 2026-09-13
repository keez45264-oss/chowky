import os
import uuid

from flask import current_app, flash, redirect, request, session, url_for
from werkzeug.utils import secure_filename

from app.auth.routes import login_required
from app.db import get_db, placeholder
from app.posts import posts_bp

VALID_TAGS = {"news", "confession", "question", "event", "chitchat"}


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def _save_image(file_storage):
    """Saves an uploaded image with a random filename, returns the relative
    path to store in the DB, or None if no valid file was given."""
    if not file_storage or file_storage.filename == "":
        return None
    if not _allowed_file(file_storage.filename):
        flash("That image type isn't supported — use png, jpg, jpeg, or gif.")
        return None

    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    file_storage.save(os.path.join(upload_folder, filename))

    return f"uploads/{filename}"


@posts_bp.route("/new", methods=["POST"])
@login_required
def new_post():
    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    content = request.form.get("content", "").strip()
    tag = request.form.get("tag") or None
    is_anonymous = 1 if request.form.get("is_anonymous") else 0
    zone_id = request.form.get("zone_id")

    if tag and tag not in VALID_TAGS:
        tag = None

    if not content:
        flash("Your post can't be empty.")
        return redirect(request.referrer or url_for("home"))

    if not zone_id:
        flash("Something went wrong — no zone selected for this post.")
        return redirect(request.referrer or url_for("home"))

    # Confirm the zone is real before posting to it
    cur.execute(f"SELECT id FROM zones WHERE id = {ph}", (zone_id,))
    if cur.fetchone() is None:
        flash("That zone doesn't exist.")
        return redirect(url_for("home"))

    image_url = _save_image(request.files.get("image"))

    cur.execute(
        f"INSERT INTO posts (author_id, zone_id, content, image_url, tag, is_anonymous) "
        f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
        (session["user_id"], zone_id, content, image_url, tag, is_anonymous),
    )
    db.commit()

    return redirect(url_for("zones.feed", zone_id=zone_id))
