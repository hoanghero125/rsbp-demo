# Disability Support System - Complete Specification

## Original Request

Build a complete system with the main purpose to support disabled individuals. The system must implement a voice and vision-based assistance pipeline that processes user questions through audio and image analysis.

## System Specifications

### Hardware Components

**Core Compute:**
- Raspberry Pi 3 Model B+

**Audio Input:**
- ReSpeaker 2-Microphone Raspberry Pi HAT
- Reference Documentation: https://wiki.seeedstudio.com/respeaker_2_mics_pi_hat_raspberry_v2/

**Audio Output:**
- Compact Mono Speaker (plugged directly into ReSpeaker 2-Microphone HAT)

**Vision Input:**
- Raspberry Pi Camera Module V3

**Control Input:**
- GPIO Button (for triggering recording start/stop)

## System Pipeline

The complete system pipeline operates in the following sequence:

```
1. User Action: Button Pressed (First Press)
   └─> Recording Starts
       └─> System begins capturing user's spoken question via ReSpeaker microphone
           └─> User speaks their question/request into the microphone
               └─> Audio is continuously recorded to file

2. User Action: Button Pressed (Second Press)
   └─> Recording Stops
       └─> Image Capture Triggered Simultaneously
           └─> Still image taken from Raspberry Pi Camera Module V3
               └─> Image saved to storage

3. LLM Processing Begins
   └─> Speech-to-Text (STT) Processing
       └─> Audio file from step 1 converted to text transcription
           └─> API Call: /audio/transcribe
               └─> Returns: Text transcription of user's question

   └─> Image Analysis
       └─> Image file from step 2 analyzed for visual context
           └─> API Call: /image/analyze-image
               └─> Returns: Description/analysis of image content

4. LLM Response Generation
   └─> Combined Processing
       └─> Transcription + Image Analysis → LLM generates response
           └─> System creates text response based on:
               - User's spoken question (from STT)
               - Visual context (from image analysis)

5. Text-to-Speech Conversion
   └─> Response Text → Audio File (.wav)
       └─> API Call: /tts/generate
           └─> Returns: WAV audio file of synthesized response

6. Audio Playback
   └─> Response audio played through speaker
       └─> User hears the system's answer to their question
           └─> Pipeline complete
```

## LLM API Details

### API Base URL (A centralized API endpoint file and .env, don't fixed code into files.)
```
API-KEY=http://203.162.88.105/pvlm-api
```

### Required API Endpoints

#### 1. Speech-to-Text Transcription
- **Endpoint Path:** `/audio/transcribe`
- **HTTP Method:** POST
- **Input:** Audio file (WAV format) from microphone recording
- **Output:** JSON response containing transcribed text
- **Purpose:** Convert user's spoken question into text

#### 2. Image Analysis
- **Endpoint Path:** `/image/analyze-image`
- **HTTP Method:** POST
- **Input:** Image file (JPEG format) from camera
- **Output:** JSON response containing image description/analysis
- **Purpose:** Analyze visual content for context

#### 3. Text-to-Speech Generation
- **Endpoint Path:** `/tts/generate`
- **HTTP Method:** POST
- **Input:** Text response from LLM
- **Output:** Audio file (WAV format) with synthesized speech
- **Purpose:** Convert text response to audio for playback

## Camera Implementation

**Tool Requirement:** rpicam-jpeg (command-line tool for image capture)

- Must use: `rpicam-jpeg` command-line interface
- Captures still images from Raspberry Pi Camera Module V3
- Output format: JPEG

## Code Requirements

### Code Style
- Professional coding style
- Clean, maintainable, well-structured code
- Self-documenting where possible

### Documentation
- Important code sections marked with `IMPORTANT:` prefix in comments
- No emoji in code or documentation
- Clear explanations of critical functionality

### Code Organization
- Separate features into different files for better debugging and organization
- Modular design for reusability
- Clear separation of concerns

### Suggested Module Structure
- `main.py` - System orchestrator
- `audio_recorder.py` - Audio input handling
- `image_capture.py` - Image capture from camera
- `audio_playback.py` - Audio output handling
- `llm_client.py` - API communication
- `button_handler.py` - GPIO button input
- `config.py` - Centralized configuration
- `test_modules.py` - Testing suite

## Deployment Information

### Target System
- **Username:** thuongvv
- **Host:** Raspberry Pi running Raspberry Pi OS
- **Deployment Directory:** `/home/thuongvv/rsbp-demo/`

## Key Technical Specifications

### Audio Configuration
- **Microphone Device:** ReSpeaker 2-Microphone HAT
- **Sample Rate:** 16 kHz (16000 Hz)
- **Channels:** 1 (Mono)
- **Format:** 16-bit PCM
- **Recording Method:** Non-blocking (threaded) for responsiveness
- **Output Format:** WAV file

### Button Configuration
- **GPIO Pin:** 17 (BCM mode)
- **Function:** Toggle recording on/off
- **Debounce:** 500 milliseconds
- **Event Type:** Falling edge (button press)

### Image Configuration
- **Capture Tool:** rpicam-jpeg command-line
- **Default Resolution:** MAX RESOLUTION
- **Output Format:** JPEG
- **Quality:** 100 (configurable)
- **Timeout:** 1000 milliseconds

### API Configuration
- **Base URL:** http://203.162.88.105/pvlm-api
- **Request Timeout:** 30 seconds
- **Protocol:** HTTP REST

### Playback Configuration
- **Output Device:** Speaker (via ReSpeaker HAT)
- **Audio Format:** WAV
- **Playback Method:** Non-blocking (can be blocking if needed)
- **Primary Tool:** aplay (ALSA)
- **Fallback:** PyAudio if aplay unavailable

## System Workflow Summary

### Normal Operation
1. System initializes all components (GPIO, audio, camera, API client)
2. System waits for button press
3. User presses button → Recording starts, system captures audio
4. User presses button again → Recording stops, image captured
5. System calls LLM API:
   - STT: Convert audio → text
   - Image analysis: Analyze visual context
6. LLM generates response text
7. System calls TTS API: Convert response text → audio
8. System plays audio response through speaker
9. Return to step 2: waiting for next button press

### Error Handling
- Graceful fallbacks for missing hardware
- Timeout handling for API calls
- File I/O error handling
- Cleanup on system shutdown

## Dependencies

### Python Packages
- `requests` - HTTP API communication
- `RPi.GPIO` - GPIO button input
- `PyAudio` - Audio input/output
- `wave` - WAV file handling

### System Tools
- `rpicam-jpeg` - Image capture (from rpicam-apps)
- `aplay` - Audio playback (ALSA)
- `python3` - Python runtime

### Hardware Dependencies
- ReSpeaker 2-Microphone HAT (installed and configured)
- Raspberry Pi Camera Module V3 (enabled)
- GPIO button (wired to pin 17)
- Speaker (connected to ReSpeaker HAT)

## Testing Requirements

The system must include a comprehensive test suite that validates:
- All module imports work correctly
- Configuration is properly loaded
- Hardware components are accessible
- Directory structure is correct
- API connectivity
- Individual component functionality

## Logging

System should log:
- Component initialization
- Button press events
- Recording start/stop
- Image capture results
- API calls and responses
- Errors and exceptions
- Processing timestamps

Log files stored in: `/home/thuongvv/rsbp-demo/logs/`

## Service Deployment

System can be deployed as:
1. **Direct execution:** `python3 main.py`
2. **systemd service:** Configured for autostart on boot

## System Features

✓ Voice-controlled assistance system
✓ Real-time audio recording and playback
✓ Image capture and analysis integration
✓ LLM-powered response generation
✓ Accessible interface for users with disabilities
✓ Comprehensive logging and diagnostics
✓ Modular architecture for maintenance
✓ Error handling and recovery
✓ Non-blocking operations for responsiveness

## API Integration Summary

The system communicates with a single LLM API endpoint with three operations:

| Operation | Endpoint | Input | Output |
|-----------|----------|-------|--------|
| Speech-to-Text | /audio/transcribe | WAV audio file | JSON with text field |
| Image Analysis | /image/analyze-image | JPEG image file | JSON with description field |
| Text-to-Speech | /tts/generate | JSON with text | WAV audio file |

## User (Deployment Target)

- **Username:** thuongvv
- **Hostname:** iec
- **System:** Raspberry Pi running Raspberry Pi OS

## Original Request Summary

This specification document captures the complete original requirements for building a Disability Support System for Raspberry Pi that:

1. Accepts voice input via ReSpeaker microphone
2. Captures visual context via Raspberry Pi Camera
3. Processes both through an LLM API (transcription + image analysis)
4. Generates spoken responses
5. Plays audio output through speaker
6. Is controlled via GPIO button

All implementation should follow professional coding standards with important sections clearly marked, no emoji, and modular organization for maintainability and debugging.

All needed drivers have been properly installed. Only need code to use the hardware as needed.