# File path: /app/history/__init__.py

from flask import Blueprint

history_bp = Blueprint("history_bp", __name__)

from app.history import routes
