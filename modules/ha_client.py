import requests
import config


def get_state(entity_id) -> dict | None:
    """GET /api/states/<entity_id>. Returns full state object dict or None on any error."""
    try:
        url = f"{config.HA_URL}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {config.HA_TOKEN}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def set_state(entity_id, state, attributes=None):
    """POST /api/states/<entity_id>. Silently swallows errors."""
    try:
        url = f"{config.HA_URL}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {config.HA_TOKEN}",
            "Content-Type": "application/json",
        }
        body = {"state": state, "attributes": attributes or {}}
        requests.post(url, headers=headers, json=body, timeout=5)
    except Exception:
        pass
