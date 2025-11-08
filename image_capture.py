"""
Image capture module for Raspberry Pi Camera Module V3.

Captures still images using rpicam-jpeg command-line tool.
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ImageCapture:
    """Handles image capture from Raspberry Pi camera."""

    def __init__(self, output_dir: str = "/home/pi/Pictures"):
        """
        Initialize image capture.

        Args:
            output_dir: Directory to save captured images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture_image(self) -> Optional[str]:
        """
        Capture a single image from the camera.

        Returns:
            Path to captured image, or None if failed
        """
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"recording_{timestamp}.jpg"

        try:
            logger.info(f"Capturing image to: {output_file}")

            # Use rpicam-jpeg to capture still image
            cmd = [
                "rpicam-jpeg",
                "--output",
                str(output_file),
                "--timeout",
                "1000",  # 1 second timeout
                "--nopreview",  # Don't show preview
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                logger.info(f"Image captured successfully: {output_file}")
                return str(output_file)
            else:
                logger.error(f"rpicam-jpeg failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Image capture timeout")
            return None
        except FileNotFoundError:
            logger.error("rpicam-jpeg not found. Is it installed?")
            return None
        except Exception as e:
            logger.error(f"Image capture error: {e}")
            return None

    def capture_image_with_options(
        self,
        width: int = 1920,
        height: int = 1440,
        quality: int = 90,
    ) -> Optional[str]:
        """
        Capture image with custom options.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            quality: JPEG quality (0-100)

        Returns:
            Path to captured image, or None if failed
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"recording_{timestamp}.jpg"

        try:
            logger.info(f"Capturing image: {width}x{height}, quality={quality}")

            cmd = [
                "rpicam-jpeg",
                "--output",
                str(output_file),
                "--width",
                str(width),
                "--height",
                str(height),
                "--quality",
                str(quality),
                "--timeout",
                "1000",
                "--nopreview",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                logger.info(f"Image captured: {output_file}")
                return str(output_file)
            else:
                logger.error(f"rpicam-jpeg failed: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Image capture error: {e}")
            return None
