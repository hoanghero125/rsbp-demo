"""
Module testing script for Disability Support System.

Tests all components individually to verify proper functionality.
Run this script to validate system setup before deployment.
"""

import logging
import sys
from pathlib import Path

# Configure logging for testing
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def test_imports():
    """Test that all required modules can be imported."""
    logger.info("=" * 60)
    logger.info("Testing module imports...")
    logger.info("=" * 60)

    try:
        from audio_recorder import AudioRecorder
        logger.info("✓ AudioRecorder imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import AudioRecorder: {e}")
        return False

    try:
        from image_capture import ImageCapture
        logger.info("✓ ImageCapture imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import ImageCapture: {e}")
        return False

    try:
        from audio_playback import AudioPlayback
        logger.info("✓ AudioPlayback imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import AudioPlayback: {e}")
        return False

    try:
        from llm_client import LLMClient
        logger.info("✓ LLMClient imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import LLMClient: {e}")
        return False

    try:
        from button_handler import ButtonHandler
        logger.info("✓ ButtonHandler imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import ButtonHandler: {e}")
        return False

    try:
        from config import Config
        logger.info("✓ Config imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import Config: {e}")
        return False

    return True


def test_config():
    """Test configuration module."""
    logger.info("=" * 60)
    logger.info("Testing configuration...")
    logger.info("=" * 60)

    try:
        from config import Config

        audio_cfg = Config.get_audio_config()
        logger.info(f"Audio Config: {audio_cfg}")

        llm_cfg = Config.get_llm_api_config()
        logger.info(f"LLM API Config: {llm_cfg}")

        button_cfg = Config.get_button_config()
        logger.info(f"Button Config: {button_cfg}")

        logger.info("✓ Configuration loaded successfully")
        return True

    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


def test_audio_recorder():
    """Test audio recorder initialization."""
    logger.info("=" * 60)
    logger.info("Testing AudioRecorder...")
    logger.info("=" * 60)

    try:
        from audio_recorder import AudioRecorder

        recorder = AudioRecorder()
        logger.info(f"✓ AudioRecorder initialized")
        logger.info(f"  - Output directory: {recorder.output_dir}")
        logger.info(f"  - Channels: {recorder.CHANNELS}")
        logger.info(f"  - Sample rate: {recorder.SAMPLE_RATE} Hz")
        logger.info(f"  - ReSpeaker device index: {recorder.RESPEAKER_DEVICE_INDEX}")

        # Check if output directory exists
        if recorder.output_dir.exists():
            logger.info(f"✓ Output directory exists: {recorder.output_dir}")
        else:
            logger.warning(
                f"⚠ Output directory does not exist: {recorder.output_dir}"
            )

        return True

    except Exception as e:
        logger.error(f"✗ AudioRecorder test failed: {e}")
        return False


def test_image_capture():
    """Test image capture initialization."""
    logger.info("=" * 60)
    logger.info("Testing ImageCapture...")
    logger.info("=" * 60)

    try:
        from image_capture import ImageCapture

        camera = ImageCapture()
        logger.info(f"✓ ImageCapture initialized")
        logger.info(f"  - Output directory: {camera.output_dir}")

        # Check if output directory exists
        if camera.output_dir.exists():
            logger.info(f"✓ Output directory exists: {camera.output_dir}")
        else:
            logger.warning(
                f"⚠ Output directory does not exist: {camera.output_dir}"
            )

        # Check if rpicam-jpeg is available
        import shutil

        if shutil.which("rpicam-jpeg"):
            logger.info("✓ rpicam-jpeg command found")
        else:
            logger.warning("⚠ rpicam-jpeg command not found (on non-RPi system?)")

        return True

    except Exception as e:
        logger.error(f"✗ ImageCapture test failed: {e}")
        return False


def test_audio_playback():
    """Test audio playback initialization."""
    logger.info("=" * 60)
    logger.info("Testing AudioPlayback...")
    logger.info("=" * 60)

    try:
        from audio_playback import AudioPlayback

        playback = AudioPlayback()
        logger.info(f"✓ AudioPlayback initialized")
        logger.info(f"  - ReSpeaker device index: {playback.RESPEAKER_DEVICE_INDEX}")
        logger.info(f"  - Chunk size: {playback.CHUNK_SIZE}")

        # Check if aplay is available
        import shutil

        if shutil.which("aplay"):
            logger.info("✓ aplay command found")
        else:
            logger.warning("⚠ aplay command not found (fallback to PyAudio)")

        return True

    except Exception as e:
        logger.error(f"✗ AudioPlayback test failed: {e}")
        return False


def test_llm_client():
    """Test LLM client initialization."""
    logger.info("=" * 60)
    logger.info("Testing LLMClient...")
    logger.info("=" * 60)

    try:
        from llm_client import LLMClient

        client = LLMClient()
        logger.info(f"✓ LLMClient initialized")
        logger.info(f"  - Base URL: {client.base_url}")
        logger.info(f"  - Timeout: {client.timeout}s")

        # Check if requests is available
        try:
            import requests

            logger.info("✓ requests library available")
        except ImportError:
            logger.warning("⚠ requests library not available")

        return True

    except Exception as e:
        logger.error(f"✗ LLMClient test failed: {e}")
        return False


def test_button_handler():
    """Test button handler initialization."""
    logger.info("=" * 60)
    logger.info("Testing ButtonHandler...")
    logger.info("=" * 60)

    try:
        from button_handler import ButtonHandler

        handler = ButtonHandler()
        logger.info(f"✓ ButtonHandler initialized")
        logger.info(f"  - Button pin: {handler.BUTTON_PIN}")
        logger.info(f"  - Debounce time: {handler.DEBOUNCE_TIME}ms")

        # Check if RPi.GPIO is available
        try:
            import RPi.GPIO

            logger.info("✓ RPi.GPIO available")
        except ImportError:
            logger.warning("⚠ RPi.GPIO not available (not on Raspberry Pi?)")

        return True

    except Exception as e:
        logger.error(f"✗ ButtonHandler test failed: {e}")
        return False


def test_directories():
    """Test that required directories exist or can be created."""
    logger.info("=" * 60)
    logger.info("Testing directory structure...")
    logger.info("=" * 60)

    directories = [
        "/home/pi/recordings",
        "/home/pi/Pictures",
    ]

    all_exist = True
    for dir_path in directories:
        path = Path(dir_path)
        if path.exists():
            logger.info(f"✓ Directory exists: {dir_path}")
        else:
            logger.warning(f"⚠ Directory missing: {dir_path}")
            all_exist = False

    return all_exist


def main():
    """Run all tests."""
    logger.info("\n")
    logger.info("#" * 60)
    logger.info("# Disability Support System - Module Test Suite")
    logger.info("#" * 60)
    logger.info("\n")

    results = {}

    # Run all tests
    results["Imports"] = test_imports()
    results["Configuration"] = test_config()
    results["AudioRecorder"] = test_audio_recorder()
    results["ImageCapture"] = test_image_capture()
    results["AudioPlayback"] = test_audio_playback()
    results["LLMClient"] = test_llm_client()
    results["ButtonHandler"] = test_button_handler()
    results["Directories"] = test_directories()

    # Summary
    logger.info("\n")
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 60)
    logger.info("\n")

    # Return success if all tests passed
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
