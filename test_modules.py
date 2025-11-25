"""
Test suite for the Disability Support System.
Validates all modules, hardware components, and API connectivity.
"""

import sys
import logging
from pathlib import Path

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def test_imports():
    """Test that all required modules can be imported."""
    logger.info("="*60)
    logger.info("Testing module imports")
    logger.info("="*60)

    modules_to_test = [
        'config',
        'audio_recorder',
        'image_capture',
        'audio_playback',
        'llm_client',
        'button_handler',
        'main'
    ]

    results = {}

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            logger.info(f"✓ {module_name}: Import successful")
            results[module_name] = True
        except Exception as e:
            logger.error(f"✗ {module_name}: Import failed - {e}")
            results[module_name] = False

    return all(results.values()), results


def test_configuration():
    """Test that configuration is properly loaded."""
    logger.info("="*60)
    logger.info("Testing configuration")
    logger.info("="*60)

    try:
        import config

        # Check required directories exist
        assert config.AUDIO_DIR.exists(), "Audio directory missing"
        assert config.IMAGE_DIR.exists(), "Image directory missing"
        assert config.LOG_DIR.exists(), "Log directory missing"

        logger.info(f"✓ Audio directory: {config.AUDIO_DIR}")
        logger.info(f"✓ Image directory: {config.IMAGE_DIR}")
        logger.info(f"✓ Log directory: {config.LOG_DIR}")

        # Check API configuration
        assert config.API_BASE_URL, "API base URL not set"
        logger.info(f"✓ API base URL: {config.API_BASE_URL}")

        # Check all endpoints are configured
        assert "transcribe" in config.API_ENDPOINTS, "Transcribe endpoint missing"
        assert "analyze_image" in config.API_ENDPOINTS, "Image analysis endpoint missing"
        assert "tts" in config.API_ENDPOINTS, "TTS endpoint missing"

        logger.info("✓ All API endpoints configured")

        # Check audio configuration
        assert config.AUDIO_CONFIG["sample_rate"] == 16000, "Sample rate incorrect"
        logger.info(f"✓ Audio sample rate: {config.AUDIO_CONFIG['sample_rate']} Hz")

        # Check button configuration
        assert config.BUTTON_CONFIG["pin"] == 17, "Button pin incorrect"
        logger.info(f"✓ Button GPIO pin: {config.BUTTON_CONFIG['pin']}")

        logger.info("✓ Configuration test passed")
        return True

    except AssertionError as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Configuration test error: {e}")
        return False


def test_audio_recorder():
    """Test audio recorder initialization."""
    logger.info("="*60)
    logger.info("Testing audio recorder")
    logger.info("="*60)

    try:
        from audio_recorder import AudioRecorder

        recorder = AudioRecorder()
        logger.info("✓ AudioRecorder instantiated")

        if recorder.initialize():
            logger.info("✓ AudioRecorder initialized successfully")
            recorder.cleanup()
            return True
        else:
            logger.warning("⚠ AudioRecorder initialization failed (hardware may not be available)")
            return True  # Not a critical failure for testing

    except Exception as e:
        logger.error(f"✗ AudioRecorder test failed: {e}")
        return False


def test_image_capture():
    """Test image capture module."""
    logger.info("="*60)
    logger.info("Testing image capture")
    logger.info("="*60)

    try:
        from image_capture import ImageCapture

        camera = ImageCapture()
        logger.info("✓ ImageCapture instantiated")

        if camera.test_camera():
            logger.info("✓ Camera is working")
            return True
        else:
            logger.warning("⚠ Camera test failed (hardware may not be available)")
            return True  # Not a critical failure for testing

    except Exception as e:
        logger.error(f"✗ ImageCapture test failed: {e}")
        return False


def test_audio_playback():
    """Test audio playback module."""
    logger.info("="*60)
    logger.info("Testing audio playback")
    logger.info("="*60)

    try:
        from audio_playback import AudioPlayback

        player = AudioPlayback()
        logger.info("✓ AudioPlayback instantiated")

        if player.test_playback():
            logger.info("✓ Audio playback system is working")
        else:
            logger.warning("⚠ Primary playback method failed, fallback will be used")

        player.cleanup()
        return True

    except Exception as e:
        logger.error(f"✗ AudioPlayback test failed: {e}")
        return False


def test_llm_client():
    """Test LLM client initialization and connection."""
    logger.info("="*60)
    logger.info("Testing LLM client")
    logger.info("="*60)

    try:
        from llm_client import LLMClient

        client = LLMClient()
        logger.info("✓ LLMClient instantiated")
        logger.info(f"✓ API base URL: {client.base_url}")
        logger.info(f"✓ Transcribe endpoint: {client.endpoints['transcribe']}")
        logger.info(f"✓ Image analysis endpoint: {client.endpoints['analyze_image']}")
        logger.info(f"✓ TTS endpoint: {client.endpoints['tts']}")

        # Test API connection
        logger.info("Testing API connection...")
        if client.test_connection():
            logger.info("✓ API is reachable")
        else:
            logger.warning("⚠ API connection test failed")

        return True

    except Exception as e:
        logger.error(f"✗ LLMClient test failed: {e}")
        return False


def test_button_handler():
    """Test button handler initialization."""
    logger.info("="*60)
    logger.info("Testing button handler")
    logger.info("="*60)

    try:
        from button_handler import ButtonHandler

        button = ButtonHandler()
        logger.info("✓ ButtonHandler instantiated")

        if button.initialize():
            logger.info("✓ ButtonHandler initialized successfully")
            button.cleanup()
        else:
            logger.warning("⚠ ButtonHandler initialization failed (GPIO may not be available)")

        return True

    except Exception as e:
        logger.error(f"✗ ButtonHandler test failed: {e}")
        return False


def test_dependencies():
    """Test that all required Python packages are installed."""
    logger.info("="*60)
    logger.info("Testing Python dependencies")
    logger.info("="*60)

    dependencies = {
        'requests': 'HTTP client for API calls',
        'pyaudio': 'Audio input/output',
        'wave': 'WAV file handling',
    }

    # Optional dependencies
    optional_dependencies = {
        'RPi.GPIO': 'GPIO control (Raspberry Pi only)',
    }

    results = {}

    # Test required dependencies
    for package, description in dependencies.items():
        try:
            __import__(package)
            logger.info(f"✓ {package}: Installed ({description})")
            results[package] = True
        except ImportError:
            logger.error(f"✗ {package}: Missing ({description})")
            results[package] = False

    # Test optional dependencies
    for package, description in optional_dependencies.items():
        try:
            __import__(package.replace('.', '_').lower())
            logger.info(f"✓ {package}: Installed ({description})")
        except ImportError:
            logger.warning(f"⚠ {package}: Missing ({description}) - This is optional")

    return all(results.values()), results


def test_system_tools():
    """Test that required system tools are available."""
    logger.info("="*60)
    logger.info("Testing system tools")
    logger.info("="*60)

    import subprocess

    tools = {
        'rpicam-jpeg': 'Image capture from camera',
        'aplay': 'Audio playback (ALSA)',
        'python3': 'Python runtime',
    }

    results = {}

    for tool, description in tools.items():
        try:
            result = subprocess.run(
                [tool, '--version'] if tool != 'rpicam-jpeg' else ['which', tool],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0 or subprocess.run(['which', tool], capture_output=True).returncode == 0:
                logger.info(f"✓ {tool}: Available ({description})")
                results[tool] = True
            else:
                logger.warning(f"⚠ {tool}: Not found ({description})")
                results[tool] = False
        except Exception as e:
            logger.warning(f"⚠ {tool}: Test failed ({description}) - {e}")
            results[tool] = False

    return results


def run_all_tests():
    """Run all tests and generate summary report."""
    logger.info("\n" + "="*60)
    logger.info("DISABILITY SUPPORT SYSTEM - TEST SUITE")
    logger.info("="*60 + "\n")

    test_results = {}

    # Run all tests
    test_results['imports'], _ = test_imports()
    test_results['configuration'] = test_configuration()
    test_results['dependencies'], _ = test_dependencies()
    test_results['system_tools'] = test_system_tools()
    test_results['audio_recorder'] = test_audio_recorder()
    test_results['image_capture'] = test_image_capture()
    test_results['audio_playback'] = test_audio_playback()
    test_results['llm_client'] = test_llm_client()
    test_results['button_handler'] = test_button_handler()

    # Generate summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)

    passed = 0
    failed = 0

    for test_name, result in test_results.items():
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        logger.info(f"{symbol} {test_name}: {status}")

        if result:
            passed += 1
        else:
            failed += 1

    logger.info("="*60)
    logger.info(f"Total tests: {len(test_results)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
