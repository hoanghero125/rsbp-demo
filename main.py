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
from led_controller import LEDController

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
    Implements the complete Vision-Language Model pipeline:
    1. Button press -> Start recording
    2. Button press -> Stop recording + Capture image
    3. Transcribe audio (STT) -> Get user's question
    4. Send image + question to VLM -> Get final answer
    5. Convert answer to speech (TTS)
    6. Play response audio
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
        self.led = LEDController(num_leds=3)  # ReSpeaker 2-Mics HAT has 3 LEDs

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

        # Initialize LED controller
        if not self.led.initialize():
            logger.warning("LED controller initialization failed - continuing anyway")
        else:
            # Test LEDs if initialized successfully
            logger.info("Testing LEDs...")
            self.led.test_leds()

        # Test camera
        if not self.camera.test_camera():
            logger.warning("Camera test failed - continuing anyway")

        # Test audio playback
        if not self.player.test_playback():
            logger.warning("Audio playback test failed - will use fallback")

        # Set LED to IDLE state
        self.led.set_state(LEDController.STATE_IDLE)

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

        # Set LED to RECORDING state (Red)
        self.led.set_state(LEDController.STATE_RECORDING)

        self.current_audio_file = self.recorder.start_recording()

        if self.current_audio_file:
            self.is_recording = True
            logger.info(f"Recording started: {self.current_audio_file}")
        else:
            logger.error("Failed to start recording")
            self.led.set_state(LEDController.STATE_ERROR)

    def stop_recording_and_process(self):
        """
        IMPORTANT: Stop recording, capture image, and process the complete query.
        This is the main processing pipeline using Vision-Language Model.

        Pipeline:
        1. Stop recording and save audio
        2. Capture image
        3. Transcribe audio (STT) -> user's question
        4. Send image + question to VLM -> get final answer
        5. Convert answer to speech (TTS)
        6. Play audio response
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
                self.led.set_state(LEDController.STATE_ERROR)
                self.is_processing = False
                return

            logger.info(f"Audio saved: {audio_file}")

            # Step 2: Capture image
            logger.info("Capturing image...")
            # Set LED to CAPTURING state (Yellow)
            self.led.set_state(LEDController.STATE_CAPTURING)

            image_file = self.camera.capture_image()
            if not image_file:
                logger.error("Failed to capture image")
                self.led.set_state(LEDController.STATE_ERROR)
                self.is_processing = False
                return

            logger.info(f"Image captured: {image_file}")

            # Step 3: Transcribe audio to get user's question
            logger.info("="*60)
            logger.info("Processing with Vision-Language Model")
            logger.info("="*60)

            # Set LED to PROCESSING state (Rotating Cyan)
            self.led.set_state(LEDController.STATE_PROCESSING)

            logger.info("Step 1: Transcribing audio (STT)...")
            user_question = self.llm_client.transcribe_audio(audio_file)
            if not user_question:
                logger.error("Failed to transcribe audio")
                self.led.set_state(LEDController.STATE_ERROR)
                self.is_processing = False
                return

            logger.info(f"User question: {user_question}")

            # Step 4: Send image + question to VLM for final answer
            # IMPORTANT: The VLM endpoint combines vision and language understanding
            # It takes the image and the user's question, then generates the answer
            logger.info("Step 2: Querying Vision-Language Model...")
            logger.info(f"  Image: {image_file}")
            logger.info(f"  Question: {user_question}")

            final_answer = self.llm_client.analyze_image(image_file, prompt=user_question)
            if not final_answer:
                logger.error("Failed to get response from VLM")
                self.led.set_state(LEDController.STATE_ERROR)
                self.is_processing = False
                return

            logger.info(f"VLM Answer: {final_answer}")

            # Step 5: Convert answer to speech (TTS)
            logger.info("Step 3: Converting answer to speech (TTS)...")
            response_audio = self.llm_client.generate_speech(final_answer)
            if not response_audio:
                logger.error("Failed to generate speech")
                self.led.set_state(LEDController.STATE_ERROR)
                self.is_processing = False
                return

            logger.info(f"Response audio generated: {response_audio}")

            # Step 6: Play response audio
            logger.info("="*60)
            logger.info("Playing response")
            logger.info("="*60)

            # Set LED to SPEAKING state (Pulsing Blue)
            self.led.set_state(LEDController.STATE_SPEAKING)

            if self.player.play_audio(response_audio, blocking=True):
                logger.info("Response played successfully")
            else:
                logger.error("Failed to play response")
                self.led.set_state(LEDController.STATE_ERROR)

        except Exception as e:
            logger.error(f"Error during processing: {e}")
            self.led.set_state(LEDController.STATE_ERROR)
            time.sleep(2)  # Show error for 2 seconds

        finally:
            self.is_processing = False
            # Return LED to IDLE state
            self.led.set_state(LEDController.STATE_IDLE)
            logger.info("="*60)
            logger.info("Ready for next query")
            logger.info("="*60)


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
            self.led.cleanup()

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
