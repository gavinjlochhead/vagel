import csv
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CSV_FILE = os.path.join(DATA_DIR, "nervous_system_log.csv")

COLUMNS = [
    "date", "time", "triggered_by", "ns_state",
    "energy", "energy_why", "focus", "focus_why",
    "connection", "connection_why",
    "sleep_hours", "sleep_quality", "wake_time",
    "caffeine_count", "caffeine_timing",
    "steps", "resting_hr", "mins_very_active", "mins_fairly_active",
    "mins_sedentary", "activity_calories", "distance", "floors",
    "protein_g", "carbs_g", "fat_g", "fibre_g",
    "screen_time_total", "screen_time_last_hr",
    "note",
]


def _ensure_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()


def append_row(row: dict):
    """Creates file with header if missing, then appends row. Missing keys write empty string."""
    _ensure_file()
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        normalised = {col: row.get(col, "") for col in COLUMNS}
        writer.writerow(normalised)


def read_recent(n=7) -> list[dict]:
    """Returns last n rows as list of dicts."""
    _ensure_file()
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows[-n:] if len(rows) >= n else rows
