import os


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    DATABASE_URL = os.environ.get("DATABASE_URL", "")  # empty -> use SQLite locally
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    REPORT_HIDE_THRESHOLD = 3  # auto-hide a post after this many reports


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
