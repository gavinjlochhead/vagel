# Home Assistant Setup Guide — Polyvagal Tracker

## 1. Update existing check-in reminder automations

You have 5 existing check-in reminder automations. Each one currently navigates to a Lovelace dashboard view. Update them to open the Flask app's check-in page directly on your phone instead.

In each automation, find the `tap_action` block and change it from:

```yaml
tap_action:
  action: navigate
  navigation_path: /lovelace/...
```

To:

```yaml
tap_action:
  action: uri
  uri: "http://<YOUR_TAILSCALE_IP>:5000/checkin"
```

Replace `<YOUR_TAILSCALE_IP>` with the Tailscale IP of the machine running Flask (see section 3 below).

---

## 2. Food logging reminder automations

### 2a. REST sensor (add to configuration.yaml or sensors.yaml)

This sensor polls the Flask endpoint hourly so automations can check whether food has been logged today.

```yaml
sensor:
  - platform: rest
    name: "Nutrition Logged Today"
    resource: "http://<YOUR_FLASK_IP>:5000/api/nutrition/logged-today"
    value_template: "{{ value_json.logged }}"
    json_attributes:
      - count
    scan_interval: 3600  # poll hourly; lower to 300 (5 min) if you want faster updates
```

After adding this, restart Home Assistant and confirm the sensor appears as `sensor.nutrition_logged_today` with a state of `True` or `False`.

### 2b. Automation YAML (add to automations.yaml or via the UI)

```yaml
automation:
  - alias: "Nutrition log reminder 13:00"
    description: "Nudge if nothing has been logged by lunchtime"
    trigger:
      - platform: time
        at: "13:00:00"
    condition:
      - condition: template
        value_template: "{{ states('sensor.nutrition_logged_today') == 'False' }}"
    action:
      - service: notify.mobile_app_<your_phone>
        data:
          title: "🍎 Food log"
          message: "Nothing logged yet today. 30 seconds to add breakfast or lunch?"
          data:
            actions:
              - action: URI
                title: "Log food"
                uri: "http://<YOUR_FLASK_IP>:5000/nutrition"

  - alias: "Nutrition log reminder 18:00"
    description: "Evening nudge if still nothing logged"
    trigger:
      - platform: time
        at: "18:00:00"
    condition:
      - condition: template
        value_template: "{{ states('sensor.nutrition_logged_today') == 'False' }}"
    action:
      - service: notify.mobile_app_<your_phone>
        data:
          title: "🍎 Food log"
          message: "Still nothing logged today — 30 seconds to add one meal?"
          data:
            actions:
              - action: URI
                title: "Log food"
                uri: "http://<YOUR_FLASK_IP>:5000/nutrition"
```

**Placeholders to replace:**

| Placeholder | What to put there |
|---|---|
| `<YOUR_FLASK_IP>` | Tailscale IP of the machine running Flask (e.g. `100.x.x.x`) |
| `<YOUR_TAILSCALE_IP>` | Same IP as above |
| `<your_phone>` | Your HA mobile app device name (e.g. `pixel_8` → service becomes `notify.mobile_app_pixel_8`) |

---

## 3. Finding your Tailscale IP

On the machine running Flask:

```bash
tailscale ip -4
```

This returns something like `100.x.x.x`. Use this address in all `uri:` and `resource:` fields above so the connection works whether you're on your home network or away.

Alternatively, open the Tailscale admin console at https://login.tailscale.com/admin/machines and find the machine there.

## 4. HA long-lived access token (if needed for future integrations)

If you later want HA to authenticate against a protected Flask endpoint, or want Flask to call the HA REST API:

1. In Home Assistant, go to your **Profile** (bottom-left avatar).
2. Scroll to **Long-lived access tokens** and click **Create token**.
3. Give it a name (e.g. `polyvagal-flask`) and copy the token immediately — it is only shown once.
4. Store it in your Flask `.env` file as `HA_TOKEN=<token>` and reference it via `config.py`.

The current `/api/nutrition/logged-today` endpoint is intentionally unauthenticated because it is called by the HA REST sensor, which does not support custom headers by default. If you later want to restrict it, add an `Authorization: Bearer <token>` header to the sensor config and a `@require_api_key` decorator on the Flask route.
