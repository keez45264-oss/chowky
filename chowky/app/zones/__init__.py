from flask import Blueprint

zones_bp = Blueprint("zones", __name__, template_folder="../templates/zones")

from app.zones import routes  # noqa: E402,F401
