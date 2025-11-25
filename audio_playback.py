"""
Audio Playback module for the Disability Support System.
Handles audio output to speaker via ReSpeaker HAT using aplay (primary) or PyAudio (fallback).
"""

import subprocess
import logging
from pathlib import Path
import wave

import config

logger = logging.getLogger(__name__)


class AudioPlayback:
    """
    Handles audio playback through the ReSpeaker HAT speaker.
    IMPORTANT: Uses aplay (ALSA) as primary method, PyAudio as fallback.
    """

    def __init__(self):
        """Initialize the audio playback module."""
        self.primary_tool = config.PLAYBACK_CONFIG["tool"]
        self.fallback_tool = config.PLAYBACK_CONFIG["fallback"]
        self.use_fallback = False

        logger.info("AudioPlayback initialized")

    def play_audio(self, audio_file_path, blocking=True):
        """
        Play audio file through the speaker.

        Args:
            audio_file_path: Path to WAV audio file to play
            blocking: If True, wait for playback to complete. If False, play in background.

        Returns:
            True if playback started successfully, False otherwise
        """
        audio_path = Path(audio_file_path)

        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_file_path}")
            return False

        # Try primary method (aplay) first
        if not self.use_fallback:
            success = self._play_with_aplay(audio_path, blocking)
            if success:
                return True
            else:
                logger.warning("aplay failed, trying fallback method")
                self.use_fallback = True

        # Fallback to PyAudio
        return self._play_with_pyaudio(audio_path, blocking)

    def _play_with_aplay(self, audio_path, blocking=True):
        """
        Play audio using aplay (ALSA) command-line tool.
        IMPORTANT: Primary playback method as specified.

        Args:
            audio_path: Path to audio file
            blocking: Whether to wait for completion

        Returns:
            True if successful, False otherwise
        """
        try:
            # IMPORTANT: Build aplay command
            cmd = [self.primary_tool, str(audio_path)]

            logger.info(f"Playing audio with aplay: {audio_path.name}")

            if blocking:
                # Wait for playback to complete
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60  # 60 second timeout
                )

                if result.returncode == 0:
                    logger.info("Audio playback completed successfully")
                    return True
                else:
                    logger.error(f"aplay failed: {result.stderr}")
                    return False
            else:
                # Non-blocking: start playback in background
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logger.info("Audio playback started (non-blocking)")
                return True

        except FileNotFoundError:
            logger.error("aplay command not found")
            return False
        except subprocess.TimeoutExpired:
            logger.error("Audio playback timed out")
            return False
        except Exception as e:
            logger.error(f"Error playing audio with aplay: {e}")
            return False

    def _play_with_pyaudio(self, audio_path, blocking=True):
        """
        Play audio using PyAudio (fallback method).

        Args:
            audio_path: Path to audio file
            blocking: Whether to wait for completion

        Returns:
            True if successful, False otherwise
        """
        try:
            import pyaudio
            import threading

            logger.info(f"Playing audio with PyAudio: {audio_path.name}")

            # IMPORTANT: Open and read WAV file
            with wave.open(str(audio_path), 'rb') as wf:
                # Initialize PyAudio
                p = pyaudio.PyAudio()

                # Open stream
                stream = p.open(
                    format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )

                # Read and play audio data
                chunk_size = 1024
                data = wf.readframes(chunk_size)

                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)

                # Clean up
                stream.stop_stream()
                stream.close()
                p.terminate()

                logger.info("Audio playback completed with PyAudio")
                return True

        except ImportError:
            logger.error("PyAudio not available")
            return False
        except Exception as e:
            logger.error(f"Error playing audio with PyAudio: {e}")
            return False

    def test_playback(self):
        """
        Test if audio playback is working.
        Creates a simple test tone and attempts to play it.

        Returns:
            True if playback system is working, False otherwise
        """
        try:
            # Check if aplay is available
            result = subprocess.run(
                [self.primary_tool, "--version"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                logger.info("aplay is available and working")
                return True
            else:
                logger.warning("aplay test failed")
                return False

        except FileNotFoundError:
            logger.warning("aplay not found, will use PyAudio fallback")
            self.use_fallback = True
            return False
        except Exception as e:
            logger.error(f"Playback test error: {e}")
            return False

    def stop_playback(self):
        """
        Stop any currently playing audio.
        Note: This is a best-effort method and may not work for all playback methods.
        """
        try:
            # Try to kill any running aplay processes
            subprocess.run(
                ["pkill", "-9", "aplay"],
                capture_output=True,
                timeout=2
            )
            logger.info("Stopped playback")
        except Exception as e:
            logger.warning(f"Could not stop playback: {e}")

    def cleanup(self):
        """Cleanup method for consistency with other modules."""
        self.stop_playback()
        logger.info("AudioPlayback cleaned up")
