"""
Image Capture module for the Disability Support System.
Handles image capture from Raspberry Pi Camera Module V3 using rpicam-jpeg.
"""

import subprocess
import logging
from datetime import datetime
from pathlib import Path

import config

logger = logging.getLogger(__name__)


class ImageCapture:
    """
    Handles image capture from Raspberry Pi Camera Module V3.
    IMPORTANT: Uses rpicam-jpeg command-line tool as required by specification.
    """

    def __init__(self):
        """Initialize the image capture module."""
        self.tool = config.IMAGE_CONFIG["tool"]
        self.quality = config.IMAGE_CONFIG["quality"]
        self.timeout_ms = config.IMAGE_CONFIG["timeout_ms"]
        self.last_capture = None

        logger.info("ImageCapture initialized")

    def capture_image(self, output_path=None):
        """
        Capture a still image from the camera using rpicam-jpeg.

        Args:
            output_path: Optional custom output path. If None, generates timestamped filename.

        Returns:
            Path to captured image file if successful, None otherwise.
        """
        try:
            # Generate output filename if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = config.FILE_PATTERNS["captured_image"].format(timestamp=timestamp)
                output_path = config.IMAGE_DIR / filename

            # Ensure output directory exists
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # IMPORTANT: Build rpicam-jpeg command with maximum resolution
            cmd = [
                self.tool,
                "-o", str(output_path),
                "--timeout", str(self.timeout_ms),
                "--quality", str(self.quality),
                "--nopreview",  # No preview window needed
            ]

            logger.info(f"Capturing image: {output_path}")

            # Execute rpicam-jpeg command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5  # 5 second timeout for the subprocess
            )

            # Check if capture was successful
            if result.returncode == 0 and output_path.exists():
                self.last_capture = str(output_path)
                logger.info(f"Image captured successfully: {output_path}")
                return str(output_path)
            else:
                logger.error(f"Image capture failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Image capture timed out")
            return None
        except FileNotFoundError:
            logger.error(f"rpicam-jpeg command not found. Ensure rpicam-apps is installed.")
            return None
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return None

    def test_camera(self):
        """
        Test if the camera is available and working.
        Returns True if camera is accessible, False otherwise.
        """
        try:
            # Try to capture a test image
            test_path = config.IMAGE_DIR / "test_capture.jpg"

            cmd = [
                self.tool,
                "-o", str(test_path),
                "--timeout", "1000",
                "--nopreview",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            # Clean up test image
            if test_path.exists():
                test_path.unlink()

            if result.returncode == 0:
                logger.info("Camera test successful")
                return True
            else:
                logger.warning(f"Camera test failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Camera test error: {e}")
            return False

    def get_last_capture(self):
        """Return path to the last captured image."""
        return self.last_capture

    def cleanup(self):
        """Cleanup method for consistency with other modules."""
        logger.info("ImageCapture cleaned up")
