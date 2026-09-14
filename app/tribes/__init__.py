from flask import Blueprint

tribes_bp = Blueprint("tribes", __name__, template_folder="../templates/tribes")

from app.tribes import routes  # noqa: E402,F401