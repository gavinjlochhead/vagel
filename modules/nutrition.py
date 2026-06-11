import csv
import os
from datetime import date, datetime

import requests

NUTRITION_CSV = "data/nutrition_log.csv"

NUTRITION_COLUMNS = [
    "date", "time", "food_name", "brand", "portion_g",
    "calories", "protein_g", "carbs_g", "fat_g", "fibre_g", "meal_period"
]


def search_food(query: str) -> list:
    """
    Calls Open Food Facts API.
    Returns list of up to 10 dicts:
      {name, brand, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, fibre_per_100g}
    Returns [] on any error or timeout (5s).
    """
    url = (
        "https://world.openfoodfacts.org/cgi/search.pl"
        f"?search_terms={requests.utils.quote(query)}"
        "&json=1&page_size=10"
        "&fields=product_name,brands,nutriments"
    )
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("products", [])
        results = []
        for p in products:
            nutriments = p.get("nutriments", {})
            results.append({
                "name": p.get("product_name", ""),
                "brand": p.get("brands", ""),
                "calories_per_100g": nutriments.get("energy-kcal_100g", 0) or 0,
                "protein_per_100g": nutriments.get("proteins_100g", 0) or 0,
                "carbs_per_100g": nutriments.get("carbohydrates_100g", 0) or 0,
                "fat_per_100g": nutriments.get("fat_100g", 0) or 0,
                "fibre_per_100g": nutriments.get("fiber_100g", 0) or 0,
            })
        return results
    except Exception:
        return []


def log_food(food_name: str, brand: str, calories: float, protein_g: float,
             carbs_g: float, fat_g: float, fibre_g: float,
             portion_g: float, meal_period: str):
    """
    Appends a row to data/nutrition_log.csv.
    Creates file with header if missing.
    date = today, time = now.
    """
    now = datetime.now()
    row = {
        "date": date.today().isoformat(),
        "time": now.strftime("%H:%M"),
        "food_name": food_name,
        "brand": brand,
        "portion_g": portion_g,
        "calories": calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "fibre_g": fibre_g,
        "meal_period": meal_period,
    }
    file_exists = os.path.isfile(NUTRITION_CSV)
    with open(NUTRITION_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=NUTRITION_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def get_today_summary() -> dict:
    """
    Reads today's rows from nutrition_log.csv.
    Returns summary dict with traffic_light logic.
    """
    empty = {
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0,
        "fibre_g": 0.0,
        "calories": 0.0,
        "meals_logged": [],
        "traffic_light": "red",
        "item_count": 0,
    }

    today = date.today().isoformat()

    if not os.path.isfile(NUTRITION_CSV):
        return empty

    protein = 0.0
    carbs = 0.0
    fat = 0.0
    fibre = 0.0
    calories = 0.0
    meals = []
    count = 0

    try:
        with open(NUTRITION_CSV, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("date") != today:
                    continue
                count += 1
                protein += float(row.get("protein_g") or 0)
                carbs += float(row.get("carbs_g") or 0)
                fat += float(row.get("fat_g") or 0)
                fibre += float(row.get("fibre_g") or 0)
                calories += float(row.get("calories") or 0)
                mp = row.get("meal_period", "")
                if mp and mp not in meals:
                    meals.append(mp)
    except Exception:
        return empty

    if count == 0:
        return empty

    # Traffic light logic
    if protein >= 50 and fibre >= 15 and calories > 0:
        traffic_light = "green"
    elif protein >= 25 or fibre >= 8:
        traffic_light = "yellow"
    else:
        traffic_light = "red"

    return {
        "protein_g": round(protein, 1),
        "carbs_g": round(carbs, 1),
        "fat_g": round(fat, 1),
        "fibre_g": round(fibre, 1),
        "calories": round(calories, 1),
        "meals_logged": meals,
        "traffic_light": traffic_light,
        "item_count": count,
    }
