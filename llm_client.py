"""
LLM Client module for the Disability Support System.
Handles all API communications: Speech-to-Text, Image Analysis, and Text-to-Speech.
"""

import requests
import logging
from pathlib import Path
from datetime import datetime

import config

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Client for communicating with the LLM API.
    IMPORTANT: Handles three main operations:
    1. Speech-to-Text transcription
    2. Image analysis
    3. Text-to-Speech generation
    """

    def __init__(self):
        """Initialize the LLM client with API configuration."""
        self.base_url = config.API_BASE_URL
        self.endpoints = config.API_ENDPOINTS
        self.timeout = config.API_TIMEOUT

        logger.info(f"LLMClient initialized with base URL: {self.base_url}")

    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file to text using Speech-to-Text API.

        Args:
            audio_file_path: Path to WAV audio file

        Returns:
            Transcribed text string if successful, None otherwise
        """
        try:
            audio_path = Path(audio_file_path)
            if not audio_path.exists():
                logger.error(f"Audio file not found: {audio_file_path}")
                return None

            # IMPORTANT: Prepare multipart file upload
            with open(audio_path, 'rb') as audio_file:
                files = {'file': (audio_path.name, audio_file, 'audio/wav')}

                logger.info(f"Sending audio for transcription: {audio_path.name}")

                # Make POST request to transcription endpoint
                response = requests.post(
                    self.endpoints["transcribe"],
                    files=files,
                    timeout=self.timeout
                )

                response.raise_for_status()
                result = response.json()

                # IMPORTANT: Extract transcribed text from response
                # Assuming API returns {"text": "transcribed content"}
                transcription = result.get('text', result.get('transcription', ''))

                if transcription:
                    logger.info(f"Transcription successful: {transcription[:100]}...")
                    return transcription
                else:
                    logger.warning("Transcription returned empty result")
                    return None

        except requests.exceptions.Timeout:
            logger.error("Transcription request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Transcription request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return None

    def analyze_image(self, image_file_path):
        """
        Analyze image using Image Analysis API.

        Args:
            image_file_path: Path to JPEG image file

        Returns:
            Image analysis/description string if successful, None otherwise
        """
        try:
            image_path = Path(image_file_path)
            if not image_path.exists():
                logger.error(f"Image file not found: {image_file_path}")
                return None

            # IMPORTANT: Prepare multipart file upload
            with open(image_path, 'rb') as image_file:
                files = {'file': (image_path.name, image_file, 'image/jpeg')}

                logger.info(f"Sending image for analysis: {image_path.name}")

                # Make POST request to image analysis endpoint
                response = requests.post(
                    self.endpoints["analyze_image"],
                    files=files,
                    timeout=self.timeout
                )

                response.raise_for_status()
                result = response.json()

                # IMPORTANT: Extract image description from response
                # Assuming API returns {"description": "image analysis"}
                description = result.get('description', result.get('analysis', ''))

                if description:
                    logger.info(f"Image analysis successful: {description[:100]}...")
                    return description
                else:
                    logger.warning("Image analysis returned empty result")
                    return None

        except requests.exceptions.Timeout:
            logger.error("Image analysis request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Image analysis request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during image analysis: {e}")
            return None

    def generate_speech(self, text, output_path=None):
        """
        Generate speech audio from text using Text-to-Speech API.

        Args:
            text: Text to convert to speech
            output_path: Optional custom output path for audio file

        Returns:
            Path to generated WAV audio file if successful, None otherwise
        """
        try:
            if not text:
                logger.warning("No text provided for TTS")
                return None

            # Generate output filename if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = config.FILE_PATTERNS["tts_audio"].format(timestamp=timestamp)
                output_path = config.AUDIO_DIR / filename

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"Generating speech: {text[:100]}...")

            # IMPORTANT: Send text to TTS endpoint
            # API might expect JSON with text field or form data
            payload = {'text': text}

            response = requests.post(
                self.endpoints["tts"],
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()

            # IMPORTANT: Save audio content to file
            # Check if response is binary audio data
            if 'audio' in response.headers.get('Content-Type', ''):
                with open(output_path, 'wb') as audio_file:
                    audio_file.write(response.content)
                logger.info(f"Speech audio saved: {output_path}")
                return str(output_path)
            else:
                # If response is JSON with audio URL or base64
                result = response.json()
                audio_data = result.get('audio', result.get('data'))

                if audio_data:
                    # If it's a URL, download it
                    if isinstance(audio_data, str) and audio_data.startswith('http'):
                        audio_response = requests.get(audio_data, timeout=self.timeout)
                        audio_response.raise_for_status()
                        with open(output_path, 'wb') as audio_file:
                            audio_file.write(audio_response.content)
                    # If it's base64 encoded
                    elif isinstance(audio_data, str):
                        import base64
                        audio_bytes = base64.b64decode(audio_data)
                        with open(output_path, 'wb') as audio_file:
                            audio_file.write(audio_bytes)
                    else:
                        logger.error("Unknown audio data format in TTS response")
                        return None

                    logger.info(f"Speech audio saved: {output_path}")
                    return str(output_path)
                else:
                    logger.warning("TTS response did not contain audio data")
                    return None

        except requests.exceptions.Timeout:
            logger.error("TTS request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during TTS generation: {e}")
            return None

    def test_connection(self):
        """
        Test connection to the API base URL.
        Returns True if API is reachable, False otherwise.
        """
        try:
            response = requests.get(self.base_url, timeout=5)
            logger.info(f"API connection test: Status {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False

    def process_complete_query(self, audio_file_path, image_file_path, query_text=None):
        """
        Complete processing pipeline: transcribe audio, analyze image, generate response.

        Args:
            audio_file_path: Path to recorded audio file
            image_file_path: Path to captured image file
            query_text: Optional pre-transcribed text (if None, will transcribe audio)

        Returns:
            Dict with transcription, image_analysis, and response_audio_path
        """
        result = {
            'transcription': None,
            'image_analysis': None,
            'response_audio': None,
            'success': False
        }

        try:
            # Step 1: Transcribe audio if not provided
            if query_text is None:
                logger.info("Step 1: Transcribing audio...")
                result['transcription'] = self.transcribe_audio(audio_file_path)
                if not result['transcription']:
                    logger.error("Failed to transcribe audio")
                    return result
            else:
                result['transcription'] = query_text

            # Step 2: Analyze image
            logger.info("Step 2: Analyzing image...")
            result['image_analysis'] = self.analyze_image(image_file_path)
            if not result['image_analysis']:
                logger.error("Failed to analyze image")
                return result

            # IMPORTANT: Step 3: Generate response based on transcription and image analysis
            # Combine the context for a meaningful response
            logger.info("Step 3: Generating response...")
            response_text = f"Based on your question '{result['transcription']}' and the image showing {result['image_analysis']}, here is the answer."

            # Step 4: Convert response to speech
            logger.info("Step 4: Converting response to speech...")
            result['response_audio'] = self.generate_speech(response_text)

            if result['response_audio']:
                result['success'] = True
                logger.info("Complete query processing successful")
            else:
                logger.error("Failed to generate speech")

            return result

        except Exception as e:
            logger.error(f"Error in complete query processing: {e}")
            return result
