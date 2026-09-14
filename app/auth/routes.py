from functools import wraps

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import auth_bp
from app.db import get_db, placeholder


def login_required(view):
    """Decorator to protect routes that require a logged-in user."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please log in to continue.")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        pseudonym = request.form.get("pseudonym", "").strip()
        password = request.form.get("password", "")

        error = None
        if not email or not pseudonym or not password:
            error = "Email, pseudonym, and password are all required."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."

        if error is None:
            db = get_db()
            ph = placeholder()
            cur = db.cursor()

            cur.execute(f"SELECT id FROM users WHERE email = {ph}", (email,))
            if cur.fetchone():
                error = "An account with that email already exists."

        if error is None:
            cur.execute(f"SELECT id FROM users WHERE pseudonym = {ph}", (pseudonym,))
            if cur.fetchone():
                error = "That pseudonym is already taken — try another."

        if error is None:
            password_hash = generate_password_hash(password)
            cur.execute(
                f"INSERT INTO users (email, password_hash, pseudonym) "
                f"VALUES ({ph}, {ph}, {ph})",
                (email, password_hash, pseudonym),
            )
            db.commit()
            flash("Account created! Please log in.")
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        ph = placeholder()
        cur = db.cursor()
        cur.execute(f"SELECT * FROM users WHERE email = {ph}", (email,))
        user = cur.fetchone()

        error = None
        if user is None:
            error = "Incorrect email or password."
        elif not check_password_hash(user["password_hash"], password):
            error = "Incorrect email or password."
        elif user["is_banned"]:
            error = "This account has been suspended."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            session["pseudonym"] = user["pseudonym"]
            session["is_admin"] = bool(user["is_admin"])
            return redirect(url_for("home"))

        flash(error)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))