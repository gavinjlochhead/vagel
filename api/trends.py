import csv
import os
from datetime import date, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CSV_FILE = os.path.join(DATA_DIR, "nervous_system_log.csv")


def _parse_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _ns_state_numeric(state: str):
    if not state:
        return None
    if state == "Green - Calm & Engaged":
        return 3
    if state.startswith("Yellow"):
        return 2
    if state.startswith("Red"):
        return 1
    return None


def _read_rows(days: int) -> list[dict]:
    if not os.path.exists(CSV_FILE):
        return []
    cutoff = (date.today() - timedelta(days=days - 1)).isoformat()
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r.get("date", "") >= cutoff]
    return rows


def get_trend_data(days: int = 30) -> dict:
    """
    Reads nervous_system_log.csv, filters to last `days` days.
    Returns a dict with time-series lists aligned by row.
    """
    rows = _read_rows(days)

    dates = []
    times = []
    ns_state_numeric = []
    energy = []
    focus = []
    connection = []
    steps = []
    resting_hr = []
    mins_sedentary = []

    for r in rows:
        dates.append(r.get("date", ""))
        times.append(r.get("time", ""))
        ns_state_numeric.append(_ns_state_numeric(r.get("ns_state", "")))
        energy.append(_parse_float(r.get("energy")))
        focus.append(_parse_float(r.get("focus")))
        connection.append(_parse_float(r.get("connection")))
        steps.append(_parse_float(r.get("steps")))
        resting_hr.append(_parse_float(r.get("resting_hr")))
        mins_sedentary.append(_parse_float(r.get("mins_sedentary")))

    return {
        "dates": dates,
        "times": times,
        "ns_state_numeric": ns_state_numeric,
        "energy": energy,
        "focus": focus,
        "connection": connection,
        "steps": steps,
        "resting_hr": resting_hr,
        "mins_sedentary": mins_sedentary,
    }


def get_summary_stats(days: int = 30) -> dict:
    """
    Returns summary statistics for the last `days` days.
    """
    rows = _read_rows(days)

    if not rows:
        return {
            "most_common_state": "—",
            "avg_energy": None,
            "avg_focus": None,
            "avg_connection": None,
            "avg_steps": None,
            "total_checkins": 0,
            "green_pct": 0.0,
            "yellow_pct": 0.0,
            "red_pct": 0.0,
        }

    total = len(rows)
    state_counts: dict[str, int] = {}
    green = yellow = red = 0

    energies = []
    focuses = []
    connections = []
    steps_list = []

    for r in rows:
        state = r.get("ns_state", "")
        state_counts[state] = state_counts.get(state, 0) + 1
        numeric = _ns_state_numeric(state)
        if numeric == 3:
            green += 1
        elif numeric == 2:
            yellow += 1
        elif numeric == 1:
            red += 1

        v = _parse_float(r.get("energy"))
        if v is not None:
            energies.append(v)
        v = _parse_float(r.get("focus"))
        if v is not None:
            focuses.append(v)
        v = _parse_float(r.get("connection"))
        if v is not None:
            connections.append(v)
        v = _parse_float(r.get("steps"))
        if v is not None:
            steps_list.append(v)

    most_common_state = max(state_counts, key=lambda k: state_counts[k]) if state_counts else "—"

    def avg(lst):
        return round(sum(lst) / len(lst), 1) if lst else None

    return {
        "most_common_state": most_common_state,
        "avg_energy": avg(energies),
        "avg_focus": avg(focuses),
        "avg_connection": avg(connections),
        "avg_steps": avg(steps_list),
        "total_checkins": total,
        "green_pct": round(green / total * 100, 1),
        "yellow_pct": round(yellow / total * 100, 1),
        "red_pct": round(red / total * 100, 1),
    }
