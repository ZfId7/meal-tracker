# File path: /app/main/routes.py

from datetime import date

from flask import render_template

from app.main import main_bp
from app.models import LogEntry, Settings


@main_bp.route("/")
def dashboard():
    today = date.today()

    settings_row = Settings.query.first()

    entries = (
        LogEntry.query
        .filter_by(entry_date=today)
        .order_by(LogEntry.meal_type.asc(), LogEntry.created_at.asc())
        .all()
    )

    totals = {
        "calories": round(sum(entry.calories or 0 for entry in entries), 2),
        "protein_g": round(sum(entry.protein_g or 0 for entry in entries), 2),
        "carbs_g": round(sum(entry.carbs_g or 0 for entry in entries), 2),
        "fat_g": round(sum(entry.fat_g or 0 for entry in entries), 2),
    }

    targets = {
        "calories": settings_row.calorie_target if settings_row else None,
        "protein_g": settings_row.protein_target_g if settings_row else None,
        "carbs_g": settings_row.carb_target_g if settings_row else None,
        "fat_g": settings_row.fat_target_g if settings_row else None,
    }

    remaining = {
        "calories": round(targets["calories"] - totals["calories"], 2) if targets["calories"] is not None else None,
        "protein_g": round(targets["protein_g"] - totals["protein_g"], 2) if targets["protein_g"] is not None else None,
        "carbs_g": round(targets["carbs_g"] - totals["carbs_g"], 2) if targets["carbs_g"] is not None else None,
        "fat_g": round(targets["fat_g"] - totals["fat_g"], 2) if targets["fat_g"] is not None else None,
    }

    meal_summary = {
        "breakfast": {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "count": 0},
        "lunch": {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "count": 0},
        "dinner": {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "count": 0},
        "snack": {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "count": 0},
    }

    for entry in entries:
        if entry.meal_type not in meal_summary:
            continue

        meal_summary[entry.meal_type]["calories"] += entry.calories or 0
        meal_summary[entry.meal_type]["protein_g"] += entry.protein_g or 0
        meal_summary[entry.meal_type]["carbs_g"] += entry.carbs_g or 0
        meal_summary[entry.meal_type]["fat_g"] += entry.fat_g or 0
        meal_summary[entry.meal_type]["count"] += 1

    for meal_key in meal_summary:
        meal_summary[meal_key]["calories"] = round(meal_summary[meal_key]["calories"], 2)
        meal_summary[meal_key]["protein_g"] = round(meal_summary[meal_key]["protein_g"], 2)
        meal_summary[meal_key]["carbs_g"] = round(meal_summary[meal_key]["carbs_g"], 2)
        meal_summary[meal_key]["fat_g"] = round(meal_summary[meal_key]["fat_g"], 2)

    return render_template(
        "dashboard.html",
        today=today,
        totals=totals,
        targets=targets,
        remaining=remaining,
        meal_summary=meal_summary,
    )
