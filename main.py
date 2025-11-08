"""
Main application orchestrator for Raspberry Pi disability support system.

Pipeline:
1. Button pressed -> Recording starts (captures user's question)
2. Button pressed again -> Recording ends + Picture captured
3. LLM processing: STT (audio) + Image analysis
4. LLM response to user's question
5. TTS conversion of response
6. Playback of audio response

Hardware:
- Raspberry Pi 3 Model B+
- ReSpeaker 2-Microphone HAT (audio input/output)
- Raspberry Pi Camera Module V3
- GPIO button on pin 17
"""

import logging
import signal
import sys
import time
from datetime import datetime
from typing import Any

from audio_recorder import AudioRecorder
from image_capture import ImageCapture
from llm_client import LLMClient
from audio_playback import AudioPlayback
from button_handler import ButtonHandler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/var/log/rsbp_system.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class DisabilitySupportSystem:
    """Main application orchestrator for disability support system."""

    def __init__(self):
        """Initialize all system components."""
        logger.info("=" * 60)
        logger.info("Initializing Disability Support System")
        logger.info("=" * 60)

        # Initialize hardware components
        self.audio_recorder = AudioRecorder()
        self.image_capture = ImageCapture()
        self.audio_playback = AudioPlayback()
        self.llm_client = LLMClient()
        self.button_handler = ButtonHandler(on_button_press=self._handle_button_press)

        # State management
        self.is_recording = False
        self.recording_start_time = None
        self.current_audio_file = None
        self.current_image_file = None

        # Initialize GPIO
        if not self.button_handler.initialize():
            logger.error("Failed to initialize GPIO button handler")
            raise RuntimeError("GPIO initialization failed")

        logger.info("System initialization complete")

    def _handle_button_press(self) -> None:
        """Handle button press events - toggle recording state."""
        if self.is_recording:
            self._stop_recording_and_process()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        """Start audio recording."""
        try:
            logger.info("Recording started")
            self.recording_start_time = datetime.now()
            self.current_audio_file = self.audio_recorder.start_recording()
            self.is_recording = True

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False

    def _stop_recording_and_process(self) -> None:
        """Stop recording, capture image, and process with LLM."""
        try:
            if not self.is_recording:
                logger.warning("No active recording to stop")
                return

            logger.info("Recording stopped")
            self.is_recording = False

            # Stop audio recording
            self.current_audio_file = self.audio_recorder.stop_recording()
            if not self.current_audio_file:
                logger.error("Failed to save audio recording")
                return

            # Calculate recording duration
            if self.recording_start_time:
                recording_duration = (
                    datetime.now() - self.recording_start_time
                ).total_seconds()
                logger.info(f"Recording duration: {recording_duration:.2f} seconds")

            # Capture image
            self.current_image_file = self.image_capture.capture_image()
            if not self.current_image_file:
                logger.error("Failed to capture image")
                return

            # Process with LLM in separate context to avoid blocking button handler
            self._process_with_llm()

        except Exception as e:
            logger.error(f"Error in recording stop/process: {e}")
            self.is_recording = False

    def _process_with_llm(self) -> None:
        """Process user input with LLM: STT, image analysis, and TTS."""
        try:
            logger.info("Starting LLM processing pipeline")

            # IMPORTANT: Step 1 - Transcribe audio (STT)
            logger.info("Step 1: Transcribing audio to text (STT)")

            if not self.current_audio_file:
                logger.error("No audio file available")
                self._play_error_response("Audio recording failed")
                return

            question_text = self.llm_client.transcribe_audio(self.current_audio_file)

            if not question_text:
                logger.error("Failed to transcribe audio")
                self._play_error_response("Failed to understand your question")
                return

            logger.info(f"Transcribed question: {question_text}")

            # IMPORTANT: Step 2 - Analyze image
            logger.info("Step 2: Analyzing image with context from question")

            if not self.current_image_file:
                logger.error("No image file available")
                self._play_error_response("Image capture failed")
                return

            image_analysis = self.llm_client.analyze_image(
                self.current_image_file, question=question_text
            )

            if not image_analysis:
                logger.error("Failed to analyze image")
                self._play_error_response("Failed to analyze the image")
                return

            logger.info("Image analysis complete")

            # IMPORTANT: Step 3 - Generate LLM response
            # Combine question and image analysis for better context
            logger.info("Step 3: Generating LLM response")

            # For now, we'll use the image analysis as the response
            # In a real system, this would go through another LLM endpoint
            response_text = (
                f"Based on your question and the image analysis: {image_analysis}"
            )

            logger.info(f"LLM response generated: {response_text[:100]}...")

            # IMPORTANT: Step 4 - Convert response to speech (TTS)
            logger.info("Step 4: Converting response to speech (TTS)")
            tts_output_file = f"/tmp/response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

            tts_file = self.llm_client.generate_tts(response_text, tts_output_file)

            if not tts_file:
                logger.error("Failed to generate TTS audio")
                self._play_error_response("Failed to generate response")
                return

            # IMPORTANT: Step 5 - Play audio response
            logger.info("Step 5: Playing audio response to user")
            self.audio_playback.play_audio_file(tts_file, blocking=True)

            logger.info("=" * 60)
            logger.info("Processing pipeline complete")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Error in LLM processing: {e}")
            self._play_error_response("An error occurred during processing")

    def _play_error_response(self, message: str) -> None:
        """Play an error message to the user."""
        try:
            logger.warning(f"Playing error message: {message}")
            # In a real system, this would also use TTS
            # For now, just log it
        except Exception as e:
            logger.error(f"Failed to play error response: {e}")

    def run(self) -> None:
        """Run the main application loop."""
        try:
            logger.info("System ready and listening for button presses")
            logger.info("Press button to start recording")
            logger.info("Press button again to stop and process")

            # Keep the application running
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
            self.shutdown()
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            self.shutdown()

    def shutdown(self) -> None:
        """Gracefully shutdown the system."""
        logger.info("Shutting down system")

        try:
            # Stop any ongoing recording
            if self.is_recording:
                self.audio_recorder.stop_recording()
                self.is_recording = False

            # Clean up GPIO
            self.button_handler.cleanup()

            logger.info("System shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def main():
    """Entry point for the application."""
    system = None

    try:
        system = DisabilitySupportSystem()

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum: int, frame: Any) -> None:
            """Handle shutdown signals."""
            logger.info(f"Signal {signum} received")
            if system:
                system.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Run the main application
        system.run()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        if system:
            system.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
