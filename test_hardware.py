"""
Hardware Testing Script for Disability Support System.
Tests each hardware component independently without requiring API access.
"""

import sys
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def test_camera():
    """Test camera by capturing a test image."""
    logger.info("="*60)
    logger.info("TEST 1: Camera Module")
    logger.info("="*60)

    try:
        from image_capture import ImageCapture

        camera = ImageCapture()
        logger.info("Capturing test image...")

        image_path = camera.capture_image()

        if image_path and Path(image_path).exists():
            logger.info(f"SUCCESS: Image captured at {image_path}")
            logger.info(f"Image size: {Path(image_path).stat().st_size} bytes")
            return True
        else:
            logger.error("FAILED: Could not capture image")
            return False

    except Exception as e:
        logger.error(f"FAILED: {e}")
        return False


def test_audio_recording():
    """Test microphone by recording a short audio clip."""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Microphone (ReSpeaker HAT)")
    logger.info("="*60)

    try:
        from audio_recorder import AudioRecorder

        recorder = AudioRecorder()

        if not recorder.initialize():
            logger.error("FAILED: Could not initialize audio recorder")
            return False

        logger.info("Recording for 3 seconds...")
        logger.info("Please speak into the microphone now!")

        # Start recording
        audio_file = recorder.start_recording()
        if not audio_file:
            logger.error("FAILED: Could not start recording")
            recorder.cleanup()
            return False

        # Record for 3 seconds
        time.sleep(3)

        # Stop recording
        saved_file = recorder.stop_recording()
        recorder.cleanup()

        if saved_file and Path(saved_file).exists():
            logger.info(f"SUCCESS: Audio recorded at {saved_file}")
            logger.info(f"Audio size: {Path(saved_file).stat().st_size} bytes")
            return saved_file
        else:
            logger.error("FAILED: Could not save audio recording")
            return False

    except Exception as e:
        logger.error(f"FAILED: {e}")
        return False


def test_audio_playback(audio_file=None):
    """Test speaker by playing audio."""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Speaker Playback")
    logger.info("="*60)

    try:
        from audio_playback import AudioPlayback

        player = AudioPlayback()

        # If we have a recorded file from previous test, play it
        if audio_file and Path(audio_file).exists():
            logger.info(f"Playing back recorded audio: {audio_file}")
            logger.info("You should hear your voice now!")

            success = player.play_audio(audio_file, blocking=True)

            if success:
                logger.info("SUCCESS: Audio playback completed")
                player.cleanup()
                return True
            else:
                logger.error("FAILED: Could not play audio")
                player.cleanup()
                return False
        else:
            logger.warning("No audio file to play back")
            logger.info("Testing if playback system is available...")
            if player.test_playback():
                logger.info("SUCCESS: Playback system is working")
                return True
            else:
                logger.warning("Playback test inconclusive")
                return False

    except Exception as e:
        logger.error(f"FAILED: {e}")
        return False


def test_button():
    """Test GPIO button."""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: GPIO Button")
    logger.info("="*60)

    try:
        from button_handler import ButtonHandler

        button_pressed = [False]  # Use list to allow modification in callback

        def on_press():
            logger.info("Button press detected!")
            button_pressed[0] = True

        button = ButtonHandler(callback=on_press)

        if not button.initialize():
            logger.warning("WARNING: Could not initialize GPIO (may not be on Raspberry Pi)")
            logger.info("GPIO test skipped")
            return True  # Not a failure, just not available

        logger.info("Please press the button on GPIO pin 17 within 10 seconds...")

        # Wait for button press with timeout
        start_time = time.time()
        while time.time() - start_time < 10:
            if button_pressed[0]:
                logger.info("SUCCESS: Button is working!")
                button.cleanup()
                return True
            time.sleep(0.1)

        logger.warning("No button press detected within 10 seconds")
        logger.info("This could mean:")
        logger.info("  - Button is not connected")
        logger.info("  - Button is on wrong GPIO pin")
        logger.info("  - You didn't press the button")
        button.cleanup()
        return False

    except Exception as e:
        logger.error(f"FAILED: {e}")
        return False


def test_complete_workflow():
    """Test complete hardware workflow: button -> record -> capture -> playback."""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: Complete Workflow (Button + Record + Camera + Playback)")
    logger.info("="*60)

    try:
        from button_handler import ButtonHandler
        from audio_recorder import AudioRecorder
        from image_capture import ImageCapture
        from audio_playback import AudioPlayback

        # Initialize components
        button = ButtonHandler()
        recorder = AudioRecorder()
        camera = ImageCapture()
        player = AudioPlayback()

        if not button.initialize():
            logger.warning("GPIO not available - skipping complete workflow test")
            return True

        if not recorder.initialize():
            logger.error("Could not initialize recorder")
            return False

        state = {'recording': False, 'audio_file': None}

        def on_button_press():
            if not state['recording']:
                # First press: start recording
                logger.info("Button pressed - Starting recording...")
                state['audio_file'] = recorder.start_recording()
                state['recording'] = True
            else:
                # Second press: stop recording and capture image
                logger.info("Button pressed - Stopping recording and capturing image...")
                state['audio_file'] = recorder.stop_recording()
                state['recording'] = False

        button.set_callback(on_button_press)

        logger.info("Press button once to start recording, press again to stop")
        logger.info("Waiting for first button press...")

        # Wait for first press
        timeout = 15
        start = time.time()
        while not state['recording'] and (time.time() - start) < timeout:
            time.sleep(0.1)

        if not state['recording']:
            logger.warning("No button press detected - workflow test incomplete")
            button.cleanup()
            recorder.cleanup()
            return False

        logger.info("Recording... speak now! Press button again when done.")

        # Wait for second press
        start = time.time()
        while state['recording'] and (time.time() - start) < timeout:
            time.sleep(0.1)

        if state['recording']:
            logger.warning("Second button press not detected - stopping manually")
            recorder.stop_recording()

        # Capture image
        logger.info("Capturing image...")
        image_file = camera.capture_image()

        # Play back recorded audio
        if state['audio_file']:
            logger.info("Playing back recorded audio...")
            player.play_audio(state['audio_file'], blocking=True)

        # Cleanup
        button.cleanup()
        recorder.cleanup()
        player.cleanup()

        if state['audio_file'] and image_file:
            logger.info("SUCCESS: Complete workflow executed!")
            logger.info(f"  Audio: {state['audio_file']}")
            logger.info(f"  Image: {image_file}")
            return True
        else:
            logger.error("Workflow incomplete")
            return False

    except Exception as e:
        logger.error(f"FAILED: {e}")
        return False


def interactive_menu():
    """Interactive menu for hardware testing."""
    logger.info("\n" + "="*60)
    logger.info("DISABILITY SUPPORT SYSTEM - HARDWARE TEST")
    logger.info("="*60)
    logger.info("\nSelect a test to run:")
    logger.info("1. Test Camera")
    logger.info("2. Test Microphone (record 3 seconds)")
    logger.info("3. Test Speaker (playback recorded audio)")
    logger.info("4. Test Button")
    logger.info("5. Test Complete Workflow")
    logger.info("6. Run All Tests")
    logger.info("0. Exit")

    recorded_audio = None

    while True:
        try:
            choice = input("\nEnter choice (0-6): ").strip()

            if choice == "0":
                logger.info("Exiting...")
                break
            elif choice == "1":
                test_camera()
            elif choice == "2":
                result = test_audio_recording()
                if result:
                    recorded_audio = result
            elif choice == "3":
                test_audio_playback(recorded_audio)
            elif choice == "4":
                test_button()
            elif choice == "5":
                test_complete_workflow()
            elif choice == "6":
                logger.info("\n" + "="*60)
                logger.info("RUNNING ALL HARDWARE TESTS")
                logger.info("="*60)

                results = {}
                results['camera'] = test_camera()
                results['recording'] = test_audio_recording()
                recorded_audio = results['recording'] if results['recording'] else None
                results['playback'] = test_audio_playback(recorded_audio)
                results['button'] = test_button()

                logger.info("\n" + "="*60)
                logger.info("TEST RESULTS SUMMARY")
                logger.info("="*60)
                for name, result in results.items():
                    status = "PASSED" if result else "FAILED"
                    symbol = "✓" if result else "✗"
                    logger.info(f"{symbol} {name}: {status}")
                logger.info("="*60)
            else:
                logger.warning("Invalid choice")

        except KeyboardInterrupt:
            logger.info("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


if __name__ == "__main__":
    interactive_menu()
