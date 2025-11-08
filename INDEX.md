# Project File Index - Disability Support System

Complete guide to all files in the project.

## Quick Navigation

- **Getting Started**: [QUICKSTART.md](QUICKSTART.md)
- **Full Documentation**: [README.md](README.md)
- **Development Guide**: [DEVELOPMENT.md](DEVELOPMENT.md)
- **Project Overview**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **This File**: [INDEX.md](INDEX.md)

## File Organization

### Core Application Modules (run on Raspberry Pi)

#### [main.py](main.py) - Main Application Orchestrator (281 lines)
The central coordinator that manages the entire system pipeline.

**Responsibilities:**
- System initialization and shutdown
- Button press event handling
- Recording state management
- LLM processing pipeline coordination
- Error handling and logging

**Key Classes:**
- `DisabilitySupportSystem` - Main orchestrator

**Usage:**
```bash
python3 main.py
```

---

#### [audio_recorder.py](audio_recorder.py) - Audio Recording Module (169 lines)
Handles audio input from the ReSpeaker 2-Microphone HAT.

**Responsibilities:**
- ReSpeaker device initialization
- Audio stream management
- Multi-threaded recording (non-blocking)
- WAV file generation

**Key Classes:**
- `AudioRecorder` - Audio input handler

**Configuration:**
- Device index: 2 (ReSpeaker)
- Sample rate: 16kHz
- Channels: 2 (stereo)
- Format: 16-bit PCM

**Usage:**
```python
from audio_recorder import AudioRecorder
recorder = AudioRecorder()
file = recorder.start_recording()
saved = recorder.stop_recording()
```

---

#### [image_capture.py](image_capture.py) - Image Capture Module (131 lines)
Captures still images from the Raspberry Pi Camera Module V3.

**Responsibilities:**
- rpicam-jpeg command execution
- Image file management
- Resolution and quality configuration
- Error handling for capture failures

**Key Classes:**
- `ImageCapture` - Camera control

**Configuration:**
- Default resolution: 1920x1440
- JPEG quality: 90
- Capture timeout: 1 second

**Usage:**
```python
from image_capture import ImageCapture
camera = ImageCapture()
image = camera.capture_image()
```

---

#### [audio_playback.py](audio_playback.py) - Audio Playback Module (168 lines)
Plays audio responses through the connected speaker.

**Responsibilities:**
- ALSA aplay command execution
- PyAudio fallback playback
- Blocking and non-blocking modes
- Thread-based async playback

**Key Classes:**
- `AudioPlayback` - Speaker control

**Configuration:**
- Primary method: aplay
- Fallback method: PyAudio
- Device index: 2 (ReSpeaker)

**Usage:**
```python
from audio_playback import AudioPlayback
speaker = AudioPlayback()
speaker.play_audio_file("response.wav")
```

---

#### [llm_client.py](llm_client.py) - LLM API Client (234 lines)
Integrates with the external LLM API for STT, image analysis, and TTS.

**Responsibilities:**
- HTTP request handling to LLM API
- Audio file upload and processing
- Image file upload and analysis
- Text-to-speech generation
- Error handling and timeouts

**Key Classes:**
- `LLMClient` - LLM API wrapper

**API Endpoints:**
- Base URL: `http://203.162.88.105/pvlm-api`
- `/audio/transcribe` - Speech-to-Text
- `/image/analyze-image` - Image analysis
- `/tts/generate` - Text-to-Speech

**Configuration:**
- Timeout: 30 seconds
- Request retry: Not implemented (future)
- Caching: Not implemented (future)

**Usage:**
```python
from llm_client import LLMClient
client = LLMClient()
text = client.transcribe_audio("audio.wav")
analysis = client.analyze_image("image.jpg", "What is this?")
audio = client.generate_tts("Hello world", "output.wav")
```

---

#### [button_handler.py](button_handler.py) - GPIO Button Handler (106 lines)
Manages GPIO button input for recording control.

**Responsibilities:**
- GPIO initialization on pin 17
- Button press event detection
- Debounce handling (500ms)
- Callback-based event dispatch
- GPIO resource cleanup

**Key Classes:**
- `ButtonHandler` - Button input handler

**Configuration:**
- GPIO Pin: 17 (BCM)
- Debounce time: 500ms
- Logic: Falling edge (button press)

**Usage:**
```python
from button_handler import ButtonHandler
handler = ButtonHandler(on_button_press=callback_func)
handler.initialize()
```

---

#### [config.py](config.py) - Configuration Management (116 lines)
Centralized configuration for all system components.

**Responsibilities:**
- Configuration constants
- Environment-specific settings
- Easy customization without code changes

**Configuration Sections:**
- `AUDIO_CONFIG` - Audio device settings
- `RECORDING_CONFIG` - Audio file storage
- `IMAGE_CONFIG` - Camera settings
- `BUTTON_CONFIG` - GPIO configuration
- `LLM_API_CONFIG` - API endpoint settings
- `PLAYBACK_CONFIG` - Speaker settings
- `LOGGING_CONFIG` - Logging parameters
- `SYSTEM_CONFIG` - System-wide settings

**Key Classes:**
- `Config` - Static configuration accessor

**Usage:**
```python
from config import Config
audio_cfg = Config.get_audio_config()
api_cfg = Config.get_llm_api_config()
```

---

### Testing & Quality

#### [test_modules.py](test_modules.py) - Test Suite (318 lines)
Comprehensive testing for all system modules.

**Test Functions:**
- `test_imports()` - Module import verification
- `test_config()` - Configuration loading
- `test_audio_recorder()` - Audio recorder initialization
- `test_image_capture()` - Camera initialization
- `test_audio_playback()` - Speaker setup
- `test_llm_client()` - LLM API client
- `test_button_handler()` - GPIO handling
- `test_directories()` - Directory structure

**Usage:**
```bash
python3 test_modules.py
```

**Output:**
- Individual test results with status (✓ PASS / ✗ FAIL)
- Summary of passed/failed tests
- Diagnostic information for troubleshooting

---

#### [requirements.txt](requirements.txt) - Python Dependencies
Lists all required Python packages for production deployment.

**Contents:**
```
RPi.GPIO==0.7.0
pyaudio==0.2.13
requests==2.31.0
```

**Installation:**
```bash
pip3 install -r requirements.txt
```

---

### Deployment & Setup

#### [rsbp-system.service](rsbp-system.service) - systemd Service File
Configuration for running the system as a background service.

**Features:**
- Automatic startup on boot
- Restart on failure
- Resource limiting (512MB RAM, 80% CPU)
- Security hardening
- Journal logging integration

**Management:**
```bash
sudo systemctl start rsbp-system
sudo systemctl stop rsbp-system
sudo systemctl status rsbp-system
sudo systemctl enable rsbp-system    # Autostart on boot
sudo systemctl disable rsbp-system   # Disable autostart
journalctl -u rsbp-system -f         # View logs
```

---

#### [install.sh](install.sh) - Installation Script
Automated installation and setup script for Raspberry Pi.

**Steps Performed:**
1. Update system packages
2. Install Python dependencies
3. Install audio packages (alsa-utils, pulseaudio)
4. Install camera tools
5. Install GPIO library
6. Install Python requirements
7. Create recording directories
8. Copy service files
9. Install ReSpeaker driver
10. Enable service

**Usage:**
```bash
sudo bash install.sh
```

---

### Documentation

#### [README.md](README.md) - Complete System Documentation
Comprehensive guide covering all aspects of the system.

**Sections:**
- System overview and architecture
- Hardware requirements
- Processing pipeline
- Project structure and modules
- Installation and setup
- Running the application
- API integration details
- File storage locations
- Error handling
- Troubleshooting guide
- Performance considerations
- Security notes
- Development and debugging

**Target Audience:** System administrators, operators, integrators

---

#### [QUICKSTART.md](QUICKSTART.md) - Quick Start Guide
Rapid deployment and operation guide.

**Content:**
- Prerequisites checklist
- Automated vs. manual installation
- Testing procedures
- Basic operation steps
- Common troubleshooting solutions
- Configuration customization
- File management
- Performance optimization
- Maintenance tasks
- Safety guidelines

**Target Audience:** New users, operators

---

#### [DEVELOPMENT.md](DEVELOPMENT.md) - Development Guide
Guide for developers extending or maintaining the system.

**Sections:**
- Architecture overview
- Module dependencies
- Code style guide
- Docstring format
- Logging best practices
- Adding new features
- Testing strategies
- Performance optimization
- Debugging techniques
- Error handling patterns
- Future enhancement ideas
- Tools and dependencies
- Version control guidelines

**Target Audience:** Developers, contributors

---

#### [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project Overview
High-level project summary and statistics.

**Content:**
- Build statistics
- Deliverables overview
- System architecture
- Key features
- Configuration reference
- Installation overview
- Testing information
- Performance metrics
- Security considerations
- Maintenance schedule
- Future enhancements
- Success criteria

**Target Audience:** Project managers, stakeholders, reviewers

---

#### [INDEX.md](INDEX.md) - This File
Complete file index with descriptions and usage.

**Content:**
- Navigation guide
- File organization
- Module documentation
- Usage examples
- Configuration reference
- Quick commands

**Target Audience:** All users

---

### Version Control

#### [.gitignore](.gitignore) - Git Ignore Patterns
Excludes unnecessary files from version control.

**Exclusions:**
- Python cache and compiled files
- Virtual environments
- IDE configuration
- Log files
- Audio/image test files
- Local overrides
- Test artifacts

---

## File Statistics

```
Total Files:        15
Total Lines:        ~3,500+ (code + docs)

Code Files:         7 (.py)        1,523 lines
Documentation:      5 (.md)        ~1,500 lines
Configuration:      1 (.py)        116 lines
Deployment:         2 files        (~100 lines)
Test Suite:         1 (.py)        318 lines
Dependencies:       1 (.txt)       3 packages
Version Control:    1 (.gitignore) 65 patterns
```

## Quick Command Reference

### Installation
```bash
sudo bash install.sh
sudo reboot
```

### Testing
```bash
python3 test_modules.py
```

### Running Application
```bash
# Manual
python3 main.py

# As service
sudo systemctl start rsbp-system
```

### Monitoring
```bash
journalctl -u rsbp-system -f
tail -f /var/log/rsbp_system.log
```

### Configuration
```bash
# Edit settings
nano config.py

# Restart service
sudo systemctl restart rsbp-system
```

## Navigation Guide

**For First Time Setup:**
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run installation script
3. Run test suite
4. Start service

**For System Operation:**
1. Check [QUICKSTART.md](QUICKSTART.md) for troubleshooting
2. Monitor logs: `journalctl -u rsbp-system -f`
3. Review configuration in [config.py](config.py)

**For Development:**
1. Read [DEVELOPMENT.md](DEVELOPMENT.md)
2. Review specific module documentation
3. Run tests: `python3 test_modules.py`
4. Check [config.py](config.py) for settings

**For Understanding Architecture:**
1. Review [README.md](README.md) system overview
2. Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. Study module documentation in this INDEX

## Integration Points

### External API
- **LLM Service**: `http://203.162.88.105/pvlm-api`
  - STT, image analysis, TTS

### Hardware Interfaces
- **GPIO**: Pin 17 (button input)
- **Audio Input**: ReSpeaker device (index 2)
- **Audio Output**: ReSpeaker device (index 2)
- **Camera**: Raspberry Pi Camera Module V3

### File System
- **Recordings**: `/home/pi/recordings/`
- **Images**: `/home/pi/Pictures/`
- **Logs**: `/var/log/rsbp_system.log`
- **Temp**: `/tmp/`

## Security Considerations

- GPIO requires elevated permissions
- Store API credentials securely
- Regular backup of recordings
- Monitor system resource usage
- Review logs periodically
- Keep Python packages updated

## Support & Help

1. **Quick Issues**: Check QUICKSTART.md troubleshooting
2. **Logs**: `journalctl -u rsbp-system -n 100`
3. **Tests**: `python3 test_modules.py`
4. **Documentation**: See README.md
5. **Development**: See DEVELOPMENT.md

---

**Last Updated**: November 8, 2025
**Version**: 1.0.0
**Status**: Production Ready
