# Pomodoro Display System

A self-hosted Pomodoro timer system with a dedicated fullscreen display and remote control capabilities.

## Features

- 🖥️ **Dual-screen support**: Control panel and fullscreen timer display
- 📱 **Remote control**: Access from any device on your network
- 🎨 **Modern UI**: Beautiful, responsive design with smooth animations
- 🔄 **Auto-cycle**: Automatic progression through Pomodoro cycles
- 🌐 **REST API**: Control via browser or command line
- ⚡ **Real-time updates**: Live timer synchronization across all clients

## Installation

### Via pip (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd pomodoro-display

# Install the package
pip install -e .

# Or install with pip directly
pip install .
```

### Manual installation

```bash
# Install dependencies
pip install flask flask-cors

# Run directly
python -m pomodoro_display.app
```

## Usage

### Starting the server

```bash
# Using the installed command
pomodoro-display

# Or using Python module
python -m pomodoro_display.app
```

The server will start on `http://0.0.0.0:5000`

### Accessing the interfaces

- **Control Panel**: `http://<your-ip>:5000/`
- **Fullscreen Display**: `http://<your-ip>:5000/display`

### Remote control via command line

```bash
# Start a Pomodoro session (25 minutes)
curl http://<host>:5000/start/pomodoro

# Start a short break (5 minutes)
curl http://<host>:5000/start/short_break

# Start a long break (15 minutes)
curl http://<host>:5000/start/long_break

# Stop/reset the timer
curl http://<host>:5000/stop

# Get current status
curl http://<host>:5000/status
```

## Configuration

Edit the durations in `pomodoro_display/app.py`:

```python
DURATIONS = {
    'pomodoro': 25 * 60,      # 25 minutes
    'short_break': 5 * 60,    # 5 minutes
    'long_break': 15 * 60     # 15 minutes
}
```

## Auto-cycle Mode

The system supports automatic Pomodoro cycles:

- After 4 Pomodoros → Long break
- After breaks → Next Pomodoro
- Toggle via the control panel

## Multi-screen Setup

1. Open the display page on your dedicated monitor
2. Press F11 to enter fullscreen mode
3. Use the control page on another device or screen

## Network Access

To access from other devices on your network:

1. Find your computer's IP address:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig` or `ip addr`
2. Access via `http://<your-ip>:5000`

## Development

### Project Structure

```
pomodoro_display/
├── __init__.py           # Package initialization
├── app.py               # Flask application
├── templates/
│   ├── control.html     # Control panel UI
│   └── display.html     # Fullscreen timer display
└── static/
    └── (CSS/JS files if needed)
```

### API Endpoints

- `GET /` - Control panel interface
- `GET /display` - Fullscreen timer display
- `GET /start/<mode>` - Start timer (modes: pomodoro, short_break, long_break)
- `GET /stop` - Stop/reset timer
- `GET /status` - Get current timer status
- `GET /toggle_auto` - Toggle auto-cycle mode

### Status Response Format

```json
{
    "active": true,
    "mode": "pomodoro",
    "remaining": 1420,
    "total": 1500,
    "auto_cycle": true,
    "pomodoro_count": 2
}
```

## Troubleshooting

### Timer not updating

- Check network connectivity
- Ensure JavaScript is enabled
- Check browser console for errors

### Cannot access from other devices

- Ensure firewall allows port 5000
- Verify the server is bound to 0.0.0.0
- Check your network settings
