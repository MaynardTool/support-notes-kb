# file: app/config.py
import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "postgresql://notesuser:notespass@localhost:5432/notesdb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    )
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    ALLOW_SELF_REGISTER = os.environ.get("ALLOW_SELF_REGISTER", "0") == "1"

    MARKDOWN_EXTENSIONS = ["extra", "codehilite", "toc", "tables", "fenced_code"]

    BLEACH_ALLOWED_TAGS = [
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "br",
        "hr",
        "ul",
        "ol",
        "li",
        "blockquote",
        "pre",
        "code",
        "a",
        "img",
        "strong",
        "em",
        "b",
        "i",
        "u",
        "s",
        "del",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
    ]
    BLEACH_ALLOWED_ATTRS = {
        "a": ["href", "title", "target", "rel"],
        "img": ["src", "alt", "title", "width", "height"],
        "td": ["colspan", "rowspan"],
        "th": ["colspan", "rowspan"],
    }


class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_SESSION_ENABLED = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
