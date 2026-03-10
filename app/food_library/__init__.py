# File path: /app/food_library/__init__.py

from flask import Blueprint

food_library_bp = Blueprint('food_library_bp', __name__)

from app.food_library import routes
