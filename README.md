# Disability Support System

A voice and vision-based assistance system for Raspberry Pi that helps disabled individuals by processing audio questions and visual context through AI-powered APIs.

## System Overview

This system provides an accessible interface for users to:
1. Ask questions via voice input
2. Capture visual context via camera
3. Receive spoken responses combining both inputs

### Hardware Requirements

- Raspberry Pi 3 Model B+ (or newer)
- ReSpeaker 2-Microphone Raspberry Pi HAT
- Raspberry Pi Camera Module V3
- Compact Mono Speaker (connected to ReSpeaker HAT)
- GPIO Button (connected to GPIO pin 17)

## System Pipeline

1. **User presses button** - Recording starts
2. **User speaks question** - Audio is captured
3. **User presses button again** - Recording stops, image captured
4. **System processes**:
   - Audio transcribed to text (STT API)
   - Image analyzed for context (Vision API)
   - Response generated combining both inputs
   - Response converted to speech (TTS API)
5. **System plays response** - User hears the answer

## Installation

### 1. System Prerequisites

Ensure your Raspberry Pi has the following installed:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install python3 python3-pip -y

# Install audio tools
sudo apt install alsa-utils portaudio19-dev -y

# Install camera tools
sudo apt install rpicam-apps -y

# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
```

### 2. Clone and Setup

```bash
# Navigate to home directory
cd /home/thuongvv

# Clone or copy the project
cd rsbp-demo

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip3 install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit if needed (default API URL is already set)
nano .env
```

### 4. Test the System

```bash
# Run comprehensive tests
python3 test_modules.py
```

This will verify:
- All modules import correctly
- Hardware components are accessible
- API connectivity
- Directory structure

### 5. Test Hardware (Without API)

Before testing with the API, verify all hardware is working:

```bash
# Activate virtual environment
source venv/bin/activate

# Run interactive hardware test
python3 test_hardware.py
```

This interactive tool lets you test:
- **Camera** - Capture test images
- **Microphone** - Record audio clips
- **Speaker** - Play back recorded audio
- **Button** - Test GPIO button input
- **Complete Workflow** - Test all components together

You can run individual tests or all tests at once. This is useful for:
- Verifying hardware connections before API is ready
- Debugging hardware issues
- Testing after setup changes

## Usage

### Running the System

```bash
# Make sure you're in the project directory
cd /home/thuongvv/rsbp-demo

# Activate virtual environment (if using one)
source venv/bin/activate

# Run the main program
python3 main.py
```

### Using the System

1. Wait for "System is ready" message
2. Press the button to start recording
3. Speak your question clearly
4. Press the button again to stop recording and capture image
5. Wait for the system to process (you'll see log messages)
6. Listen to the spoken response
7. Repeat from step 2 for next question

### Stopping the System

Press `Ctrl+C` to gracefully shutdown the system.

## Module Structure

- `config.py` - Centralized configuration and settings
- `audio_recorder.py` - Audio input from ReSpeaker HAT
- `image_capture.py` - Camera image capture using rpicam-jpeg
- `llm_client.py` - API communication (STT, Vision, TTS)
- `audio_playback.py` - Audio output via speaker
- `button_handler.py` - GPIO button control
- `main.py` - System orchestrator and main loop
- `test_modules.py` - Comprehensive testing suite

## API Endpoints

The system communicates with a centralized LLM API:

- **Base URL**: `http://203.162.88.105/pvlm-api`
- **STT Endpoint**: `/audio/transcribe` - Converts audio to text
- **Vision Endpoint**: `/image/analyze-image` - Analyzes images
- **TTS Endpoint**: `/tts/generate` - Converts text to speech

## Troubleshooting

### Audio Recording Issues

```bash
# List audio devices
aplay -l
arecord -l

# Test microphone
arecord -D plughw:2,0 -f S16_LE -r 16000 test.wav -d 3
aplay test.wav
```

### Camera Issues

```bash
# Test camera
rpicam-jpeg -o test.jpg --timeout 1000

# Check if camera is enabled
vcgencmd get_camera
```

### GPIO Issues

```bash
# Check GPIO access
gpio readall

# Ensure user is in gpio group
sudo usermod -a -G gpio $USER
```

### API Connection Issues

```bash
# Test API connectivity
curl http://203.162.88.105/pvlm-api

# Check network connection
ping 203.162.88.105
```

## Logs

System logs are stored in `logs/system.log` and provide detailed information about:
- Component initialization
- Button press events
- Recording status
- API calls and responses
- Errors and exceptions

View logs in real-time:
```bash
tail -f logs/system.log
```

## Running as a Service

To run the system automatically on boot:

```bash
# Create systemd service file
sudo nano /etc/systemd/system/disability-support.service
```

Add the following content (adjust paths as needed):

```ini
[Unit]
Description=Disability Support System
After=network.target sound.target

[Service]
Type=simple
User=thuongvv
WorkingDirectory=/home/thuongvv/rsbp-demo
Environment="PATH=/home/thuongvv/rsbp-demo/venv/bin"
ExecStart=/home/thuongvv/rsbp-demo/venv/bin/python3 /home/thuongvv/rsbp-demo/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable disability-support.service

# Start the service
sudo systemctl start disability-support.service

# Check status
sudo systemctl status disability-support.service

# View logs
sudo journalctl -u disability-support.service -f
```

## Development

### Adding New Features

The modular design makes it easy to extend functionality:
- Add new API endpoints in `llm_client.py`
- Modify response generation in `main.py`
- Adjust audio/image settings in `config.py`

### Testing Changes

Always run the test suite after making changes:

```bash
python3 test_modules.py
```

## Technical Specifications

- **Audio**: 16kHz, Mono, 16-bit PCM WAV
- **Button**: GPIO pin 17 (BCM), 500ms debounce
- **Camera**: Max resolution JPEG, quality 100
- **API Timeout**: 30 seconds
- **Playback**: aplay (ALSA) primary, PyAudio fallback

## License

This project is designed for educational and assistive purposes.

## Support

For issues or questions, check:
1. System logs in `logs/system.log`
2. Test output from `test_modules.py`
3. Hardware connections and configuration

## Credits

Built for supporting disabled individuals with voice and vision-based AI assistance.
