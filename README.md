# Disability Support System

A Raspberry Pi-based audio recording and image capture system that provides voice-based interaction support for users. The system processes audio questions and visual context through an LLM API to generate helpful responses.

## System Overview

### Hardware Requirements

- **Core Compute**: Raspberry Pi 3 Model B+ (or later)
- **Audio Input**: ReSpeaker 2-Microphone Raspberry Pi HAT
- **Audio Output**: Compact Mono Speaker (connected to ReSpeaker HAT)
- **Vision Input**: Raspberry Pi Camera Module V3
- **Input Control**: GPIO button on pin 17

### Pipeline Architecture

```
Button pressed
    ↓
[Recording starts] ← User asks question via microphone
    ↓
Button pressed
    ↓
[Recording ends] + [Capture image]
    ↓
[LLM Processing Pipeline]
├─ STT: Transcribe audio to text
├─ Image Analysis: Describe captured image
└─ Generate Response: Combine question and image context
    ↓
[TTS]: Convert text response to speech
    ↓
[Audio Playback]: Play response through speaker
```

## Project Structure

```
rsbp-demo/
├── main.py                 # Main application orchestrator
├── audio_recorder.py       # Audio recording module (ReSpeaker)
├── image_capture.py        # Image capture module (Pi Camera)
├── audio_playback.py       # Audio playback module (Speaker)
├── llm_client.py           # LLM API client (STT, image analysis, TTS)
├── button_handler.py       # GPIO button input handler
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Module Documentation

### audio_recorder.py
Handles audio recording from the ReSpeaker 2-Microphone HAT.

**Key Features:**
- Records 16-bit PCM audio at 16kHz, 2 channels
- Non-blocking recording using separate thread
- Automatic WAV file generation with timestamps
- Exception handling for audio stream errors

**Usage:**
```python
from audio_recorder import AudioRecorder

recorder = AudioRecorder()
audio_file = recorder.start_recording()
# ... perform other operations ...
saved_file = recorder.stop_recording()
```

### image_capture.py
Captures images using rpicam-jpeg command-line tool.

**Key Features:**
- Still image capture from Raspberry Pi Camera Module V3
- Configurable resolution and JPEG quality
- Automatic timestamped filename generation
- Error handling for capture failures

**Usage:**
```python
from image_capture import ImageCapture

camera = ImageCapture()
image_file = camera.capture_image()
# Or with custom options
image_file = camera.capture_image_with_options(width=1920, height=1440, quality=90)
```

### llm_client.py
Client for interacting with the LLM API endpoints.

**Key Features:**
- Speech-to-Text (STT): `/audio/transcribe`
- Image Analysis: `/image/analyze-image`
- Text-to-Speech (TTS): `/tts/generate`
- Error handling and request timeout management

**API Endpoint:** `http://203.162.88.105/pvlm-api`

**Usage:**
```python
from llm_client import LLMClient

client = LLMClient()

# Transcribe audio
text = client.transcribe_audio("audio.wav")

# Analyze image
analysis = client.analyze_image("image.jpg", question="What is this?")

# Generate speech
audio_file = client.generate_tts("Hello world", "output.wav")
```

### audio_playback.py
Handles audio playback through the connected speaker.

**Key Features:**
- Primary playback using ALSA `aplay` command
- Fallback using PyAudio if aplay unavailable
- Blocking and non-blocking playback modes
- Thread-based async playback support

**Usage:**
```python
from audio_playback import AudioPlayback

speaker = AudioPlayback()
speaker.play_audio_file("response.wav", blocking=True)
```

### button_handler.py
Manages GPIO button input for recording control.

**Key Features:**
- GPIO event detection on pin 17
- 500ms debounce time to prevent duplicate triggers
- Callback-based event handling
- Automatic GPIO cleanup

**Usage:**
```python
from button_handler import ButtonHandler

def on_button_press():
    print("Button pressed!")

handler = ButtonHandler(on_button_press=on_button_press)
handler.initialize()
```

### main.py
Main application orchestrator that coordinates all system components.

**Key Responsibilities:**
- System initialization and hardware setup
- Button press event handling
- Recording state management
- LLM processing pipeline coordination
- Error handling and graceful shutdown

**State Machine:**
- **Idle**: Waiting for button press
- **Recording**: Capturing user's audio question
- **Processing**: Running LLM pipeline (STT → Image Analysis → TTS)
- **Playback**: Playing response to user

## Installation

### Prerequisites

1. **Raspberry Pi OS** with GPIO access
2. **ReSpeaker 2-Microphone HAT** properly installed and configured
3. **Raspberry Pi Camera Module V3** connected and enabled
4. **rpicam-jpeg** command-line tool installed

### Setup Steps

1. **Clone the repository:**
```bash
git clone <repository-url>
cd rsbp-demo
```

2. **Install Python dependencies:**
```bash
sudo pip install -r requirements.txt
```

3. **Configure ReSpeaker (if not already done):**
```bash
sudo apt-get update
sudo apt-get install git
git clone https://github.com/respeaker/seeed-voicecard.git
cd seeed-voicecard
sudo ./install.sh
sudo reboot
```

4. **Enable Raspberry Pi Camera:**
```bash
sudo raspi-config
# Navigate to Interface Options → Camera → Enable
sudo reboot
```

5. **Create recording directories:**
```bash
mkdir -p /home/pi/recordings
mkdir -p /home/pi/Pictures
```

## Running the Application

### Basic Startup

```bash
# Run with default configuration
python main.py
```

### With Logging

The application logs to both console and `/var/log/rsbp_system.log`:

```bash
# Monitor logs in real-time
tail -f /var/log/rsbp_system.log
```

### Operational Instructions

1. Press the GPIO button to start recording
2. Speak your question clearly into the microphone
3. Press the button again to stop recording
4. System captures an image and processes with LLM
5. Response is played back through the speaker

## API Integration

### LLM API Endpoints

All requests go to: `http://203.162.88.105/pvlm-api`

#### STT (Speech-to-Text)
- **Endpoint**: `/audio/transcribe`
- **Method**: POST
- **Input**: Audio file (WAV format)
- **Output**: JSON with `text` field

#### Image Analysis
- **Endpoint**: `/image/analyze-image`
- **Method**: POST
- **Input**: Image file + optional question
- **Output**: JSON with analysis description

#### TTS (Text-to-Speech)
- **Endpoint**: `/tts/generate`
- **Method**: POST
- **Input**: JSON with `text` field
- **Output**: Binary audio data (WAV format)

## File Storage

### Audio Recordings
- **Path**: `/home/pi/recordings/`
- **Naming**: `audio_YYYYMMDD_HHMMSS.wav`
- **Format**: WAV, 16-bit PCM, 16kHz, 2 channels

### Captured Images
- **Path**: `/home/pi/Pictures/`
- **Naming**: `recording_YYYYMMDD_HHMMSS.jpg`
- **Format**: JPEG

### TTS Output
- **Path**: `/tmp/`
- **Naming**: `response_YYYYMMDD_HHMMSS.wav`

## Error Handling

The system implements comprehensive error handling:

- **Audio Recording Errors**: Logged and reported to user
- **Image Capture Failures**: Graceful fallback with user notification
- **API Timeouts**: 30-second timeout with error messages
- **GPIO Errors**: Safe initialization checks
- **File I/O Errors**: Exception handling and recovery

All errors are logged to the system log file for debugging.

## Troubleshooting

### Audio Issues

**ReSpeaker not detected:**
```bash
# Check audio devices
arecord -l
aplay -l
```

**Low audio quality:**
- Check microphone alignment
- Ensure proper ReSpeaker HAT connection
- Adjust gain settings in ReSpeaker configuration

### Camera Issues

**Camera not found:**
```bash
# Enable camera interface
sudo raspi-config
# Enable camera in Interface Options
```

**Image capture failures:**
- Check camera ribbon cable connection
- Verify rpicam-jpeg installation: `which rpicam-jpeg`

### API Connection Issues

**Cannot reach LLM API:**
```bash
# Test connectivity
curl http://203.162.88.105/pvlm-api/audio/transcribe
```

**Timeout errors:**
- Check network connectivity
- Verify API endpoint availability
- Check system log: `/var/log/rsbp_system.log`

### GPIO Button Not Responding

**Check button connection:**
```bash
# Monitor GPIO input
gpio readall
```

**Test button manually:**
```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
while True:
    print(GPIO.input(17))
```

## Performance Considerations

- **Memory**: System runs comfortably on Pi 3B+ with ~150MB RAM usage
- **Processing Time**: LLM API requests typically take 5-30 seconds
- **Audio Quality**: 16kHz sample rate provides good balance between quality and bandwidth
- **Storage**: Each recording varies; typical hour of audio ≈ 57MB WAV file

## Security Considerations

- Audio files and images stored locally on Raspberry Pi
- API communication over HTTP (consider HTTPS in production)
- GPIO access requires appropriate user permissions
- Implement access controls for sensitive environments

## Development and Debugging

### Enable Debug Logging

Edit `main.py` and change logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Modules

```bash
# Test audio recording
python -c "from audio_recorder import AudioRecorder; r = AudioRecorder(); print('AudioRecorder OK')"

# Test image capture
python -c "from image_capture import ImageCapture; c = ImageCapture(); print('ImageCapture OK')"

# Test LLM client
python -c "from llm_client import LLMClient; c = LLMClient(); print('LLMClient OK')"
```

## License

This project is provided as-is for disability support assistance.

## Support

For issues, questions, or improvements, please refer to the project repository.
