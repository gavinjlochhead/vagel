from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user,
)
import config
from modules import csv_logger, ha_client, nutrition as nutrition_module
from api import claude_client
from api.trends import get_trend_data, get_summary_stats
from api.nutrition_status import nutrition_status_bp

try:
    from modules import fitbit as fitbit_module
except ImportError:
    fitbit_module = None

app = Flask(__name__)
app.register_blueprint(nutrition_status_bp)
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
        snapshot = fitbit_module.get_fitbit_snapshot() if fitbit_module else {}
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
            # Fitbit fields from HA snapshot
            "steps": snapshot.get("steps") or "",
            "resting_hr": snapshot.get("resting_hr") or "",
            "mins_very_active": snapshot.get("mins_very_active") or "",
            "mins_fairly_active": snapshot.get("mins_fairly_active") or "",
            "mins_sedentary": snapshot.get("mins_sedentary") or "",
            "activity_calories": snapshot.get("activity_calories") or "",
            "distance": snapshot.get("distance") or "",
            "floors": snapshot.get("floors") or "",
            # Nutrition fields from today's nutrition log
            "protein_g": nutrition_module.get_today_summary()["protein_g"],
            "carbs_g": nutrition_module.get_today_summary()["carbs_g"],
            "fat_g": nutrition_module.get_today_summary()["fat_g"],
            "fibre_g": nutrition_module.get_today_summary()["fibre_g"],
            # Screen time from HA snapshot
            "screen_time_total": snapshot.get("screen_time_total") or "",
            "screen_time_last_hr": snapshot.get("screen_time_last_hr") or "",
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

        # Claude API integration
        checkin_ctx = {
            "ns_state": row["ns_state"],
            "energy": row["energy"],
            "focus": row["focus"],
            "connection": row["connection"],
            "sleep_hours": row["sleep_hours"],
            "sleep_quality": row["sleep_quality"],
            "wake_time": row["wake_time"],
            "caffeine_count": row["caffeine_count"],
            "caffeine_timing": row["caffeine_timing"],
        }
        fitbit_ctx = dict(snapshot) if snapshot else {}
        nutrition_ctx = nutrition_module.get_today_summary()
        recent = csv_logger.read_recent(7)

        try:
            claude_resp = claude_client.get_checkin_response(
                checkin=checkin_ctx,
                fitbit=fitbit_ctx,
                nutrition=nutrition_ctx,
                recent_history=recent,
                note=row["note"],
            )
            session["claude_response"] = claude_resp
        except Exception:
            session["claude_response"] = None

        flash("Check-in saved", "success")
        return redirect(url_for("checkin"))

    # Count today's check-ins
    all_rows = csv_logger.read_recent(100)
    todays_count = sum(1 for r in all_rows if r.get("date") == today)

    snapshot = fitbit_module.get_fitbit_snapshot() if fitbit_module else {}
    claude_response = session.pop("claude_response", None)
    nutrition_summary = nutrition_module.get_today_summary()
    return render_template(
        "checkin.html",
        todays_count=todays_count,
        fitbit=snapshot,
        claude_response=claude_response,
        nutrition_summary=nutrition_summary,
    )


@app.route("/nutrition")
@login_required
def nutrition():
    return render_template("nutrition.html")


@app.route("/trends")
@login_required
def trends():
    days = int(request.args.get("days", 30))
    summary_stats = get_summary_stats(days)
    return render_template("trends.html", summary_stats=summary_stats, days=days)


@app.route("/api/trends/data")
@login_required
def trends_data():
    days = int(request.args.get("days", 30))
    return jsonify(get_trend_data(days))


@app.route("/insights")
@login_required
def insights():
    return render_template("insights.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
