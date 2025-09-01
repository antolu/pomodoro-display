# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based Pomodoro timer system with dual-screen support - a control panel and fullscreen display. The main application is in `pomodoro_display/app.py` with HTML templates for the web interfaces.

## Development Commands

### Installation and Setup
```bash
pip install -e .                    # Install in development mode
pip install -e .[dev,test,doc]      # Install with all optional dependencies
```

### Running the Application
```bash
pomodoro-display                     # Run using installed console script
python -m pomodoro_display.app      # Run as Python module
```

### Testing and Quality Checks
```bash
python -m pytest ./tests --cov=pomodoro-display --cov-report term --cov-report html:coverage-html
pre-commit run --all-files          # Run all pre-commit hooks
ruff check --fix --unsafe-fixes --preview  # Lint and auto-fix
ruff format                          # Format code
mypy .                               # Type checking
```

### Build and Packaging
```bash
pip install build
python -m build                     # Build sdist and wheel
```

## Architecture

### Core Components

- **`pomodoro_display/app.py`**: Main Flask application with timer state management
  - `TimerState` class: Thread-safe timer state with auto-cycle functionality
  - Flask routes for REST API endpoints and web interfaces
  - Background timer thread for state updates

- **`pomodoro_display/templates/`**: Web interface templates
  - `control.html`: Interactive control panel with modern UI (TailwindCSS + Alpine.js)
  - `display.html`: Fullscreen timer display with animations

### Timer State Management

The `TimerState` class manages all timer functionality:
- Thread-safe operations using `threading.Lock()`
- Auto-cycle mode for automatic Pomodoro progression
- Real-time updates via background thread
- Supports three modes: `pomodoro`, `short_break`, `long_break`

### Web Interface Routes

- `GET /` - Fullscreen timer display (main page)
- `GET /control` - Control panel interface

### REST API Endpoints

- `GET /start/<mode>` - Start timer with mode (pomodoro/short_break/long_break)
- `GET /stop` - Stop/reset timer
- `GET /status` - Get current timer status (JSON)
- `GET /toggle_auto` - Toggle auto-cycle mode
- `GET /reset_cycle` - Reset Pomodoro cycle counter
- `POST /set_task` - Set current task title
- `GET /confirm_next` - Confirm proceeding to next session

## Configuration

### Timer Durations
Modify `DURATIONS` dict in `app.py`:
```python
DURATIONS = {
    "pomodoro": 25 * 60,      # 25 minutes
    "short_break": 5 * 60,    # 5 minutes
    "long_break": 15 * 60     # 15 minutes
}
```

### Code Quality Standards

- Uses `from __future__ import annotations` for forward compatibility
- All functions must have type annotations (enforced by mypy)
- Pre-commit hooks enforce code quality:
  - Ruff for linting and formatting
  - MyPy for type checking
  - Various pre-commit hooks for file consistency

### Project Structure

```
pomodoro_display/
├── __init__.py           # Package initialization with version
├── app.py               # Main Flask application (executable)
├── templates/
│   ├── control.html     # Control panel interface
│   └── display.html     # Fullscreen timer display
└── _version.py          # Auto-generated version file
```

The project uses setuptools-scm for dynamic versioning and includes a console script entry point `pomodoro-display` for easy execution.
