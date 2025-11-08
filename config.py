"""
Configuration module for Disability Support System.

Centralized configuration for all system parameters.
"""

# IMPORTANT: Audio Configuration
AUDIO_CONFIG = {
    "format": "pcm16",  # 16-bit PCM
    "channels": 2,
    "sample_rate": 16000,  # 16kHz
    "chunk_size": 1024,
    "respeaker_device_index": 2,
}

# IMPORTANT: Recording Configuration
RECORDING_CONFIG = {
    "output_dir": "/home/pi/recordings",
    "file_prefix": "audio",
}

# IMPORTANT: Image Capture Configuration
IMAGE_CONFIG = {
    "output_dir": "/home/pi/Pictures",
    "file_prefix": "recording",
    "width": 1920,
    "height": 1440,
    "quality": 90,
    "timeout_ms": 1000,
}

# IMPORTANT: GPIO Button Configuration
BUTTON_CONFIG = {
    "pin": 17,
    "debounce_time_ms": 500,
}

# IMPORTANT: LLM API Configuration
LLM_API_CONFIG = {
    "base_url": "http://203.162.88.105/pvlm-api",
    "timeout_seconds": 30,
    "endpoints": {
        "transcribe": "/audio/transcribe",
        "analyze_image": "/image/analyze-image",
        "tts": "/tts/generate",
    },
}

# IMPORTANT: Audio Playback Configuration
PLAYBACK_CONFIG = {
    "primary_method": "aplay",  # Use aplay command first
    "fallback_method": "pyaudio",  # Fallback to PyAudio
    "respeaker_device_index": 2,
    "chunk_size": 1024,
}

# IMPORTANT: Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "log_file": "/var/log/rsbp_system.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
}

# IMPORTANT: System Configuration
SYSTEM_CONFIG = {
    "enable_logging": True,
    "enable_gpio": True,
    "enable_api": True,
    "startup_delay_ms": 100,
    "shutdown_timeout_ms": 5000,
}


class Config:
    """Configuration management class."""

    @staticmethod
    def get_audio_config():
        """Get audio configuration."""
        return AUDIO_CONFIG

    @staticmethod
    def get_recording_config():
        """Get recording configuration."""
        return RECORDING_CONFIG

    @staticmethod
    def get_image_config():
        """Get image capture configuration."""
        return IMAGE_CONFIG

    @staticmethod
    def get_button_config():
        """Get button configuration."""
        return BUTTON_CONFIG

    @staticmethod
    def get_llm_api_config():
        """Get LLM API configuration."""
        return LLM_API_CONFIG

    @staticmethod
    def get_playback_config():
        """Get audio playback configuration."""
        return PLAYBACK_CONFIG

    @staticmethod
    def get_logging_config():
        """Get logging configuration."""
        return LOGGING_CONFIG

    @staticmethod
    def get_system_config():
        """Get system configuration."""
        return SYSTEM_CONFIG
