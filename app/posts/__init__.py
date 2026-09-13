from flask import Blueprint

posts_bp = Blueprint("posts", __name__, template_folder="../templates/posts")

from app.posts import routes  # noqa: E402,F401
