# Pomodoro Display System

A self-hosted Pomodoro timer system with a dedicated fullscreen display and remote control capabilities.

## Features

- 🖥️ **Dual-screen support**: Control panel and fullscreen timer display
- 📱 **Remote control**: Access from any device on your network
- 🎨 **Modern UI**: Beautiful, responsive design with smooth animations
- ⚙️ **Configurable durations**: Customize timer lengths through web interface or API
- 🔄 **Auto-cycle**: Automatic progression through Pomodoro cycles
- ⏸️ **Pause/Resume**: Pause and resume timers without losing progress
- 📝 **Task tracking**: Set and display current task on timer screen
- 🔊 **Audio notifications**: Different sounds for pomodoro and break completions
- 🔇 **Mute control**: Toggle sound notifications on/off
- 🌐 **REST API**: Control via browser or command line
- ⚡ **Real-time updates**: Live timer synchronization across all clients
- 💾 **Persistent settings**: Configuration saved across browser sessions and server restarts

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

- **Control Panel**: `http://<your-ip>:5000/control`
- **Fullscreen Display**: `http://<your-ip>:5000/` (main page)

### Remote control via command line

#### Basic Timer Control
```bash
# Start a Pomodoro session with optional task
curl "http://<host>:5000/start/pomodoro?task=Write%20documentation"

# Start a short break
curl http://<host>:5000/start/short_break

# Start a long break
curl http://<host>:5000/start/long_break

# Stop/reset the timer
curl http://<host>:5000/stop

# Pause/resume the timer
curl http://<host>:5000/toggle_pause

# Get current status
curl http://<host>:5000/status
```

#### Configuration Management
```bash
# Get current timer durations
curl http://<host>:5000/get_durations

# Set custom durations (in minutes)
curl -X POST -H "Content-Type: application/json" \
  -d '{"durations": {"pomodoro": 30, "short_break": 10, "long_break": 20}}' \
  http://<host>:5000/set_durations

# Set current task
curl -X POST -H "Content-Type: application/json" \
  -d '{"task": "Review pull requests"}' \
  http://<host>:5000/set_task

# Toggle auto-cycle mode
curl http://<host>:5000/toggle_auto

# Reset Pomodoro cycle counter
curl http://<host>:5000/reset_cycle
```

## Configuration

### Timer Durations

You can customize timer durations through multiple methods:

#### 1. Web Interface (Easiest)
1. Open the control panel at `http://<your-ip>:5000/control`
2. Click the "Timer Settings" button
3. Modify durations in the popup modal (1-120 minutes range)
4. Click "Save Settings" - changes persist automatically

#### 2. Command Line API
```bash
# Set custom durations (all values in minutes)
curl -X POST -H "Content-Type: application/json" \
  -d '{"durations": {"pomodoro": 25, "short_break": 5, "long_break": 15}}' \
  http://<host>:5000/set_durations
```

#### 3. Configuration File
Settings are automatically saved to `config.json` in the project directory:
```json
{
  "durations": {
    "pomodoro": 1500,     // 25 minutes (stored in seconds)
    "short_break": 300,   // 5 minutes
    "long_break": 900     // 15 minutes
  }
}
```

### Audio Setup

To enable audio notifications:
1. Place your audio files in `pomodoro_display/static/`:
   - `alarm.wav` - Played when Pomodoro sessions complete
   - `break.wav` - Played when break sessions complete
2. Use the mute/unmute button in the control panel to toggle sounds

### Task Management

- Set current task through the control panel's task input field
- Tasks display on both control panel and fullscreen timer
- Tasks can also be set via API when starting timers

## Auto-cycle Mode

The system supports automatic Pomodoro cycles:

- After 4 Pomodoros → Long break
- After breaks → Next Pomodoro
- Toggle via the control panel

## Multi-screen Setup

### Dedicated Timer Display
1. Open `http://<your-ip>:5000/` on your dedicated monitor
2. Click the fullscreen button (top-right corner) or press F11
3. The display will auto-hide the cursor after 3 seconds of inactivity

### Control Interface
- Use `http://<your-ip>:5000/control` on another device/screen
- Control panel works on phones, tablets, and computers
- All changes reflect immediately on the display screen

### Keyboard Shortcuts (Display Screen)
- **Enter/Space**: Confirm next session when timer completes
- **Escape**: Skip to manual control when timer completes

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
├── static/              # Audio files directory
│   ├── alarm.wav        # Pomodoro completion sound
│   └── break.wav        # Break completion sound
└── _version.py          # Auto-generated version file
config.json              # Persistent configuration (auto-created)
```

### API Endpoints

#### Web Interface Routes
- `GET /` - Fullscreen timer display (main page)
- `GET /control` - Control panel interface

#### Timer Control API
- `GET /start/<mode>?task=<task>` - Start timer with optional task
  - Modes: `pomodoro`, `short_break`, `long_break`
- `GET /stop` - Stop/reset timer
- `GET /toggle_pause` - Toggle pause/resume state
- `GET /status` - Get current timer status (JSON)
- `GET /confirm_next` - Confirm proceeding to next session

#### Configuration API
- `GET /get_durations` - Get current timer durations (in minutes)
- `POST /set_durations` - Set custom timer durations (in minutes)
- `POST /set_task` - Set current task title
- `GET /toggle_auto` - Toggle auto-cycle mode
- `GET /reset_cycle` - Reset Pomodoro cycle counter

### Status Response Format

```json
{
    "active": true,
    "mode": "pomodoro",
    "remaining": 1420,
    "total": 1500,
    "auto_cycle": true,
    "pomodoro_count": 2,
    "current_task": "Write documentation",
    "just_completed": false,
    "paused": false
}
```

### Configuration API Examples

#### Get Durations Response
```json
{
    "durations": {
        "pomodoro": 25,
        "short_break": 5,
        "long_break": 15
    }
}
```

#### Set Durations Request
```json
{
    "durations": {
        "pomodoro": 30,
        "short_break": 10,
        "long_break": 20
    }
}
```

## Troubleshooting

### Timer not updating

- Check network connectivity
- Ensure JavaScript is enabled
- Check browser console for errors

### Audio not playing

- Ensure audio files (`alarm.wav`, `break.wav`) are in the `pomodoro_display/static/` directory
- Check that sounds aren't muted in the control panel
- Verify browser allows audio playback (some browsers require user interaction first)
- Check browser console for audio-related errors

### Settings not persisting

- Ensure the application has write permissions in its directory
- Check that `config.json` file is being created and updated
- Verify localStorage is enabled in your browser

### Cannot access from other devices

- Ensure firewall allows port 5000
- Verify the server is bound to 0.0.0.0 (not localhost/127.0.0.1)
- Check your network settings and IP address

### Pause/Resume not working

- Ensure timer is active before attempting to pause
- Check the `/toggle_pause` endpoint returns successful response
- Verify the paused state shows in the status response
