#!/usr/bin/env python3
"""
Pomodoro Display System - Flask Application
"""

from __future__ import annotations

import os
import threading
import time

from flask import Flask, jsonify, render_template
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for remote access

# Timer durations in seconds
DURATIONS = {
    "pomodoro": 25 * 60,  # 25 minutes
    "short_break": 5 * 60,  # 5 minutes
    "long_break": 15 * 60,  # 15 minutes
}

DEFAULT_PORT = 5000


# Global timer state
class TimerState:
    def __init__(self) -> None:
        self.active = False
        self.mode: str | None = None
        self.start_time: float | None = None
        self.duration = 0
        self.auto_cycle = False
        self.pomodoro_count = 0
        self.lock = threading.Lock()

    def start(self, mode: str) -> None:
        with self.lock:
            self.active = True
            self.mode = mode
            self.start_time = time.time()
            self.duration = DURATIONS.get(mode, 25 * 60)

            # Track Pomodoro count for auto-cycle
            if mode == "pomodoro":
                self.pomodoro_count += 1

    def stop(self) -> None:
        with self.lock:
            self.active = False
            self.mode = None
            self.start_time = None
            self.duration = 0

    def get_remaining(self) -> int:
        with self.lock:
            if not self.active:
                return 0
            elapsed = time.time() - (self.start_time or 0)
            remaining = max(0, self.duration - elapsed)

            # Check if timer completed
            if remaining == 0 and self.active:
                self.active = False

                # Auto-cycle logic
                if self.auto_cycle:
                    # Schedule next timer in a separate thread to avoid blocking
                    threading.Thread(target=self._auto_cycle_next).start()

            return int(remaining)

    def _auto_cycle_next(self) -> None:
        """Automatically start the next timer in the cycle"""
        time.sleep(1)  # Brief pause before next timer

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

    def get_status(self) -> dict[str, str | int | bool | None]:
        with self.lock:
            return {
                "active": self.active,
                "mode": self.mode,
                "remaining": self.get_remaining(),
                "total": self.duration,
                "auto_cycle": self.auto_cycle,
                "pomodoro_count": self.pomodoro_count,
            }

    def reset_cycle(self) -> None:
        with self.lock:
            self.pomodoro_count = 0


# Create global timer instance
timer = TimerState()


# Routes
@app.route("/")
def control() -> str:
    """Control panel interface"""
    return render_template("control.html")


@app.route("/display")
def display() -> str:
    """Fullscreen timer display"""
    return render_template("display.html")


@app.route("/start/<mode>")
def start_timer(mode: str) -> tuple[str, int] | str:
    """Start timer with specified mode"""
    if mode not in DURATIONS:
        return jsonify({"error": "Invalid mode"}), 400

    timer.start(mode)
    return jsonify({"status": "started", "mode": mode})


@app.route("/stop")
def stop_timer() -> str:
    """Stop/reset the timer"""
    timer.stop()
    return jsonify({"status": "stopped"})


@app.route("/status")
def get_status() -> str:
    """Get current timer status"""
    return jsonify(timer.get_status())


@app.route("/toggle_auto")
def toggle_auto() -> str:
    """Toggle auto-cycle mode"""
    auto_cycle = timer.toggle_auto_cycle()
    return jsonify({"auto_cycle": auto_cycle})


@app.route("/reset_cycle")
def reset_cycle() -> str:
    """Reset the Pomodoro cycle counter"""
    timer.reset_cycle()
    return jsonify({"status": "cycle_reset"})


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
