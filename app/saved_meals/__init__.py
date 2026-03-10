# File path: app/saved_meals/__init__.py

from flask import Blueprint

saved_meals_bp = Blueprint("saved_meals_bp", __name__)

from app.saved_meals import routes
