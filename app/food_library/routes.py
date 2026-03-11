# File path: /app/food_library/routes.py

from flask import flash, redirect, render_template, request, url_for

from app.constants import FOOD_CATEGORIES, FOOD_UNITS
from app.extensions import db
from app.food_library import food_library_bp
from app.models import Food


def _parse_optional_float(value, field_label, errors):
    raw = (value or "").strip()
    if not raw:
        return None

    try:
        return float(raw)
    except ValueError:
        errors.append(f"{field_label} must be a valid number.")
        return None


def _parse_required_float(value, field_label, errors):
    raw = (value or "").strip()
    if not raw:
        errors.append(f"{field_label} is required.")
        return None

    try:
        return float(raw)
    except ValueError:
        errors.append(f"{field_label} must be a valid number.")
        return None


@food_library_bp.route("/")
def index():
    selected_category = (request.args.get("category") or "").strip()

    query = Food.query

    if selected_category:
        query = query.filter(Food.category == selected_category)

    foods = query.order_by(Food.category.asc(), Food.name.asc()).all()

    grouped_foods = {}
    uncategorized_foods = []

    category_label_map = dict(FOOD_CATEGORIES)

    for food in foods:
        if food.category:
            category_label = category_label_map.get(food.category, food.category.title())
            grouped_foods.setdefault(category_label, []).append(food)
        else:
            uncategorized_foods.append(food)

    ordered_grouped_foods = []
    used_labels = set()

    for value, label in FOOD_CATEGORIES:
        if label in grouped_foods:
            ordered_grouped_foods.append((label, grouped_foods[label]))
            used_labels.add(label)

    for category_label, category_foods in grouped_foods.items():
        if category_label not in used_labels:
            ordered_grouped_foods.append((category_label, category_foods))

    if uncategorized_foods:
        ordered_grouped_foods.append(("Uncategorized", uncategorized_foods))

    return render_template(
        "food_library/index.html",
        grouped_foods=ordered_grouped_foods,
        food_categories=FOOD_CATEGORIES,
        selected_category=selected_category,
    )


@food_library_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        brand = (request.form.get("brand") or "").strip() or None
        category = (request.form.get("category") or "").strip() or None
        reference_unit = (request.form.get("reference_unit") or "").strip()
        notes = (request.form.get("notes") or "").strip() or None

        errors = []

        if not name:
            errors.append("Food name is required.")

        if not reference_unit:
            errors.append("Reference unit is required.")

        reference_amount = _parse_required_float(
            request.form.get("reference_amount"),
            "Reference amount",
            errors,
        )
        calories = _parse_required_float(
            request.form.get("calories"),
            "Calories",
            errors,
        )
        protein_g = _parse_required_float(
            request.form.get("protein_g"),
            "Protein",
            errors,
        )
        carbs_g = _parse_required_float(
            request.form.get("carbs_g"),
            "Carbs",
            errors,
        )
        fat_g = _parse_required_float(
            request.form.get("fat_g"),
            "Fat",
            errors,
        )

        equivalent_grams = _parse_optional_float(
            request.form.get("equivalent_grams"),
            "Equivalent grams",
            errors,
        )
        equivalent_ml = _parse_optional_float(
            request.form.get("equivalent_ml"),
            "Equivalent mL",
            errors,
        )
        fiber_g = _parse_optional_float(
            request.form.get("fiber_g"),
            "Fiber",
            errors,
        )
        sugar_g = _parse_optional_float(
            request.form.get("sugar_g"),
            "Sugar",
            errors,
        )
        sodium_mg = _parse_optional_float(
            request.form.get("sodium_mg"),
            "Sodium",
            errors,
        )
        saturated_fat_g = _parse_optional_float(
            request.form.get("saturated_fat_g"),
            "Saturated fat",
            errors,
        )
        cholesterol_mg = _parse_optional_float(
            request.form.get("cholesterol_mg"),
            "Cholesterol",
            errors,
        )

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "food_library/create.html",
                food_units=FOOD_UNITS,
                food_categories=FOOD_CATEGORIES,
                form_data=request.form,
            )

        food = Food(
            name=name,
            brand=brand,
            category=category,
            reference_amount=reference_amount,
            reference_unit=reference_unit,
            equivalent_grams=equivalent_grams,
            equivalent_ml=equivalent_ml,
            calories=calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            fiber_g=fiber_g,
            sugar_g=sugar_g,
            sodium_mg=sodium_mg,
            saturated_fat_g=saturated_fat_g,
            cholesterol_mg=cholesterol_mg,
            notes=notes,
        )

        db.session.add(food)
        db.session.commit()

        flash("Food created successfully.", "success")
        return redirect(url_for("food_library_bp.index"))

    return render_template(
        "food_library/create.html",
        food_units=FOOD_UNITS,
        food_categories=FOOD_CATEGORIES,
        form_data={},
    )


@food_library_bp.route("/<int:food_id>/edit", methods=["GET", "POST"])
def edit(food_id):
    food = Food.query.get_or_404(food_id)

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        brand = (request.form.get("brand") or "").strip() or None
        category = (request.form.get("category") or "").strip() or None
        reference_unit = (request.form.get("reference_unit") or "").strip()
        notes = (request.form.get("notes") or "").strip() or None

        errors = []

        if not name:
            errors.append("Food name is required.")

        if not reference_unit:
            errors.append("Reference unit is required.")

        reference_amount = _parse_required_float(
            request.form.get("reference_amount"),
            "Reference amount",
            errors,
        )
        calories = _parse_required_float(
            request.form.get("calories"),
            "Calories",
            errors,
        )
        protein_g = _parse_required_float(
            request.form.get("protein_g"),
            "Protein",
            errors,
        )
        carbs_g = _parse_required_float(
            request.form.get("carbs_g"),
            "Carbs",
            errors,
        )
        fat_g = _parse_required_float(
            request.form.get("fat_g"),
            "Fat",
            errors,
        )

        equivalent_grams = _parse_optional_float(
            request.form.get("equivalent_grams"),
            "Equivalent grams",
            errors,
        )
        equivalent_ml = _parse_optional_float(
            request.form.get("equivalent_ml"),
            "Equivalent mL",
            errors,
        )
        fiber_g = _parse_optional_float(
            request.form.get("fiber_g"),
            "Fiber",
            errors,
        )
        sugar_g = _parse_optional_float(
            request.form.get("sugar_g"),
            "Sugar",
            errors,
        )
        sodium_mg = _parse_optional_float(
            request.form.get("sodium_mg"),
            "Sodium",
            errors,
        )
        saturated_fat_g = _parse_optional_float(
            request.form.get("saturated_fat_g"),
            "Saturated fat",
            errors,
        )
        cholesterol_mg = _parse_optional_float(
            request.form.get("cholesterol_mg"),
            "Cholesterol",
            errors,
        )

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "food_library/edit.html",
                food=food,
                food_units=FOOD_UNITS,
                food_categories=FOOD_CATEGORIES,
                form_data=request.form,
            )

        food.name = name
        food.brand = brand
        food.category = category
        food.reference_amount = reference_amount
        food.reference_unit = reference_unit
        food.equivalent_grams = equivalent_grams
        food.equivalent_ml = equivalent_ml
        food.calories = calories
        food.protein_g = protein_g
        food.carbs_g = carbs_g
        food.fat_g = fat_g
        food.fiber_g = fiber_g
        food.sugar_g = sugar_g
        food.sodium_mg = sodium_mg
        food.saturated_fat_g = saturated_fat_g
        food.cholesterol_mg = cholesterol_mg
        food.notes = notes

        db.session.commit()

        flash("Food updated successfully.", "success")
        return redirect(url_for("food_library_bp.index"))

    form_data = {
        "name": food.name or "",
        "brand": food.brand or "",
        "category": food.category or "",
        "reference_amount": food.reference_amount if food.reference_amount is not None else "",
        "reference_unit": food.reference_unit or "",
        "equivalent_grams": food.equivalent_grams if food.equivalent_grams is not None else "",
        "equivalent_ml": food.equivalent_ml if food.equivalent_ml is not None else "",
        "calories": food.calories if food.calories is not None else "",
        "protein_g": food.protein_g if food.protein_g is not None else "",
        "carbs_g": food.carbs_g if food.carbs_g is not None else "",
        "fat_g": food.fat_g if food.fat_g is not None else "",
        "fiber_g": food.fiber_g if food.fiber_g is not None else "",
        "sugar_g": food.sugar_g if food.sugar_g is not None else "",
        "sodium_mg": food.sodium_mg if food.sodium_mg is not None else "",
        "saturated_fat_g": food.saturated_fat_g if food.saturated_fat_g is not None else "",
        "cholesterol_mg": food.cholesterol_mg if food.cholesterol_mg is not None else "",
        "notes": food.notes or "",
    }

    return render_template(
        "food_library/edit.html",
        food=food,
        food_units=FOOD_UNITS,
        food_categories=FOOD_CATEGORIES,
        form_data=form_data,
    )
