"""
Configuration module for the Disability Support System.
Centralizes all system settings, hardware parameters, and API endpoints.
"""

import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded .env file from: {env_path}")
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables only.")

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# IMPORTANT: Data directories for storing audio, images, and logs
AUDIO_DIR = BASE_DIR / "audio"
IMAGE_DIR = BASE_DIR / "images"
LOG_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
AUDIO_DIR.mkdir(exist_ok=True)
IMAGE_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# IMPORTANT: API Configuration - loaded from environment variable or .env file
API_BASE_URL = os.getenv("API_KEY")

# API Endpoints
API_ENDPOINTS = {
    "transcribe": f"{API_BASE_URL}/audio/transcribe",
    "analyze_image": f"{API_BASE_URL}/image/analyze-image",
    "tts": f"{API_BASE_URL}/tts/generate"
}

# API Settings
API_TIMEOUT = 30  # seconds

# IMPORTANT: Audio Recording Configuration
AUDIO_CONFIG = {
    "sample_rate": 16000,  # 16 kHz as specified
    "channels": 1,  # Mono
    "format": "paInt16",  # 16-bit PCM
    "chunk_size": 1024,
    "device_index": None,  # Will auto-detect ReSpeaker HAT
}

# IMPORTANT: GPIO Button Configuration
BUTTON_CONFIG = {
    "pin": 17,  # BCM pin 17
    "debounce_ms": 500,  # 500 milliseconds
}

# IMPORTANT: Image Capture Configuration
IMAGE_CONFIG = {
    "tool": "rpicam-jpeg",
    "quality": 100,
    "timeout_ms": 1000,
    "format": "jpeg",
}

# IMPORTANT: Audio Playback Configuration
PLAYBACK_CONFIG = {
    "tool": "aplay",  # Primary: ALSA aplay
    "fallback": "pyaudio",  # Fallback: PyAudio
}

# Logging Configuration
LOG_CONFIG = {
    "file": LOG_DIR / "system.log",
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}

# File naming patterns
FILE_PATTERNS = {
    "audio_recording": "recording_{timestamp}.wav",
    "captured_image": "capture_{timestamp}.jpg",
    "tts_audio": "response_{timestamp}.wav",
}

# System state
SYSTEM_STATE = {
    "recording": False,
    "processing": False,
}
