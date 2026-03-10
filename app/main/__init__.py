# File path: app/main/__init__.py

from flask import Blueprint

main_bp = Blueprint('main_bp', __name__)

from app.main import routes
