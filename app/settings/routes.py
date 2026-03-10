# File path: /app/settings/routes.py

from flask import flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Settings
from app.settings import settings_bp


def _parse_optional_float(value, field_label, errors):
    raw = (value or "").strip()
    if not raw:
        return None

    try:
        return float(raw)
    except ValueError:
        errors.append(f"{field_label} must be a valid number.")
        return None


@settings_bp.route("/", methods=["GET", "POST"])
def index():
    settings_row = Settings.query.first()

    if settings_row is None:
        settings_row = Settings()
        db.session.add(settings_row)
        db.session.commit()

    if request.method == "POST":
        errors = []

        calorie_target = _parse_optional_float(
            request.form.get("calorie_target"),
            "Calorie target",
            errors,
        )
        protein_target_g = _parse_optional_float(
            request.form.get("protein_target_g"),
            "Protein target",
            errors,
        )
        carb_target_g = _parse_optional_float(
            request.form.get("carb_target_g"),
            "Carb target",
            errors,
        )
        fat_target_g = _parse_optional_float(
            request.form.get("fat_target_g"),
            "Fat target",
            errors,
        )

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            settings_row.calorie_target = calorie_target
            settings_row.protein_target_g = protein_target_g
            settings_row.carb_target_g = carb_target_g
            settings_row.fat_target_g = fat_target_g

            db.session.commit()
            flash("Settings saved successfully.", "success")
            return redirect(url_for("settings_bp.index"))

    return render_template("settings/index.html", settings_row=settings_row)
