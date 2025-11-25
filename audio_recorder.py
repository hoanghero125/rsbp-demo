"""
Audio Recorder module for the Disability Support System.
Handles audio input from the ReSpeaker 2-Microphone HAT using PyAudio.
"""

import pyaudio
import wave
import threading
import logging
from datetime import datetime
from pathlib import Path

import config

logger = logging.getLogger(__name__)


class AudioRecorder:
    """
    Handles audio recording from the ReSpeaker HAT microphone.
    Uses threaded recording for non-blocking operation.
    """

    def __init__(self):
        """Initialize the audio recorder with configuration from config module."""
        self.audio = None
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.recording_thread = None
        self.output_file = None

        # IMPORTANT: Audio configuration from config module
        self.sample_rate = config.AUDIO_CONFIG["sample_rate"]
        self.channels = config.AUDIO_CONFIG["channels"]
        self.chunk_size = config.AUDIO_CONFIG["chunk_size"]

        # Convert format string to PyAudio constant
        format_str = config.AUDIO_CONFIG["format"]
        self.format = getattr(pyaudio, format_str)

        logger.info("AudioRecorder initialized")

    def initialize(self):
        """
        Initialize PyAudio instance.
        IMPORTANT: Must be called before starting recording.
        """
        try:
            self.audio = pyaudio.PyAudio()
            logger.info("PyAudio initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio: {e}")
            return False

    def _find_respeaker_device(self):
        """
        Find the ReSpeaker device index automatically.
        Returns device index or None if not found.
        """
        if not self.audio:
            return None

        # IMPORTANT: Search for ReSpeaker device in available audio devices
        for i in range(self.audio.get_device_count()):
            dev_info = self.audio.get_device_info_by_index(i)
            name = dev_info.get("name", "").lower()
            if "respeaker" in name or "seeed" in name:
                logger.info(f"Found ReSpeaker device: {dev_info.get('name')} at index {i}")
                return i

        # If not found by name, return default input device
        default_device = self.audio.get_default_input_device_info()
        logger.warning(f"ReSpeaker not found by name, using default: {default_device.get('name')}")
        return default_device.get("index")

    def start_recording(self):
        """
        Start recording audio in a separate thread.
        Returns the output file path if successful, None otherwise.
        """
        if self.is_recording:
            logger.warning("Recording already in progress")
            return None

        try:
            # Generate output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = config.FILE_PATTERNS["audio_recording"].format(timestamp=timestamp)
            self.output_file = config.AUDIO_DIR / filename

            # Find device index
            device_index = config.AUDIO_CONFIG["device_index"]
            if device_index is None:
                device_index = self._find_respeaker_device()

            # IMPORTANT: Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=device_index
            )

            self.frames = []
            self.is_recording = True

            # Start recording in separate thread for non-blocking operation
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()

            logger.info(f"Recording started: {self.output_file}")
            return str(self.output_file)

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False
            return None

    def _record_audio(self):
        """
        Internal method that runs in a separate thread to record audio.
        IMPORTANT: Continuously captures audio chunks until stop_recording is called.
        """
        try:
            while self.is_recording:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
        except Exception as e:
            logger.error(f"Error during recording: {e}")
            self.is_recording = False

    def stop_recording(self):
        """
        Stop recording and save the audio to a WAV file.
        Returns the path to the saved file if successful, None otherwise.
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None

        try:
            # Signal recording thread to stop
            self.is_recording = False

            # Wait for recording thread to finish
            if self.recording_thread:
                self.recording_thread.join(timeout=2.0)

            # Close the stream
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None

            # IMPORTANT: Save recorded audio to WAV file
            if self.frames and self.output_file:
                with wave.open(str(self.output_file), 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(self.audio.get_sample_size(self.format))
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(b''.join(self.frames))

                logger.info(f"Recording saved: {self.output_file}")
                return str(self.output_file)
            else:
                logger.warning("No audio data recorded")
                return None

        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return None

    def cleanup(self):
        """
        Clean up resources and terminate PyAudio.
        IMPORTANT: Should be called when shutting down the system.
        """
        try:
            if self.is_recording:
                self.stop_recording()

            if self.audio:
                self.audio.terminate()
                self.audio = None

            logger.info("AudioRecorder cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def get_status(self):
        """Return current recording status."""
        return {
            "is_recording": self.is_recording,
            "output_file": str(self.output_file) if self.output_file else None
        }
