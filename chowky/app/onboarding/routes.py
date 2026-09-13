from flask import flash, redirect, render_template, request, session, url_for

from app.auth.routes import login_required
from app.db import get_db, placeholder
from app.onboarding import onboarding_bp


@onboarding_bp.route("/city", methods=["GET", "POST"])
@login_required
def select_city():
    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    if request.method == "POST":
        city_id = request.form.get("city_id")

        cur.execute(f"SELECT * FROM cities WHERE id = {ph}", (city_id,))
        city = cur.fetchone()
        if city is None:
            flash("Please choose a valid city.")
            return redirect(url_for("onboarding.select_city"))

        # Check whether this city already has zones defined
        cur.execute(f"SELECT id, name FROM zones WHERE city_id = {ph} ORDER BY name", (city_id,))
        zones = cur.fetchall()

        if not zones:
            # No sub-zones yet for this city (e.g. it hasn't been broken up,
            # or it's meant to be single-zone) — auto-create one "Citywide"
            # zone so the user always has something to be assigned to.
            cur.execute(
                f"INSERT INTO zones (city_id, name) VALUES ({ph}, {ph})",
                (city_id, "Citywide"),
            )
            db.commit()
            cur.execute(
                f"SELECT id FROM zones WHERE city_id = {ph} AND name = {ph}",
                (city_id, "Citywide"),
            )
            zone = cur.fetchone()
            _assign_zone(db, cur, ph, zone["id"])
            flash(f"You're all set in {city['name']}!")
            return redirect(url_for("home"))

        # City has real zones — remember the chosen city and go pick a zone
        session["onboarding_city_id"] = city_id
        return redirect(url_for("onboarding.select_zone"))

    cur.execute("SELECT id, name, state FROM cities ORDER BY state IS NULL, state, name")
    cities = cur.fetchall()
    return render_template("onboarding/select_city.html", cities=cities)


@onboarding_bp.route("/zone", methods=["GET", "POST"])
@login_required
def select_zone():
    city_id = session.get("onboarding_city_id")
    if not city_id:
        return redirect(url_for("onboarding.select_city"))

    db = get_db()
    ph = placeholder()
    cur = db.cursor()

    cur.execute(f"SELECT * FROM cities WHERE id = {ph}", (city_id,))
    city = cur.fetchone()

    if request.method == "POST":
        zone_id = request.form.get("zone_id")

        cur.execute(f"SELECT id FROM zones WHERE id = {ph} AND city_id = {ph}", (zone_id, city_id))
        zone = cur.fetchone()
        if zone is None:
            flash("Please choose a valid zone.")
            return redirect(url_for("onboarding.select_zone"))

        _assign_zone(db, cur, ph, zone_id)
        session.pop("onboarding_city_id", None)
        flash(f"You're all set in {city['name']}!")
        return redirect(url_for("home"))

    cur.execute(f"SELECT id, name FROM zones WHERE city_id = {ph} ORDER BY name", (city_id,))
    zones = cur.fetchall()
    return render_template("onboarding/select_zone.html", city=city, zones=zones)


def _assign_zone(db, cur, ph, zone_id):
    """Set both home_zone_id and current_zone_id for the logged-in user."""
    cur.execute(
        f"UPDATE users SET home_zone_id = {ph}, current_zone_id = {ph} WHERE id = {ph}",
        (zone_id, zone_id, session["user_id"]),
    )
    db.commit()
