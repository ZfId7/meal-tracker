# File path: /app/daily_log/__init__.py

from flask import Blueprint

daily_log_bp = Blueprint("daily_log_bp", __name__)

from app.daily_log import routes
