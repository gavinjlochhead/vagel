import csv
import os
from datetime import date
from flask import Blueprint, jsonify

nutrition_status_bp = Blueprint("nutrition_status", __name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "nutrition_log.csv")


@nutrition_status_bp.route("/api/nutrition/logged-today")
def logged_today():
    today = date.today().isoformat()

    if not os.path.exists(DATA_FILE):
        return jsonify({"logged": False, "count": 0})

    count = 0
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("date") == today:
                count += 1

    return jsonify({"logged": count > 0, "count": count})
