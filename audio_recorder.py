"""
Audio recording module for ReSpeaker 2-Microphone HAT.

Captures audio from ReSpeaker microphone array and saves as WAV files.
"""

import logging
import threading
import wave
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import pyaudio
except ImportError:
    pyaudio = None

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Handles audio recording from ReSpeaker device."""

    # Audio configuration
    AUDIO_FORMAT = pyaudio.paInt16 if pyaudio else None
    CHANNELS = 2
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    RESPEAKER_DEVICE_INDEX = 2  # ReSpeaker USB device index

    def __init__(self, output_dir: str = "/home/pi/recordings"):
        """
        Initialize audio recorder.

        Args:
            output_dir: Directory to save audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.recording = False
        self.frames = []
        self.stream = None
        self.audio = None
        self.thread = None

    def start_recording(self) -> str:
        """
        Start audio recording in a separate thread.

        Returns:
            Filename of the recording
        """
        if self.recording:
            logger.warning("Recording already in progress")
            return ""

        self.recording = True
        self.frames = []

        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_file = self.output_dir / f"audio_{timestamp}.wav"

        logger.info(f"Starting audio recording: {self.current_file}")

        # Start recording in separate thread to avoid blocking
        self.thread = threading.Thread(target=self._record_audio, daemon=False)
        self.thread.start()

        return str(self.current_file)

    def stop_recording(self) -> Optional[str]:
        """
        Stop audio recording and save to file.

        Returns:
            Path to saved audio file, or None if failed
        """
        if not self.recording:
            logger.warning("No recording in progress")
            return None

        self.recording = False

        # Wait for recording thread to complete
        if self.thread:
            self.thread.join(timeout=5.0)

        # Save the audio file
        try:
            if self.frames:
                with wave.open(str(self.current_file), "wb") as wav_file:
                    wav_file.setnchannels(self.CHANNELS)
                    wav_file.setsampwidth(
                        self.audio.get_sample_size(self.AUDIO_FORMAT)
                    )
                    wav_file.setframerate(self.SAMPLE_RATE)
                    wav_file.writeframes(b"".join(self.frames))

                logger.info(
                    f"Audio saved successfully: {self.current_file} "
                    f"({len(self.frames)} frames)"
                )
                return str(self.current_file)
            else:
                logger.warning("No audio frames recorded")
                return None
        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            return None
        finally:
            self._cleanup_stream()

    def _record_audio(self) -> None:
        """Internal method to record audio in thread."""
        try:
            if not pyaudio:
                logger.error("PyAudio not available")
                return

            self.audio = pyaudio.PyAudio()

            # Open stream from ReSpeaker device
            self.stream = self.audio.open(
                format=self.AUDIO_FORMAT,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                input_device_index=self.RESPEAKER_DEVICE_INDEX,
                frames_per_buffer=self.CHUNK_SIZE,
            )

            logger.debug("Audio stream opened")

            # Record audio chunks
            while self.recording:
                try:
                    data = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                    self.frames.append(data)
                except Exception as e:
                    logger.error(f"Error reading audio chunk: {e}")
                    break

        except Exception as e:
            logger.error(f"Audio recording error: {e}")
        finally:
            self._cleanup_stream()

    def _cleanup_stream(self) -> None:
        """Clean up audio stream resources."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None

            if self.audio:
                self.audio.terminate()
                self.audio = None

            logger.debug("Audio stream cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up audio stream: {e}")

    def is_recording(self) -> bool:
        """Check if audio is currently recording."""
        return self.recording
