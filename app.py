from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user,
)
import config
from modules import csv_logger, ha_client

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."


class AdminUser(UserMixin):
    def get_id(self):
        return "admin"


ADMIN_USER = AdminUser()


@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return ADMIN_USER
    return None


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == config.ADMIN_PASSWORD:
            login_user(ADMIN_USER)
            return redirect(url_for("checkin"))
        flash("Incorrect password.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Main routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return redirect(url_for("checkin"))


@app.route("/checkin", methods=["GET", "POST"])
@login_required
def checkin():
    today = date.today().isoformat()

    if request.method == "POST":
        now = datetime.now()
        row = {
            "date": today,
            "time": now.strftime("%H:%M"),
            "triggered_by": request.form.get("triggered_by", ""),
            "ns_state": request.form.get("ns_state", ""),
            "energy": request.form.get("energy", ""),
            "energy_why": request.form.get("energy_why", ""),
            "focus": request.form.get("focus", ""),
            "focus_why": request.form.get("focus_why", ""),
            "connection": request.form.get("connection", ""),
            "connection_why": request.form.get("connection_why", ""),
            "sleep_hours": request.form.get("sleep_hours", ""),
            "sleep_quality": request.form.get("sleep_quality", ""),
            "wake_time": request.form.get("wake_time", ""),
            "caffeine_count": request.form.get("caffeine_count", ""),
            "caffeine_timing": request.form.get("caffeine_timing", ""),
            # Fitbit fields left empty until Phase 2A
            "steps": "",
            "resting_hr": "",
            "mins_very_active": "",
            "mins_fairly_active": "",
            "mins_sedentary": "",
            "activity_calories": "",
            "distance": "",
            "floors": "",
            # Nutrition fields left empty until Phase 3B
            "protein_g": "",
            "carbs_g": "",
            "fat_g": "",
            "fibre_g": "",
            # Screen time left empty until Phase 2A
            "screen_time_total": "",
            "screen_time_last_hr": "",
            "note": request.form.get("note", ""),
        }

        # Save to CSV
        csv_logger.append_row(row)

        # Write-back to Home Assistant (errors swallowed inside ha_client)
        ha_client.set_state(config.HA_NS_STATE_ENTITY, row["ns_state"])
        ha_client.set_state(config.HA_ENERGY_ENTITY, row["energy"])
        ha_client.set_state(config.HA_FOCUS_ENTITY, row["focus"])
        ha_client.set_state(config.HA_CONNECTION_ENTITY, row["connection"])
        ha_client.set_state(config.HA_ENERGY_WHY_ENTITY, row["energy_why"])
        ha_client.set_state(config.HA_FOCUS_WHY_ENTITY, row["focus_why"])
        ha_client.set_state(config.HA_CONNECTION_WHY_ENTITY, row["connection_why"])
        ha_client.set_state(config.HA_SLEEP_HOURS_ENTITY, row["sleep_hours"])
        ha_client.set_state(config.HA_SLEEP_QUALITY_ENTITY, row["sleep_quality"])
        ha_client.set_state(config.HA_WAKE_TIME_ENTITY, row["wake_time"])
        ha_client.set_state(config.HA_CAFFEINE_COUNT_ENTITY, row["caffeine_count"])
        ha_client.set_state(config.HA_CAFFEINE_TIMING_ENTITY, row["caffeine_timing"])
        ha_client.set_state(config.HA_CHECKIN_TRIGGER_ENTITY, row["triggered_by"])
        ha_client.set_state(config.HA_CHECKIN_NOTE_ENTITY, row["note"])

        flash("Check-in saved", "success")
        return redirect(url_for("checkin"))

    # Count today's check-ins
    all_rows = csv_logger.read_recent(100)
    todays_count = sum(1 for r in all_rows if r.get("date") == today)

    return render_template("checkin.html", todays_count=todays_count)


@app.route("/nutrition")
@login_required
def nutrition():
    return render_template("nutrition.html")


@app.route("/trends")
@login_required
def trends():
    return render_template("trends.html")


@app.route("/insights")
@login_required
def insights():
    return render_template("insights.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
