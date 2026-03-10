# File path: /app/history/routes.py

import calendar
from datetime import date, datetime

from flask import render_template, request

from app.constants import MEAL_TYPES
from app.history import history_bp
from app.models import LogEntry


@history_bp.route("/")
def index():
    today = date.today()

    year_raw = request.args.get("year", "").strip()
    month_raw = request.args.get("month", "").strip()
    selected_date_raw = request.args.get("selected_date", "").strip()

    try:
        selected_year = int(year_raw) if year_raw else today.year
    except ValueError:
        selected_year = today.year

    try:
        selected_month = int(month_raw) if month_raw else today.month
    except ValueError:
        selected_month = today.month

    if selected_month < 1 or selected_month > 12:
        selected_month = today.month

    month_start = date(selected_year, selected_month, 1)
    last_day = calendar.monthrange(selected_year, selected_month)[1]
    month_end = date(selected_year, selected_month, last_day)

    month_entries = (
        LogEntry.query
        .filter(LogEntry.entry_date >= month_start, LogEntry.entry_date <= month_end)
        .order_by(LogEntry.entry_date.asc(), LogEntry.created_at.asc())
        .all()
    )

    daily_totals = {}
    for entry in month_entries:
        entry_day = entry.entry_date
        if entry_day not in daily_totals:
            daily_totals[entry_day] = {
                "calories": 0,
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 0,
                "count": 0,
            }

        daily_totals[entry_day]["calories"] += entry.calories or 0
        daily_totals[entry_day]["protein_g"] += entry.protein_g or 0
        daily_totals[entry_day]["carbs_g"] += entry.carbs_g or 0
        daily_totals[entry_day]["fat_g"] += entry.fat_g or 0
        daily_totals[entry_day]["count"] += 1

    for day_totals in daily_totals.values():
        day_totals["calories"] = round(day_totals["calories"], 2)
        day_totals["protein_g"] = round(day_totals["protein_g"], 2)
        day_totals["carbs_g"] = round(day_totals["carbs_g"], 2)
        day_totals["fat_g"] = round(day_totals["fat_g"], 2)

    cal = calendar.Calendar(firstweekday=6)  # Sunday
    weeks = []

    for week in cal.monthdatescalendar(selected_year, selected_month):
        week_cells = []
        for day_obj in week:
            week_cells.append({
                "date": day_obj,
                "day_number": day_obj.day,
                "is_current_month": day_obj.month == selected_month,
                "is_today": day_obj == today,
                "totals": daily_totals.get(day_obj),
            })
        weeks.append(week_cells)

    if selected_date_raw:
        try:
            selected_date = datetime.strptime(selected_date_raw, "%Y-%m-%d").date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today if today.month == selected_month and today.year == selected_year else month_start

    selected_entries = (
        LogEntry.query
        .filter_by(entry_date=selected_date)
        .order_by(LogEntry.meal_type.asc(), LogEntry.created_at.asc())
        .all()
    )

    grouped_entries = {meal_key: [] for meal_key, _ in MEAL_TYPES}
    for entry in selected_entries:
        grouped_entries.setdefault(entry.meal_type, []).append(entry)

    selected_totals = {
        "calories": round(sum(entry.calories or 0 for entry in selected_entries), 2),
        "protein_g": round(sum(entry.protein_g or 0 for entry in selected_entries), 2),
        "carbs_g": round(sum(entry.carbs_g or 0 for entry in selected_entries), 2),
        "fat_g": round(sum(entry.fat_g or 0 for entry in selected_entries), 2),
    }

    prev_month = selected_month - 1
    prev_year = selected_year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1

    next_month = selected_month + 1
    next_year = selected_year
    if next_month > 12:
        next_month = 1
        next_year += 1

    month_label = month_start.strftime("%B %Y")

    return render_template(
        "history/index.html",
        today=today,
        selected_year=selected_year,
        selected_month=selected_month,
        selected_date=selected_date,
        month_label=month_label,
        weeks=weeks,
        meal_types=MEAL_TYPES,
        grouped_entries=grouped_entries,
        selected_totals=selected_totals,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
    )
