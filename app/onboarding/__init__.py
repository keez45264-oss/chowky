from flask import Blueprint

onboarding_bp = Blueprint("onboarding", __name__, template_folder="../templates/onboarding")

from app.onboarding import routes  # noqa: E402,F401
