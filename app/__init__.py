from flask import Flask

from app import db
from app.auth import auth_bp
from app.onboarding import onboarding_bp
from app.posts import posts_bp
from app.tribes import tribes_bp
from app.zones import zones_bp


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(onboarding_bp, url_prefix="/onboarding")
    app.register_blueprint(posts_bp, url_prefix="/post")
    app.register_blueprint(zones_bp, url_prefix="/zone")
    app.register_blueprint(tribes_bp, url_prefix="/tribe")

    # Blueprints below will be added as we build them out:
    # from app.admin import admin_bp
    # app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def home():
        from flask import session, redirect, url_for
        from app.db import get_db, placeholder

        if not session.get("user_id"):
            return redirect(url_for("auth.login"))

        db = get_db()
        ph = placeholder()
        cur = db.cursor()
        cur.execute(f"SELECT home_zone_id FROM users WHERE id = {ph}", (session["user_id"],))
        user = cur.fetchone()

        if not user or not user["home_zone_id"]:
            return redirect(url_for("onboarding.select_city"))

        return redirect(url_for("zones.feed", zone_id=user["home_zone_id"]))

    return app