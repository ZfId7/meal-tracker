# File path: app/nutrition.py

def calculate_entry_from_food(food, amount, unit):
    source_amount = food.reference_amount
    source_unit = food.reference_unit

    if source_amount in (None, 0):
        raise ValueError("Food reference amount is missing or zero.")

    multiplier = None

    if unit == source_unit:
        multiplier = amount / source_amount

    elif unit == "g" and food.equivalent_grams:
        multiplier = amount / food.equivalent_grams

    elif unit == "ml" and food.equivalent_ml:
        multiplier = amount / food.equivalent_ml

    elif unit == "oz":
        if source_unit == "lb":
            multiplier = amount / (source_amount * 16.0)
        elif food.equivalent_grams:
            multiplier = (amount * 28.349523125) / food.equivalent_grams

    elif unit == "lb":
        if source_unit == "oz":
            multiplier = (amount * 16.0) / source_amount
        elif food.equivalent_grams:
            multiplier = (amount * 453.59237) / food.equivalent_grams

    elif unit == "fl_oz":
        if source_unit == "cup":
            multiplier = amount / (source_amount * 8.0)
        elif food.equivalent_ml:
            multiplier = (amount * 29.5735295625) / food.equivalent_ml

    elif unit == "cup":
        if source_unit == "fl_oz":
            multiplier = (amount * 8.0) / source_amount
        elif food.equivalent_ml:
            multiplier = (amount * 236.5882365) / food.equivalent_ml

    elif unit == "tbsp":
        if source_unit == "tsp":
            multiplier = (amount * 3.0) / source_amount
        elif food.equivalent_ml:
            multiplier = (amount * 14.78676478125) / food.equivalent_ml

    elif unit == "tsp":
        if source_unit == "tbsp":
            multiplier = amount / (source_amount * 3.0)
        elif food.equivalent_ml:
            multiplier = (amount * 4.92892159375) / food.equivalent_ml

    if multiplier is None:
        raise ValueError(
            f"Cannot convert from '{unit}' to this food's reference unit '{source_unit}'. "
            "Add an equivalent grams/mL value or use the reference unit."
        )

    return {
        "calories": round((food.calories or 0) * multiplier, 2),
        "protein_g": round((food.protein_g or 0) * multiplier, 2),
        "carbs_g": round((food.carbs_g or 0) * multiplier, 2),
        "fat_g": round((food.fat_g or 0) * multiplier, 2),
        "fiber_g": round((food.fiber_g or 0) * multiplier, 2) if food.fiber_g is not None else None,
        "sugar_g": round((food.sugar_g or 0) * multiplier, 2) if food.sugar_g is not None else None,
        "sodium_mg": round((food.sodium_mg or 0) * multiplier, 2) if food.sodium_mg is not None else None,
        "saturated_fat_g": round((food.saturated_fat_g or 0) * multiplier, 2) if food.saturated_fat_g is not None else None,
        "cholesterol_mg": round((food.cholesterol_mg or 0) * multiplier, 2) if food.cholesterol_mg is not None else None,
    }
