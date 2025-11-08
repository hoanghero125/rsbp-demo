"""
Audio playback module for speaker output.

Plays audio files through the connected speaker via ReSpeaker HAT.
"""

import logging
import subprocess
import threading
from pathlib import Path
from typing import Optional

try:
    import pyaudio
    import wave
except ImportError:
    pyaudio = None
    wave = None

logger = logging.getLogger(__name__)


class AudioPlayback:
    """Handles audio playback through speaker."""

    # Audio configuration
    RESPEAKER_DEVICE_INDEX = 2  # ReSpeaker output device index
    CHUNK_SIZE = 1024

    def __init__(self):
        """Initialize audio playback handler."""
        self.is_playing = False
        self.thread = None

    def play_audio_file(self, audio_file: str, blocking: bool = True) -> bool:
        """
        Play audio file through speaker.

        Args:
            audio_file: Path to audio file to play
            blocking: If True, wait for playback to complete

        Returns:
            True if playback started successfully, False otherwise
        """
        audio_path = Path(audio_file)
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_file}")
            return False

        if self.is_playing:
            logger.warning("Audio already playing, queueing next playback")

        logger.info(f"Playing audio: {audio_file}")

        if blocking:
            return self._play_audio_direct(audio_file)
        else:
            self.thread = threading.Thread(
                target=self._play_audio_direct, args=(audio_file,), daemon=True
            )
            self.thread.start()
            return True

    def _play_audio_direct(self, audio_file: str) -> bool:
        """
        Internal method to play audio file directly.

        Args:
            audio_file: Path to audio file

        Returns:
            True if playback succeeded, False otherwise
        """
        try:
            self.is_playing = True

            # Try using aplay (standard ALSA player)
            result = subprocess.run(
                ["aplay", "-D", "default", audio_file],
                capture_output=True,
                timeout=60,
            )

            if result.returncode == 0:
                logger.info(f"Audio playback completed: {audio_file}")
                return True
            else:
                logger.error(f"aplay failed: {result.stderr.decode()}")
                # Try fallback method
                return self._play_audio_pyaudio(audio_file)

        except FileNotFoundError:
            logger.warning("aplay not found, trying PyAudio")
            return self._play_audio_pyaudio(audio_file)
        except subprocess.TimeoutExpired:
            logger.error("Audio playback timeout")
            return False
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            return False
        finally:
            self.is_playing = False

    def _play_audio_pyaudio(self, audio_file: str) -> bool:
        """
        Play audio using PyAudio (fallback method).

        Args:
            audio_file: Path to audio file

        Returns:
            True if playback succeeded, False otherwise
        """
        if not pyaudio or not wave:
            logger.error("PyAudio not available for fallback playback")
            return False

        try:
            with wave.open(audio_file, "rb") as wav_file:
                # Get audio parameters
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()

                # Open output stream
                audio = pyaudio.PyAudio()
                stream = audio.open(
                    format=audio.get_format_from_width(sample_width),
                    channels=n_channels,
                    rate=frame_rate,
                    output=True,
                    output_device_index=self.RESPEAKER_DEVICE_INDEX,
                )

                # Play audio in chunks
                data = wav_file.readframes(self.CHUNK_SIZE)
                while data:
                    stream.write(data)
                    data = wav_file.readframes(self.CHUNK_SIZE)

                # Clean up
                stream.stop_stream()
                stream.close()
                audio.terminate()

                logger.info(f"Audio playback completed via PyAudio: {audio_file}")
                return True

        except Exception as e:
            logger.error(f"PyAudio playback error: {e}")
            return False

    def stop_playback(self) -> None:
        """Stop current playback if in progress."""
        # Note: Stopping subprocess playback is difficult without process handle
        # This would need to be enhanced with process management
        logger.info("Stop playback requested")

    def wait_until_finished(self) -> None:
        """Wait until current playback finishes (for threaded playback)."""
        if self.thread and self.thread.is_alive():
            self.thread.join()
            logger.debug("Playback thread finished")

    def is_audio_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self.is_playing
