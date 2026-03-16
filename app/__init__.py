# File path: app/__init__.py

from flask import Flask
from pathlib import Path

from config import Config
from app.extensions import db, migrate


def create_app():
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="templates",
        static_folder="static",
    )

    app.config.from_object(Config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.main import main_bp
    from app.food_library import food_library_bp
    from app.saved_meals import saved_meals_bp
    from app.daily_log import daily_log_bp
    from app.history import history_bp
    from app.settings import settings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(food_library_bp, url_prefix="/foods")
    app.register_blueprint(saved_meals_bp, url_prefix="/saved-meals")
    app.register_blueprint(daily_log_bp, url_prefix="/daily-log")
    app.register_blueprint(history_bp, url_prefix="/history")
    app.register_blueprint(settings_bp, url_prefix="/settings")

    with app.app_context():
        from app import models
        db.create_all()

    return app
