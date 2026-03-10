# File path: /config.py

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-later")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{INSTANCE_DIR / 'meal_tracker.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
