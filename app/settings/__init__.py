# File path: /app/settings/__init__.py

from flask import Blueprint

settings_bp = Blueprint("settings_bp", __name__)

from app.settings import routes
