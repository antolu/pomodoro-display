#!/usr/bin/env python3
"""
Pomodoro Display System - Flask Application
"""

import json
import os
import threading
import time
from typing import Any

from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for remote access


DEFAULT_PORT = 5000

# Default timer durations in seconds
DEFAULT_DURATIONS: dict[str, int] = {
    "pomodoro": 25 * 60,  # 25 minutes
    "short_break": 5 * 60,  # 5 minutes
    "long_break": 15 * 60,  # 15 minutes
}

# Config file path - use data directory if available (for Docker), otherwise current directory
DATA_DIR = (
    "/app/data"
    if os.path.exists("/app/data") and os.access("/app/data", os.W_OK)
    else "."
)
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

# Duration limits (in minutes)
MAX_DURATION_MINUTES = 120
NYAN_CAT_DURATION = 10.0


# Load durations from config file or use defaults
def load_durations() -> dict[str, int]:
    """Load timer durations from config file, fallback to defaults"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, encoding="utf-8") as f:
                config = json.load(f)
                durations = config.get("durations", DEFAULT_DURATIONS)
                # Validate that all required keys exist
                for key in DEFAULT_DURATIONS:  # noqa: PLC0206
                    if key not in durations:
                        durations[key] = DEFAULT_DURATIONS[key]
                return durations
    except (OSError, json.JSONDecodeError):
        pass
    return DEFAULT_DURATIONS.copy()


def save_durations(durations: dict[str, int]) -> bool:
    """Save timer durations to config file"""
    try:
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)

        config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, encoding="utf-8") as f:
                config = json.load(f)

        config["durations"] = durations

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error saving configuration to {CONFIG_FILE}: {e}")
        return False
    else:
        print(f"Configuration saved successfully to {CONFIG_FILE}")
        return True


# Current durations - loaded from config
DURATIONS = load_durations()


# Global timer state
class TimerState:
    def __init__(self) -> None:
        self.active: bool = False
        self.mode: str | None = None
        self.start_time: float | None = None
        self.duration: int = 0
        self.auto_cycle: bool = False
        self.pomodoro_count: int = 0
        self.current_task: str = ""
        self.just_completed: bool = False
        self.paused: bool = False
        self.paused_remaining: int = 0
        self.nyan_cat_active: bool = False
        self.nyan_cat_start_time: float | None = None
        self.lock: threading.RLock = threading.RLock()

    def start(self, mode: str, task: str | None = None) -> None:
        with self.lock:
            self.active = True
            self.mode = mode
            self.start_time = time.time()
            self.duration = DURATIONS.get(mode, 25 * 60)
            self.just_completed = False
            self.paused = False
            self.paused_remaining = 0

            # Track Pomodoro count for auto-cycle
            if mode == "pomodoro":
                self.pomodoro_count += 1
                if task:
                    self.current_task = task

    def stop(self) -> None:
        with self.lock:
            self.active = False
            self.mode = None
            self.start_time = None
            self.duration = 0
            self.just_completed = False
            self.paused = False
            self.paused_remaining = 0

    def pause(self) -> bool:
        """Pause the timer, storing current remaining time"""
        with self.lock:
            if not self.active or self.paused:
                return False

            # Store remaining time when pausing
            if self.start_time is not None:
                elapsed = time.time() - self.start_time
                self.paused_remaining = max(0, self.duration - int(elapsed))
                self.paused = True
                return True
            return False

    def resume(self) -> bool:
        """Resume the timer from paused state"""
        with self.lock:
            if not self.active or not self.paused:
                return False

            # Reset start_time to continue from paused_remaining
            self.start_time = time.time() - (self.duration - self.paused_remaining)
            self.paused = False
            self.paused_remaining = 0
            return True

    def toggle_pause(self) -> bool:
        """Toggle between pause and resume states"""
        with self.lock:
            if not self.active:
                return False

            if self.paused:
                return self.resume()
            return self.pause()

    def get_remaining(self) -> int:
        with self.lock:
            if not self.active:
                return 0

            # If paused, return the stored remaining time
            if self.paused:
                return self.paused_remaining

            # Normal calculation when running
            if self.start_time is None:
                return 0

            elapsed = time.time() - self.start_time
            remaining = max(0, self.duration - elapsed)

            # Check if timer completed (only when not paused)
            if remaining == 0 and self.active and not self.paused:
                self.active = False
                self.just_completed = True
                # Don't auto-cycle immediately - wait for user action
                # Auto-cycle only works from control panel

            return int(remaining)

    def confirm_next(self) -> None:
        """User confirms to proceed to next session"""
        with self.lock:
            self.just_completed = False
            if self.mode == "pomodoro":
                # After 4 pomodoros, take a long break
                if self.pomodoro_count % 4 == 0:
                    self.start("long_break")
                else:
                    self.start("short_break")
            else:
                # After any break, start a new pomodoro
                self.start("pomodoro")

    def toggle_auto_cycle(self) -> bool:
        with self.lock:
            self.auto_cycle = not self.auto_cycle
            return self.auto_cycle

    def get_status(self) -> dict[str, Any]:
        with self.lock:
            nyan_status = self.check_nyan_cat_status()
            return {
                "active": self.active,
                "mode": self.mode,
                "remaining": self.get_remaining(),
                "total": self.duration,
                "auto_cycle": self.auto_cycle,
                "pomodoro_count": self.pomodoro_count,
                "current_task": self.current_task,
                "just_completed": self.just_completed,
                "paused": self.paused,
                "nyan_cat": nyan_status,
            }

    def set_task(self, task: str) -> None:
        with self.lock:
            self.current_task = task

    def reset_cycle(self) -> None:
        with self.lock:
            self.pomodoro_count = 0

    def trigger_nyan_cat(self) -> None:
        """Trigger Nyan Cat animation across all connected clients"""
        with self.lock:
            self.nyan_cat_active = True
            self.nyan_cat_start_time = time.time()

    def check_nyan_cat_status(self) -> dict[str, bool | int]:
        """Check current Nyan Cat status and auto-deactivate after 10 seconds"""
        with self.lock:
            if self.nyan_cat_active and self.nyan_cat_start_time:
                elapsed = time.time() - self.nyan_cat_start_time
                if elapsed >= NYAN_CAT_DURATION:  # 10 seconds duration
                    self.nyan_cat_active = False
                    self.nyan_cat_start_time = None
                else:
                    return {
                        "active": True,
                        "remaining": max(0, int(NYAN_CAT_DURATION - elapsed)),
                    }
            return {"active": False, "remaining": 0}


# Create global timer instance
timer = TimerState()


# Routes
@app.route("/")
def display() -> str:
    """Fullscreen timer display (main page)"""
    return render_template("display.html")


@app.route("/control")
def control() -> str:
    """Control panel interface"""
    return render_template("control.html")


@app.route("/start/<mode>")
def start_timer(mode: str) -> Response:
    """Start timer with specified mode"""
    if mode not in DURATIONS:
        return jsonify({"error": "Invalid mode"}), 400

    task = request.args.get("task", "")
    timer.start(mode, task)
    return jsonify({"status": "started", "mode": mode})


@app.route("/stop")
def stop_timer() -> Response:
    """Stop/reset the timer"""
    timer.stop()
    return jsonify({"status": "stopped"})


@app.route("/status")
def get_status() -> Response:
    """Get current timer status"""
    return jsonify(timer.get_status())


@app.route("/toggle_auto")
def toggle_auto() -> Response:
    """Toggle auto-cycle mode"""
    auto_cycle = timer.toggle_auto_cycle()
    return jsonify({"auto_cycle": auto_cycle})


@app.route("/toggle_pause")
def toggle_pause() -> Response:
    """Toggle pause/resume state"""
    success = timer.toggle_pause()
    return jsonify({"paused": timer.paused, "success": success})


@app.route("/reset_cycle")
def reset_cycle() -> Response:
    """Reset the Pomodoro cycle counter"""
    timer.reset_cycle()
    return jsonify({"status": "cycle_reset"})


@app.route("/set_task", methods=["POST"])
def set_task() -> Response:
    """Set the current task title"""
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    task = data.get("task", "")
    timer.set_task(task)
    return jsonify({"status": "task_set", "task": task})


@app.route("/confirm_next")
def confirm_next() -> Response:
    """Confirm proceeding to next session"""
    timer.confirm_next()
    return jsonify({"status": "next_confirmed"})


@app.route("/get_durations")
def get_durations() -> Response:
    """Get current timer durations in minutes"""
    durations_minutes = {key: value // 60 for key, value in DURATIONS.items()}
    return jsonify({"durations": durations_minutes})


def _validate_duration_data(durations_data: dict[str, Any]) -> Response | None:
    """Validate duration data, return error response if invalid."""
    required_keys = ["pomodoro", "short_break", "long_break"]
    for key in required_keys:
        if key not in durations_data:
            return jsonify({"error": f"Missing {key} duration"}), 400

        try:
            minutes = int(durations_data[key])
            if minutes < 1 or minutes > MAX_DURATION_MINUTES:
                return jsonify({
                    "error": f"{key} must be between 1 and {MAX_DURATION_MINUTES} minutes"
                }), 400
        except (ValueError, TypeError):
            return jsonify({"error": f"Invalid {key} duration"}), 400
    return None


@app.route("/trigger_nyancat")
def trigger_nyancat() -> Response:
    """Trigger Nyan Cat animation across all connected clients"""
    timer.trigger_nyan_cat()
    return jsonify({"status": "nyan_cat_triggered"})


@app.route("/set_durations", methods=["POST"])
def set_durations() -> Response:
    """Set timer durations (in minutes)"""
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    durations_data = data.get("durations")
    if not durations_data:
        return jsonify({"error": "Missing durations"}), 400

    # Validate input
    validation_error = _validate_duration_data(durations_data)
    if validation_error:
        return validation_error

    # Convert minutes to seconds and update
    new_durations = {key: int(durations_data[key]) * 60 for key in durations_data}

    # Save to config file and update global
    if save_durations(new_durations):
        global DURATIONS  # noqa: PLW0603
        DURATIONS = new_durations
        return jsonify({"status": "durations_updated", "durations": durations_data})
    return jsonify({
        "error": "Failed to save configuration",
        "config_file": CONFIG_FILE,
        "data_dir": DATA_DIR,
        "writable": os.access(DATA_DIR, os.W_OK) if os.path.exists(DATA_DIR) else False,
    }), 500


# Background timer thread
def timer_thread() -> None:
    """Background thread to update timer state"""
    while True:
        if timer.active:
            timer.get_remaining()  # This will trigger auto-cycle if needed
        time.sleep(1)


# Start background timer thread
threading.Thread(target=timer_thread, daemon=True).start()


def main() -> None:
    """Main entry point for the application"""
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    debug = os.environ.get("DEBUG", "False").lower() == "true"

    print(f"""
    ╔════════════════════════════════════════╗
    ║     Pomodoro Display System Started    ║
    ╠════════════════════════════════════════╣
    ║  Control Panel: http://0.0.0.0:{port:<5}   ║
    ║  Display:       http://0.0.0.0:{port}/display ║
    ╚════════════════════════════════════════╝
    """)

    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
