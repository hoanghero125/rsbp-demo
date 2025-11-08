"""
LLM API client for processing audio and images.

Handles STT (Speech-to-Text), image analysis, and TTS (Text-to-Speech).
"""

import base64
import logging
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with the LLM API."""

    def __init__(self, base_url: str = "http://203.162.88.105/pvlm-api"):
        """
        Initialize LLM client.

        Args:
            base_url: Base URL for LLM API
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = 30

    def transcribe_audio(self, audio_file: str) -> Optional[str]:
        """
        Transcribe audio file to text using STT.

        Args:
            audio_file: Path to audio file

        Returns:
            Transcribed text, or None if failed
        """
        if not requests:
            logger.error("requests library not available")
            return None

        try:
            audio_path = Path(audio_file)
            if not audio_path.exists():
                logger.error(f"Audio file not found: {audio_file}")
                return None

            logger.info(f"Transcribing audio: {audio_file}")

            # Prepare file for upload
            with open(audio_path, "rb") as f:
                files = {"file": f}
                response = requests.post(
                    f"{self.base_url}/audio/transcribe",
                    files=files,
                    timeout=self.timeout,
                )

            response.raise_for_status()
            result = response.json()

            # Extract transcribed text
            text = result.get("text", "")
            if text:
                logger.info(f"Transcription successful: {text}")
                return text
            else:
                logger.warning("Empty transcription result")
                return None

        except requests.exceptions.Timeout:
            logger.error("STT request timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"STT API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    def analyze_image(self, image_file: str, question: str = "") -> Optional[str]:
        """
        Analyze image using LLM.

        Args:
            image_file: Path to image file
            question: Optional question about the image

        Returns:
            Image analysis description, or None if failed
        """
        if not requests:
            logger.error("requests library not available")
            return None

        try:
            image_path = Path(image_file)
            if not image_path.exists():
                logger.error(f"Image file not found: {image_file}")
                return None

            logger.info(f"Analyzing image: {image_file}")

            # Prepare image for upload
            with open(image_path, "rb") as f:
                files = {"image": f}
                data = {}
                if question:
                    data["question"] = question

                response = requests.post(
                    f"{self.base_url}/image/analyze-image",
                    files=files,
                    data=data,
                    timeout=self.timeout,
                )

            response.raise_for_status()
            result = response.json()

            # Extract analysis result
            analysis = result.get("description") or result.get("analysis") or result.get("result", "")
            if analysis:
                logger.info(f"Image analysis successful")
                return analysis
            else:
                logger.warning("Empty image analysis result")
                return None

        except requests.exceptions.Timeout:
            logger.error("Image analysis request timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Image analysis API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return None

    def generate_tts(self, text: str, output_file: str) -> Optional[str]:
        """
        Generate speech from text using TTS.

        Args:
            text: Text to convert to speech
            output_file: Path to save audio file

        Returns:
            Path to saved TTS audio file, or None if failed
        """
        if not requests:
            logger.error("requests library not available")
            return None

        try:
            if not text:
                logger.warning("Empty text for TTS")
                return None

            logger.info(f"Generating TTS audio")

            payload = {"text": text}

            response = requests.post(
                f"{self.base_url}/tts/generate",
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            # Save audio content to file
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(response.content)

            logger.info(f"TTS audio saved: {output_file}")
            return str(output_path)

        except requests.exceptions.Timeout:
            logger.error("TTS request timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS API error: {e}")
            return None
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            return None

    def process_user_input(
        self,
        audio_file: str,
        image_file: str,
    ) -> Optional[str]:
        """
        Process user input: transcribe audio and analyze image together.

        Args:
            audio_file: Path to user's audio question
            image_file: Path to captured image

        Returns:
            LLM response text, or None if failed
        """
        try:
            logger.info("Processing user input with audio and image")

            # Transcribe audio to get the question
            question = self.transcribe_audio(audio_file)
            if not question:
                logger.error("Failed to transcribe audio")
                return None

            logger.info(f"User question: {question}")

            # Analyze image with the question context
            image_analysis = self.analyze_image(image_file, question)
            if not image_analysis:
                logger.error("Failed to analyze image")
                return None

            logger.info("User input processing complete")
            return f"Question: {question}\n\nImage Analysis: {image_analysis}"

        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return None
