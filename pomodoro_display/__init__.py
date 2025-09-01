"""
Pomodoro Display System

A self-hosted Pomodoro timer with fullscreen display and remote control.
"""

from ._version import version as __version__  # noqa
from .app import app, main

__all__ = ["app", "main"]
