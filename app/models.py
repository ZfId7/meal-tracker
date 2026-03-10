# File path: app/models.py

from datetime import datetime, date

from app.extensions import db


class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)

    calorie_target = db.Column(db.Float, nullable=True)
    protein_target_g = db.Column(db.Float, nullable=True)
    carb_target_g = db.Column(db.Float, nullable=True)
    fat_target_g = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Food(db.Model):
    __tablename__ = "foods"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    brand = db.Column(db.String(120), nullable=True)
    category = db.Column(db.String(80), nullable=True)

    reference_amount = db.Column(db.Float, nullable=False, default=1.0)
    reference_unit = db.Column(db.String(20), nullable=False)

    equivalent_grams = db.Column(db.Float, nullable=True)
    equivalent_ml = db.Column(db.Float, nullable=True)

    calories = db.Column(db.Float, nullable=False, default=0.0)
    protein_g = db.Column(db.Float, nullable=False, default=0.0)
    carbs_g = db.Column(db.Float, nullable=False, default=0.0)
    fat_g = db.Column(db.Float, nullable=False, default=0.0)

    fiber_g = db.Column(db.Float, nullable=True)
    sugar_g = db.Column(db.Float, nullable=True)
    sodium_mg = db.Column(db.Float, nullable=True)
    saturated_fat_g = db.Column(db.Float, nullable=True)
    cholesterol_mg = db.Column(db.Float, nullable=True)

    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    saved_meal_items = db.relationship(
        "SavedMealItem",
        back_populates="food",
        cascade="all, delete-orphan",
    )


class SavedMeal(db.Model):
    __tablename__ = "saved_meals"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    items = db.relationship(
        "SavedMealItem",
        back_populates="saved_meal",
        cascade="all, delete-orphan",
    )


class SavedMealItem(db.Model):
    __tablename__ = "saved_meal_items"

    id = db.Column(db.Integer, primary_key=True)

    saved_meal_id = db.Column(
        db.Integer,
        db.ForeignKey("saved_meals.id"),
        nullable=False,
    )
    food_id = db.Column(
        db.Integer,
        db.ForeignKey("foods.id"),
        nullable=False,
    )

    amount = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    saved_meal = db.relationship("SavedMeal", back_populates="items")
    food = db.relationship("Food", back_populates="saved_meal_items")


class LogEntry(db.Model):
    __tablename__ = "log_entries"

    id = db.Column(db.Integer, primary_key=True)

    entry_date = db.Column(db.Date, nullable=False, default=date.today)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    entry_kind = db.Column(db.String(20), nullable=False)  # food, saved_meal

    source_food_id = db.Column(db.Integer, db.ForeignKey("foods.id"), nullable=True)
    source_saved_meal_id = db.Column(db.Integer, db.ForeignKey("saved_meals.id"), nullable=True)

    display_name = db.Column(db.String(160), nullable=False)

    amount = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), nullable=False)

    calories = db.Column(db.Float, nullable=False, default=0.0)
    protein_g = db.Column(db.Float, nullable=False, default=0.0)
    carbs_g = db.Column(db.Float, nullable=False, default=0.0)
    fat_g = db.Column(db.Float, nullable=False, default=0.0)

    fiber_g = db.Column(db.Float, nullable=True)
    sugar_g = db.Column(db.Float, nullable=True)
    sodium_mg = db.Column(db.Float, nullable=True)
    saturated_fat_g = db.Column(db.Float, nullable=True)
    cholesterol_mg = db.Column(db.Float, nullable=True)

    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    source_food = db.relationship("Food", foreign_keys=[source_food_id])
    source_saved_meal = db.relationship("SavedMeal", foreign_keys=[source_saved_meal_id])
