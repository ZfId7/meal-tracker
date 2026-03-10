# File path: app/saved_meals/routes.py

from flask import flash, redirect, render_template, request, url_for

from app.constants import FOOD_UNITS
from app.extensions import db
from app.models import Food, SavedMeal, SavedMealItem
from app.saved_meals import saved_meals_bp
from app.nutrition  import calculate_entry_from_food


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


@saved_meals_bp.route("/")
def index():
    saved_meals = (
        SavedMeal.query
        .order_by(SavedMeal.name.asc())
        .all()
    )

    meal_totals = {}

    for meal in saved_meals:
        totals = {
            "calories": 0.0,
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fat_g": 0.0,
        }

        for item in meal.items:
            try:
                nutrition = calculate_entry_from_food(item.food, item.amount, item.unit)
            except ValueError:
                continue

            totals["calories"] += nutrition["calories"]
            totals["protein_g"] += nutrition["protein_g"]
            totals["carbs_g"] += nutrition["carbs_g"]
            totals["fat_g"] += nutrition["fat_g"]

        meal_totals[meal.id] = {
            "calories": round(totals["calories"], 2),
            "protein_g": round(totals["protein_g"], 2),
            "carbs_g": round(totals["carbs_g"], 2),
            "fat_g": round(totals["fat_g"], 2),
        }

    return render_template(
        "saved_meals/index.html",
        saved_meals=saved_meals,
        meal_totals=meal_totals,
    )


@saved_meals_bp.route("/create", methods=["GET", "POST"])
def create():
    foods = Food.query.filter_by(is_active=True).order_by(Food.name.asc()).all()

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        notes = (request.form.get("notes") or "").strip() or None

        food_ids = request.form.getlist("food_id")
        amounts = request.form.getlist("amount")
        units = request.form.getlist("unit")

        errors = []

        if not name:
            errors.append("Saved meal name is required.")

        item_rows = []

        for index, food_id_raw in enumerate(food_ids):
            food_id_raw = (food_id_raw or "").strip()
            amount_raw = (amounts[index] if index < len(amounts) else "").strip()
            unit_raw = (units[index] if index < len(units) else "").strip()

            if not food_id_raw and not amount_raw and not unit_raw:
                continue

            if not food_id_raw:
                errors.append(f"Row {index + 1}: Food is required.")
                continue

            try:
                food_id = int(food_id_raw)
            except ValueError:
                errors.append(f"Row {index + 1}: Invalid food selection.")
                continue

            food = Food.query.get(food_id)
            if food is None:
                errors.append(f"Row {index + 1}: Selected food was not found.")
                continue

            amount = _safe_float(amount_raw, f"Row {index + 1} amount", errors)

            if not unit_raw:
                errors.append(f"Row {index + 1}: Unit is required.")

            if amount is None or not unit_raw:
                continue

            item_rows.append({
                "food": food,
                "amount": amount,
                "unit": unit_raw,
            })

        if not item_rows:
            errors.append("Add at least one food item to the saved meal.")

        if errors:
            for error in errors:
                flash(error, "error")
            row_count = max(len(food_ids), 3)

            return render_template(
                "saved_meals/create.html",
                foods=foods,
                food_units=FOOD_UNITS,
                form_data=request.form,
                row_count=row_count,
                selected_food_ids=food_ids + ([""] * (row_count - len(food_ids))),
                selected_amounts=amounts + ([""] * (row_count - len(amounts))),
                selected_units=units + ([""] * (row_count - len(units))),
            )

        saved_meal = SavedMeal(
            name=name,
            notes=notes,
        )
        db.session.add(saved_meal)
        db.session.flush()

        for row in item_rows:
            db.session.add(
                SavedMealItem(
                    saved_meal_id=saved_meal.id,
                    food_id=row["food"].id,
                    amount=row["amount"],
                    unit=row["unit"],
                )
            )

        db.session.commit()

        flash("Saved meal created successfully.", "success")
        return redirect(url_for("saved_meals_bp.index"))

    return render_template(
        "saved_meals/create.html",
        foods=foods,
        food_units=FOOD_UNITS,
        form_data={},
        row_count=3,
        selected_food_ids=["", "", ""],
        selected_amounts=["", "", ""],
        selected_units=["", "", ""],
    )

@saved_meals_bp.route("/<int:saved_meal_id>/edit", methods=["GET", "POST"])
def edit(saved_meal_id):
    saved_meal = SavedMeal.query.get_or_404(saved_meal_id)
    foods = Food.query.filter_by(is_active=True).order_by(Food.name.asc()).all()

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        notes = (request.form.get("notes") or "").strip() or None

        food_ids = request.form.getlist("food_id")
        amounts = request.form.getlist("amount")
        units = request.form.getlist("unit")

        errors = []

        if not name:
            errors.append("Saved meal name is required.")

        item_rows = []

        for index, food_id_raw in enumerate(food_ids):
            food_id_raw = (food_id_raw or "").strip()
            amount_raw = (amounts[index] if index < len(amounts) else "").strip()
            unit_raw = (units[index] if index < len(units) else "").strip()

            if not food_id_raw and not amount_raw and not unit_raw:
                continue

            if not food_id_raw:
                errors.append(f"Row {index + 1}: Food is required.")
                continue

            try:
                food_id = int(food_id_raw)
            except ValueError:
                errors.append(f"Row {index + 1}: Invalid food selection.")
                continue

            food = Food.query.get(food_id)
            if food is None:
                errors.append(f"Row {index + 1}: Selected food was not found.")
                continue

            amount = _safe_float(amount_raw, f"Row {index + 1} amount", errors)

            if not unit_raw:
                errors.append(f"Row {index + 1}: Unit is required.")

            if amount is None or not unit_raw:
                continue

            item_rows.append({
                "food": food,
                "amount": amount,
                "unit": unit_raw,
            })

        if not item_rows:
            errors.append("Add at least one food item to the saved meal.")

        if errors:
            for error in errors:
                flash(error, "error")

            row_count = max(len(food_ids), 3)

            return render_template(
                "saved_meals/edit.html",
                saved_meal=saved_meal,
                foods=foods,
                food_units=FOOD_UNITS,
                form_data=request.form,
                row_count=row_count,
                selected_food_ids=food_ids + ([""] * (row_count - len(food_ids))),
                selected_amounts=amounts + ([""] * (row_count - len(amounts))),
                selected_units=units + ([""] * (row_count - len(units))),
            )

        saved_meal.name = name
        saved_meal.notes = notes

        SavedMealItem.query.filter_by(saved_meal_id=saved_meal.id).delete()

        for row in item_rows:
            db.session.add(
                SavedMealItem(
                    saved_meal_id=saved_meal.id,
                    food_id=row["food"].id,
                    amount=row["amount"],
                    unit=row["unit"],
                )
            )

        db.session.commit()

        flash("Saved meal updated successfully.", "success")
        return redirect(url_for("saved_meals_bp.index"))

    existing_items = list(saved_meal.items)
    row_count = max(len(existing_items), 3)

    selected_food_ids = []
    selected_amounts = []
    selected_units = []

    for item in existing_items:
        selected_food_ids.append(str(item.food_id))
        selected_amounts.append(str(item.amount))
        selected_units.append(item.unit or "")

    while len(selected_food_ids) < row_count:
        selected_food_ids.append("")
        selected_amounts.append("")
        selected_units.append("")

    form_data = {
        "name": saved_meal.name or "",
        "notes": saved_meal.notes or "",
    }

    return render_template(
        "saved_meals/edit.html",
        saved_meal=saved_meal,
        foods=foods,
        food_units=FOOD_UNITS,
        form_data=form_data,
        row_count=row_count,
        selected_food_ids=selected_food_ids,
        selected_amounts=selected_amounts,
        selected_units=selected_units,
    )


@saved_meals_bp.route("/<int:saved_meal_id>/delete", methods=["POST"])
def delete(saved_meal_id):
    saved_meal = SavedMeal.query.get_or_404(saved_meal_id)

    db.session.delete(saved_meal)
    db.session.commit()

    flash("Saved meal deleted successfully.", "success")
    return redirect(url_for("saved_meals_bp.index"))
