import os
from dotenv import load_dotenv

load_dotenv()

# Home Assistant
HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# Flask
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

# Fitbit sensor entity IDs
FITBIT_STEPS_ENTITY = os.getenv("FITBIT_STEPS_ENTITY", "sensor.gavin_l_steps")
FITBIT_RHR_ENTITY = os.getenv("FITBIT_RHR_ENTITY", "sensor.gavin_l_resting_heart_rate")
FITBIT_MINS_VERY_ACTIVE_ENTITY = os.getenv("FITBIT_MINS_VERY_ACTIVE_ENTITY", "sensor.gavin_l_minutes_very_active")
FITBIT_MINS_FAIRLY_ACTIVE_ENTITY = os.getenv("FITBIT_MINS_FAIRLY_ACTIVE_ENTITY", "sensor.gavin_l_minutes_fairly_active")
FITBIT_MINS_SEDENTARY_ENTITY = os.getenv("FITBIT_MINS_SEDENTARY_ENTITY", "sensor.gavin_l_minutes_sedentary")
FITBIT_ACTIVITY_CALORIES_ENTITY = os.getenv("FITBIT_ACTIVITY_CALORIES_ENTITY", "sensor.gavin_l_activity_calories")
FITBIT_DISTANCE_ENTITY = os.getenv("FITBIT_DISTANCE_ENTITY", "sensor.gavin_l_distance")
FITBIT_FLOORS_ENTITY = os.getenv("FITBIT_FLOORS_ENTITY", "sensor.gavin_l_floors")

# HA helper entity IDs for write-back
HA_NS_STATE_ENTITY = os.getenv("HA_NS_STATE_ENTITY", "input_select.nervous_system_state")
HA_ENERGY_ENTITY = os.getenv("HA_ENERGY_ENTITY", "input_number.energy_level")
HA_FOCUS_ENTITY = os.getenv("HA_FOCUS_ENTITY", "input_number.focus_level")
HA_CONNECTION_ENTITY = os.getenv("HA_CONNECTION_ENTITY", "input_number.connection_feeling")
HA_ENERGY_WHY_ENTITY = os.getenv("HA_ENERGY_WHY_ENTITY", "input_select.energy_why")
HA_FOCUS_WHY_ENTITY = os.getenv("HA_FOCUS_WHY_ENTITY", "input_select.focus_why")
HA_CONNECTION_WHY_ENTITY = os.getenv("HA_CONNECTION_WHY_ENTITY", "input_select.connection_why")
HA_SLEEP_HOURS_ENTITY = os.getenv("HA_SLEEP_HOURS_ENTITY", "input_number.sleep_hours")
HA_SLEEP_QUALITY_ENTITY = os.getenv("HA_SLEEP_QUALITY_ENTITY", "input_select.sleep_quality")
HA_WAKE_TIME_ENTITY = os.getenv("HA_WAKE_TIME_ENTITY", "input_select.wake_time")
HA_CAFFEINE_COUNT_ENTITY = os.getenv("HA_CAFFEINE_COUNT_ENTITY", "input_number.caffeine_count")
HA_CAFFEINE_TIMING_ENTITY = os.getenv("HA_CAFFEINE_TIMING_ENTITY", "input_select.caffeine_timing")
HA_CHECKIN_TRIGGER_ENTITY = os.getenv("HA_CHECKIN_TRIGGER_ENTITY", "input_select.checkin_trigger")
HA_CHECKIN_NOTE_ENTITY = os.getenv("HA_CHECKIN_NOTE_ENTITY", "input_text.checkin_note")
HA_SCREEN_TIME_ENTITY = os.getenv("HA_SCREEN_TIME_ENTITY", "sensor.gavin_phone_screen_time")
