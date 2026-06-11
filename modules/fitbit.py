import time
import config
from modules import ha_client

# 5-minute in-memory cache
_cache = {}
_CACHE_TTL = 300  # seconds


def _safe_numeric(value, cast=float):
    """Convert a state string to a number, returning None if not possible."""
    if value is None or value in ("unavailable", "unknown", ""):
        return None
    try:
        return cast(value)
    except (ValueError, TypeError):
        return None


def get_fitbit_snapshot() -> dict:
    """
    Reads all Fitbit sensors from HA via ha_client.get_state().
    Returns a dict with these keys (all may be None if sensor unavailable):
      steps, resting_hr, mins_very_active, mins_fairly_active,
      mins_sedentary, activity_calories, distance, floors,
      screen_time_total, screen_time_last_hr
    Caches result for 5 minutes using time.time().
    """
    now = time.time()
    cached = _cache.get("snapshot")
    if cached and (now - cached["ts"]) < _CACHE_TTL:
        return cached["data"]

    def read(entity_id, cast=float):
        result = ha_client.get_state(entity_id)
        if result is None:
            return None
        return _safe_numeric(result.get("state"), cast)

    snapshot = {
        "steps": read(config.FITBIT_STEPS_ENTITY, int),
        "resting_hr": read(config.FITBIT_RHR_ENTITY, int),
        "mins_very_active": read(config.FITBIT_MINS_VERY_ACTIVE_ENTITY, int),
        "mins_fairly_active": read(config.FITBIT_MINS_FAIRLY_ACTIVE_ENTITY, int),
        "mins_sedentary": read(config.FITBIT_MINS_SEDENTARY_ENTITY, int),
        "activity_calories": read(config.FITBIT_ACTIVITY_CALORIES_ENTITY, int),
        "distance": read(config.FITBIT_DISTANCE_ENTITY, float),
        "floors": read(config.FITBIT_FLOORS_ENTITY, int),
        "screen_time_total": read(config.HA_SCREEN_TIME_ENTITY, int),
        "screen_time_last_hr": None,  # No separate entity yet; add HA template sensor later
    }

    _cache["snapshot"] = {"ts": now, "data": snapshot}
    return snapshot
