# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Disability Support System** for Raspberry Pi that provides voice and vision-based assistance. The system uses a button-triggered workflow to record audio questions, capture images, process both through an LLM API, and deliver spoken responses.

**Target Platform:** Raspberry Pi 3 Model B+ running Raspberry Pi OS
**Deployment Path:** `/home/thuongvv/rsbp-demo/`
**User:** thuongvv

## System Architecture

### Core Pipeline Flow

The system implements a state-driven pipeline triggered by GPIO button presses:

1. **Button Press 1** → Start audio recording (threaded, non-blocking)
2. **Button Press 2** → Stop recording + Capture image (simultaneously)
3. **API Processing** → Three sequential API calls:
   - STT: Audio → Text transcription
   - Vision: Image → Description
   - TTS: Combined response → Speech audio
4. **Playback** → Play response audio through speaker
5. **Loop** → Return to waiting for button press

### Module Responsibilities

**config.py** - Single source of truth for all configuration
- Hardware specs (GPIO pin, audio sample rate, camera quality)
- API endpoints (loaded from `API_KEY` environment variable)
- File paths and naming patterns
- **CRITICAL:** API_BASE_URL is loaded from `os.getenv("API_KEY")` not "API_URL"

**main.py** - System orchestrator with state machine
- Manages component lifecycle (initialize, run, shutdown)
- Button callback toggles between recording/processing states
- Coordinates the complete pipeline in `stop_recording_and_process()`
- Signal handlers for graceful shutdown

**button_handler.py** - GPIO event-driven input
- BCM mode GPIO 17 with 500ms debounce
- Falling edge detection (pull-up resistor, active low)
- Graceful degradation if GPIO unavailable (for dev environments)

**audio_recorder.py** - Threaded audio capture
- Auto-detects ReSpeaker HAT or uses default input device
- Non-blocking recording via separate thread
- 16kHz mono 16-bit PCM WAV output

**image_capture.py** - Subprocess-based camera control
- Uses `rpicam-jpeg` command-line tool (required by spec)
- Maximum resolution JPEG output
- 1 second timeout for capture

**llm_client.py** - HTTP API client
- Three multipart/form-data POST endpoints
- File upload for audio/image, JSON payload for TTS
- Handles various response formats (binary audio, JSON with base64/URL)
- 30-second timeout on all requests

**audio_playback.py** - Audio output with fallback
- Primary: `aplay` (ALSA command-line tool)
- Fallback: PyAudio if aplay unavailable
- Blocking and non-blocking modes

## Testing Commands

### Hardware Testing (No API Required)
```bash
source venv/bin/activate
python3 test_hardware.py
```
Interactive menu to test camera, microphone, speaker, button independently. Use this when API is not available or debugging hardware issues.

### Module/Integration Testing
```bash
source venv/bin/activate
python3 test_modules.py
```
Tests imports, configuration, dependencies, and component initialization. Tests API connectivity if available.

### Run Main System
```bash
source venv/bin/activate
python3 main.py
```
Starts the main event loop. Press Ctrl+C to shutdown gracefully.

### View Logs
```bash
tail -f logs/system.log
```
Real-time monitoring of system activity.

## Installation & Setup

### Quick Install
```bash
./install.sh
```
Automated script that installs system dependencies, creates venv, installs Python packages, sets user groups, and runs tests.

### Manual Setup
```bash
# System dependencies
sudo apt install python3 python3-pip python3-venv -y
sudo apt install alsa-utils portaudio19-dev python3-dev libasound2-dev -y
sudo apt install rpicam-apps -y

# IMPORTANT: Install RPi.GPIO as system package for proper permissions
sudo apt install python3-rpi.gpio -y

# Python environment (use --system-site-packages for GPIO access)
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Note: PyAudio may fail to build. If so, install via apt instead:
sudo apt install python3-pyaudio -y
pip3 install requests

# Configuration
cp .env.example .env
# Edit .env to set API_KEY if needed
```

### User Permissions
User must be in these groups for hardware access:
```bash
sudo usermod -a -G audio,video,gpio thuongvv
# Logout and login again for changes to take effect
```

## API Integration

**Environment Variable:** `API_KEY` (not API_URL)
**Default Value:** `http://203.162.88.105/pvlm-api`

### Endpoint Details

**POST /audio/transcribe**
- Input: Multipart file upload, key="file", audio/wav
- Output: JSON `{"text": "..."}` or `{"transcription": "..."}`

**POST /image/analyze-image**
- Input: Multipart file upload, key="file", image/jpeg
- Output: JSON `{"description": "..."}` or `{"analysis": "..."}`

**POST /tts/generate**
- Input: JSON `{"text": "..."}`
- Output: Binary WAV audio OR JSON with `{"audio": "url or base64"}`

The llm_client handles multiple response formats automatically.

## Key Implementation Constraints

### Hardware Requirements (From Spec)
- **Camera:** MUST use `rpicam-jpeg` command-line tool (not picamera library)
- **Audio Sample Rate:** MUST be 16kHz mono
- **Button:** MUST be GPIO pin 17 BCM mode
- **Playback:** Primary tool MUST be `aplay`, PyAudio is fallback only

### Code Style (From Spec)
- Important sections marked with `IMPORTANT:` comment prefix
- No emojis in code or documentation
- Modular organization (one feature per file)
- Professional, clean, maintainable code

### Configuration (From Spec)
- API base URL MUST NOT be hardcoded in modules
- All configuration centralized in config.py
- Environment variable for API endpoint

## Common Development Tasks

### Adding New API Endpoints
1. Add endpoint to `API_ENDPOINTS` dict in config.py
2. Add method to LLMClient class in llm_client.py
3. Follow existing pattern: file upload for audio/image, JSON for text

### Modifying Hardware Configuration
All hardware parameters are in config.py:
- `AUDIO_CONFIG` - Sample rate, channels, format
- `BUTTON_CONFIG` - GPIO pin, debounce timing
- `IMAGE_CONFIG` - Quality, timeout, tool command
- `PLAYBACK_CONFIG` - Primary/fallback tools

### Adjusting Response Generation
The `_generate_response()` method in main.py combines transcription and image analysis. This is where you'd implement more sophisticated prompt engineering or context handling.

### Debugging Component Issues
Each module has a `.cleanup()` method for proper resource cleanup. Main system catches KeyboardInterrupt and calls cleanup on all components. Check logs/system.log for detailed execution trace.

## File Locations

- **Recorded Audio:** `audio/recording_YYYYMMDD_HHMMSS.wav`
- **Captured Images:** `images/capture_YYYYMMDD_HHMMSS.jpg`
- **TTS Responses:** `audio/response_YYYYMMDD_HHMMSS.wav`
- **System Logs:** `logs/system.log`

These directories are auto-created by config.py on import.

## Systemd Service Deployment

Template service file is provided in `disability-support.service`. To deploy:

```bash
sudo cp disability-support.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable disability-support.service
sudo systemctl start disability-support.service
```

Service runs as user `thuongvv` and auto-restarts on failure.

## Troubleshooting

### GPIO Button Not Working in Virtual Environment

**Symptom:** Button works when running Python outside venv, but fails with "Failed to add edge detection" error inside venv.

**Root Cause:** RPi.GPIO installed via pip in the venv doesn't have proper permissions to access `/dev/gpiomem`. The system-installed `python3-rpi.gpio` package has the necessary permissions.

**Solution:** Use the system-installed RPi.GPIO package instead of pip-installed version.

**Quick Fix:**
```bash
./fix_gpio.sh
```
This script will:
1. Install system RPi.GPIO package via apt
2. Recreate venv with `--system-site-packages` flag
3. Reinstall dependencies
4. Test GPIO access

**Manual Fix:**
```bash
# Install system package
sudo apt install python3-rpi.gpio

# Recreate venv with system site packages
rm -rf venv
python3 -m venv --system-site-packages venv

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**Prevention:** New installations using the updated `install.sh` will automatically use the correct setup.

### Other Common Issues

**PyAudio Installation Fails:**
```bash
# Use system package instead of pip
sudo apt install python3-pyaudio
```

**Camera Not Detected:**
```bash
# Enable camera interface
sudo raspi-config
# Navigate to Interface Options > Camera > Enable
```

**Permission Denied Errors:**
```bash
# Add user to necessary groups
sudo usermod -a -G audio,video,gpio $USER
# Logout and login for changes to take effect
```

## Critical Notes for Code Modifications

1. **API Environment Variable:** The code uses `os.getenv("API_KEY")` not `os.getenv("API_URL")`. This is intentional per the spec requirement.

2. **Threading:** Audio recording uses a background thread. Ensure proper thread cleanup in stop_recording() before exiting.

3. **GPIO Cleanup:** Always call `GPIO.cleanup()` on shutdown to release GPIO resources. The main system handles this via signal handlers.

4. **Subprocess Timeouts:** Camera and playback use subprocess.run() with timeouts. These prevent hangs if hardware is unresponsive.

5. **Graceful Degradation:** Button and GPIO modules check if hardware is available and log warnings rather than failing. This allows testing on non-Pi systems.

6. **State Management:** The main system uses `is_recording` and `is_processing` flags to prevent race conditions from button presses during processing.
