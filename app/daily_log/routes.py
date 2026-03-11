# File path: /app/daily_log/routes.py

from datetime import datetime, date

from flask import flash, redirect, render_template, request, url_for

from app.constants import FOOD_UNITS, MEAL_TYPES
from app.daily_log import daily_log_bp
from app.extensions import db
from app.models import Food, LogEntry, SavedMeal
from app.nutrition import calculate_entry_from_food

def _parse_date(value):
    raw = (value or "").strip()
    if not raw:
        return date.today()
    return datetime.strptime(raw, "%Y-%m-%d").date()


def _safe_float(value, field_label, errors):
    raw = (value or "").strip()
    if not raw:
        errors.append(f"{field_label} is required.")
        return None

    try:
        return float(raw)
    except ValueError:
        errors.append(f"{field_label} must be a valid number.")
        return None



@daily_log_bp.route("/", methods=["GET", "POST"])
def index():
    selected_date = _parse_date(request.values.get("entry_date"))

    if request.method == "POST":
        food_id_raw = request.form.get("food_id")
        meal_type = (request.form.get("meal_type") or "").strip()
        unit = (request.form.get("unit") or "").strip()
        notes = (request.form.get("notes") or "").strip() or None

        errors = []

        if not food_id_raw:
            errors.append("Food is required.")

        if not meal_type:
            errors.append("Meal type is required.")

        if not unit:
            errors.append("Unit is required.")

        amount = _safe_float(request.form.get("amount"), "Amount", errors)

        food = None
        if food_id_raw:
            food = Food.query.get(food_id_raw)
            if food is None:
                errors.append("Selected food was not found.")

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            try:
                nutrition = calculate_entry_from_food(food, amount, unit)
            except ValueError as exc:
                flash(str(exc), "error")
            else:
                entry = LogEntry(
                    entry_date=selected_date,
                    meal_type=meal_type,
                    entry_kind="food",
                    source_food_id=food.id,
                    display_name=food.name,
                    amount=amount,
                    unit=unit,
                    calories=nutrition["calories"],
                    protein_g=nutrition["protein_g"],
                    carbs_g=nutrition["carbs_g"],
                    fat_g=nutrition["fat_g"],
                    fiber_g=nutrition["fiber_g"],
                    sugar_g=nutrition["sugar_g"],
                    sodium_mg=nutrition["sodium_mg"],
                    saturated_fat_g=nutrition["saturated_fat_g"],
                    cholesterol_mg=nutrition["cholesterol_mg"],
                    notes=notes,
                )

                db.session.add(entry)
                db.session.commit()

                flash("Log entry added successfully.", "success")
                return redirect(
                    url_for("daily_log_bp.index", entry_date=selected_date.isoformat())
                )

    foods = Food.query.filter_by(is_active=True).order_by(Food.name.asc()).all()
    saved_meals = SavedMeal.query.filter_by(is_active=True).order_by(SavedMeal.name.asc()).all()

    entries = (
        LogEntry.query
        .filter_by(entry_date=selected_date)
        .order_by(LogEntry.meal_type.asc(), LogEntry.created_at.asc())
        .all()
    )

    grouped_entries = {meal_key: [] for meal_key, _ in MEAL_TYPES}
    for entry in entries:
        grouped_entries.setdefault(entry.meal_type, []).append(entry)

    totals = {
        "calories": round(sum(entry.calories or 0 for entry in entries), 2),
        "protein_g": round(sum(entry.protein_g or 0 for entry in entries), 2),
        "carbs_g": round(sum(entry.carbs_g or 0 for entry in entries), 2),
        "fat_g": round(sum(entry.fat_g or 0 for entry in entries), 2),
    }

    return render_template(
        "daily_log/index.html",
        selected_date=selected_date,
        foods=foods,
        saved_meals=saved_meals,
        meal_types=MEAL_TYPES,
        food_units=FOOD_UNITS,
        grouped_entries=grouped_entries,
        totals=totals,
    )

@daily_log_bp.route("/log-saved-meal", methods=["POST"])
def log_saved_meal():
    selected_date = _parse_date(request.form.get("entry_date"))
    meal_type = (request.form.get("meal_type") or "").strip()
    saved_meal_id_raw = (request.form.get("saved_meal_id") or "").strip()

    errors = []

    if not meal_type:
        errors.append("Meal type is required.")

    if not saved_meal_id_raw:
        errors.append("Saved meal is required.")

    quantity = _safe_float(request.form.get("quantity"), "Quantity", errors)

    if quantity is not None and quantity <= 0:
        errors.append("Quantity must be greater than zero.")

    saved_meal = None
    if saved_meal_id_raw:
        try:
            saved_meal_id = int(saved_meal_id_raw)
            saved_meal = SavedMeal.query.get(saved_meal_id)
            if saved_meal is None:
                errors.append("Selected saved meal was not found.")
        except ValueError:
            errors.append("Invalid saved meal selection.")

    if saved_meal and not saved_meal.items:
        errors.append("Selected saved meal has no items.")

    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("daily_log_bp.index", entry_date=selected_date.isoformat()))

    created_count = 0

    for item in saved_meal.items:
        food = item.food

        try:
            effective_amount = item.amount * quantity
            nutrition = calculate_entry_from_food(food, effective_amount, item.unit)

        except ValueError as exc:
            flash(f"{saved_meal.name}: {exc}", "error")
            return redirect(url_for("daily_log_bp.index", entry_date=selected_date.isoformat()))

        entry = LogEntry(
            entry_date=selected_date,
            meal_type=meal_type,
            entry_kind="food",
            source_food_id=food.id,
            source_saved_meal_id=saved_meal.id,
            display_name=food.name,
            amount=effective_amount,
            unit=item.unit,
            calories=nutrition["calories"],
            protein_g=nutrition["protein_g"],
            carbs_g=nutrition["carbs_g"],
            fat_g=nutrition["fat_g"],
            fiber_g=nutrition["fiber_g"],
            sugar_g=nutrition["sugar_g"],
            sodium_mg=nutrition["sodium_mg"],
            saturated_fat_g=nutrition["saturated_fat_g"],
            cholesterol_mg=nutrition["cholesterol_mg"],
            notes=f"From saved meal: {saved_meal.name} x{quantity}",
        )

        db.session.add(entry)
        created_count += 1

    db.session.commit()

    flash(f"Saved meal logged successfully ({created_count} items).", "success")
    return redirect(url_for("daily_log_bp.index", entry_date=selected_date.isoformat()))

@daily_log_bp.route("/<int:entry_id>/edit", methods=["GET", "POST"])
def edit_entry(entry_id):
    entry = LogEntry.query.get_or_404(entry_id)

    foods = Food.query.filter_by(is_active=True).order_by(Food.name.asc()).all()

    if request.method == "POST":
        selected_date = _parse_date(request.form.get("entry_date"))
        food_id_raw = request.form.get("food_id")
        meal_type = (request.form.get("meal_type") or "").strip()
        unit = (request.form.get("unit") or "").strip()
        notes = (request.form.get("notes") or "").strip() or None

        errors = []

        if not food_id_raw:
            errors.append("Food is required.")

        if not meal_type:
            errors.append("Meal type is required.")

        if not unit:
            errors.append("Unit is required.")

        amount = _safe_float(request.form.get("amount"), "Amount", errors)

        food = None
        if food_id_raw:
            food = Food.query.get(food_id_raw)
            if food is None:
                errors.append("Selected food was not found.")

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            try:
                nutrition = calculate_entry_from_food(food, amount, unit)
            except ValueError as exc:
                flash(str(exc), "error")
            else:
                entry.entry_date = selected_date
                entry.meal_type = meal_type
                entry.entry_kind = "food"
                entry.source_food_id = food.id
                entry.source_saved_meal_id = None
                entry.display_name = food.name
                entry.amount = amount
                entry.unit = unit
                entry.calories = nutrition["calories"]
                entry.protein_g = nutrition["protein_g"]
                entry.carbs_g = nutrition["carbs_g"]
                entry.fat_g = nutrition["fat_g"]
                entry.fiber_g = nutrition["fiber_g"]
                entry.sugar_g = nutrition["sugar_g"]
                entry.sodium_mg = nutrition["sodium_mg"]
                entry.saturated_fat_g = nutrition["saturated_fat_g"]
                entry.cholesterol_mg = nutrition["cholesterol_mg"]
                entry.notes = notes

                db.session.commit()

                flash("Log entry updated successfully.", "success")
                return redirect(
                    url_for("daily_log_bp.index", entry_date=selected_date.isoformat())
                )

    form_data = {
        "entry_date": entry.entry_date.isoformat() if entry.entry_date else "",
        "meal_type": entry.meal_type or "",
        "food_id": str(entry.source_food_id) if entry.source_food_id else "",
        "amount": entry.amount if entry.amount is not None else "",
        "unit": entry.unit or "",
        "notes": entry.notes or "",
    }

    return render_template(
        "daily_log/edit.html",
        entry=entry,
        foods=foods,
        meal_types=MEAL_TYPES,
        food_units=FOOD_UNITS,
        form_data=form_data,
    )

@daily_log_bp.route("/<int:entry_id>/delete", methods=["POST"])
def delete_entry(entry_id):
    entry = LogEntry.query.get_or_404(entry_id)
    entry_date = entry.entry_date

    db.session.delete(entry)
    db.session.commit()

    flash("Log entry deleted successfully.", "success")
    return redirect(url_for("daily_log_bp.index", entry_date=entry_date.isoformat()))
