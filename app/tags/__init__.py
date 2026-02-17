# file: app/tags/__init__.py
from flask import Blueprint

tags = Blueprint("tags", __name__)

from app.tags import routes
