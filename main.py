"""
Main orchestrator for the Disability Support System.
Coordinates all system components to provide voice and vision-based assistance.
"""

import logging
import signal
import sys
import time
from datetime import datetime

import config
from audio_recorder import AudioRecorder
from image_capture import ImageCapture
from audio_playback import AudioPlayback
from llm_client import LLMClient
from button_handler import ButtonHandler

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_CONFIG["level"]),
    format=config.LOG_CONFIG["format"],
    handlers=[
        logging.FileHandler(config.LOG_CONFIG["file"]),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class DisabilitySupportSystem:
    """
    IMPORTANT: Main system orchestrator that coordinates all components.
    Implements the complete pipeline:
    1. Button press -> Start recording
    2. Button press -> Stop recording + Capture image
    3. Transcribe audio + Analyze image
    4. Generate response
    5. Play response audio
    """

    def __init__(self):
        """Initialize all system components."""
        logger.info("="*60)
        logger.info("Initializing Disability Support System")
        logger.info("="*60)

        # Initialize components
        self.recorder = AudioRecorder()
        self.camera = ImageCapture()
        self.player = AudioPlayback()
        self.llm_client = LLMClient()
        self.button = ButtonHandler(callback=self.on_button_press)

        # System state
        self.is_recording = False
        self.is_processing = False
        self.current_audio_file = None
        self.current_image_file = None
        self.running = False

        logger.info("All components initialized")

    def initialize(self):
        """
        Initialize hardware and test components.
        IMPORTANT: Must be called before starting the main loop.

        Returns:
            True if initialization successful, False otherwise
        """
        logger.info("Starting system initialization...")

        # Initialize audio recorder
        if not self.recorder.initialize():
            logger.error("Failed to initialize audio recorder")
            return False

        # Initialize button handler
        if not self.button.initialize():
            logger.warning("Button handler initialization failed - continuing anyway")

        # Test camera
        if not self.camera.test_camera():
            logger.warning("Camera test failed - continuing anyway")

        # Test audio playback
        if not self.player.test_playback():
            logger.warning("Audio playback test failed - will use fallback")

        logger.info("System initialization complete")
        return True

    def on_button_press(self):
        """
        IMPORTANT: Callback triggered when button is pressed.
        Toggles between starting and stopping recording.
        """
        try:
            # Ignore button presses while processing
            if self.is_processing:
                logger.info("Button press ignored - system is processing")
                return

            if not self.is_recording:
                # First press: Start recording
                self.start_recording()
            else:
                # Second press: Stop recording and process
                self.stop_recording_and_process()

        except Exception as e:
            logger.error(f"Error in button press handler: {e}")

    def start_recording(self):
        """Start audio recording."""
        logger.info("="*60)
        logger.info("BUTTON PRESS: Starting recording")
        logger.info("="*60)

        self.current_audio_file = self.recorder.start_recording()

        if self.current_audio_file:
            self.is_recording = True
            logger.info(f"Recording started: {self.current_audio_file}")
        else:
            logger.error("Failed to start recording")

    def stop_recording_and_process(self):
        """
        IMPORTANT: Stop recording, capture image, and process the complete query.
        This is the main processing pipeline.
        """
        logger.info("="*60)
        logger.info("BUTTON PRESS: Stopping recording and processing")
        logger.info("="*60)

        self.is_recording = False
        self.is_processing = True

        try:
            # Step 1: Stop recording and save audio
            audio_file = self.recorder.stop_recording()
            if not audio_file:
                logger.error("Failed to save audio recording")
                self.is_processing = False
                return

            logger.info(f"Audio saved: {audio_file}")

            # Step 2: Capture image simultaneously
            logger.info("Capturing image...")
            image_file = self.camera.capture_image()
            if not image_file:
                logger.error("Failed to capture image")
                self.is_processing = False
                return

            logger.info(f"Image captured: {image_file}")

            # Step 3: Process with LLM API
            logger.info("="*60)
            logger.info("Processing query with LLM API")
            logger.info("="*60)

            # Transcribe audio
            logger.info("Transcribing audio...")
            transcription = self.llm_client.transcribe_audio(audio_file)
            if not transcription:
                logger.error("Failed to transcribe audio")
                self.is_processing = False
                return

            logger.info(f"Transcription: {transcription}")

            # Analyze image
            logger.info("Analyzing image...")
            image_analysis = self.llm_client.analyze_image(image_file)
            if not image_analysis:
                logger.error("Failed to analyze image")
                self.is_processing = False
                return

            logger.info(f"Image analysis: {image_analysis}")

            # IMPORTANT: Generate response combining both inputs
            logger.info("Generating response...")
            response_text = self._generate_response(transcription, image_analysis)
            logger.info(f"Response: {response_text}")

            # Step 4: Convert response to speech
            logger.info("Converting response to speech...")
            response_audio = self.llm_client.generate_speech(response_text)
            if not response_audio:
                logger.error("Failed to generate speech")
                self.is_processing = False
                return

            logger.info(f"Response audio generated: {response_audio}")

            # Step 5: Play response audio
            logger.info("="*60)
            logger.info("Playing response")
            logger.info("="*60)

            if self.player.play_audio(response_audio, blocking=True):
                logger.info("Response played successfully")
            else:
                logger.error("Failed to play response")

        except Exception as e:
            logger.error(f"Error during processing: {e}")

        finally:
            self.is_processing = False
            logger.info("="*60)
            logger.info("Ready for next query")
            logger.info("="*60)

    def _generate_response(self, transcription, image_analysis):
        """
        Generate response text based on transcription and image analysis.
        IMPORTANT: This combines the user's question with visual context.

        Args:
            transcription: User's spoken question
            image_analysis: Description of captured image

        Returns:
            Response text string
        """
        # Create a meaningful response combining both inputs
        response = (
            f"Based on your question: {transcription}. "
            f"And looking at the image which shows: {image_analysis}. "
            f"Here is my response to help you."
        )

        return response

    def run(self):
        """
        IMPORTANT: Main system loop.
        Keeps the system running and waiting for button presses.
        """
        self.running = True

        logger.info("="*60)
        logger.info("System is ready and running")
        logger.info("Press the button to start recording")
        logger.info("="*60)

        try:
            while self.running:
                # Keep the main thread alive
                # Button presses are handled by GPIO callbacks
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """
        Clean shutdown of all system components.
        IMPORTANT: Ensures proper cleanup of hardware resources.
        """
        logger.info("="*60)
        logger.info("Shutting down system")
        logger.info("="*60)

        self.running = False

        # Clean up all components
        try:
            if self.is_recording:
                self.recorder.stop_recording()

            self.recorder.cleanup()
            self.camera.cleanup()
            self.player.cleanup()
            self.button.cleanup()

            logger.info("System shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def signal_handler(sig, frame):
    """Handle system signals for graceful shutdown."""
    logger.info(f"Signal {sig} received")
    sys.exit(0)


def main():
    """Main entry point for the application."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and initialize system
    system = DisabilitySupportSystem()

    if not system.initialize():
        logger.error("System initialization failed")
        sys.exit(1)

    # Run the system
    try:
        system.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
