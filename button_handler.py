"""
GPIO button input handler for Raspberry Pi.

Detects button presses and triggers recording state changes.
"""

import logging
from typing import Callable, Optional

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

logger = logging.getLogger(__name__)


class ButtonHandler:
    """Handles GPIO button input for recording control."""

    # GPIO configuration
    BUTTON_PIN = 17  # GPIO pin for button input
    DEBOUNCE_TIME = 500  # milliseconds

    def __init__(self, on_button_press: Optional[Callable] = None):
        """
        Initialize button handler.

        Args:
            on_button_press: Callback function to execute on button press
        """
        self.on_button_press = on_button_press
        self.is_initialized = False

    def initialize(self) -> bool:
        """
        Initialize GPIO for button input.

        Returns:
            True if initialization successful, False otherwise
        """
        if not GPIO:
            logger.error("RPi.GPIO not available")
            return False

        try:
            # Set up GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Set up button press event (falling edge = button press)
            GPIO.add_event_detect(
                self.BUTTON_PIN,
                GPIO.FALLING,
                callback=self._on_button_event,
                bouncetime=self.DEBOUNCE_TIME,
            )

            self.is_initialized = True
            logger.info(f"GPIO button initialized on pin {self.BUTTON_PIN}")
            return True

        except Exception as e:
            logger.error(f"GPIO initialization failed: {e}")
            return False

    def _on_button_event(self, channel: int) -> None:
        """
        Internal callback for button press event.

        Args:
            channel: GPIO channel that triggered the event
        """
        logger.debug(f"Button pressed on GPIO {channel}")

        if self.on_button_press:
            try:
                self.on_button_press()
            except Exception as e:
                logger.error(f"Error executing button callback: {e}")

    def set_button_callback(self, callback: Callable) -> None:
        """
        Set or update the button press callback.

        Args:
            callback: Function to call on button press
        """
        self.on_button_press = callback
        logger.debug("Button callback updated")

    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        if not GPIO:
            return

        try:
            GPIO.cleanup(self.BUTTON_PIN)
            self.is_initialized = False
            logger.info("GPIO button cleaned up")
        except Exception as e:
            logger.error(f"GPIO cleanup failed: {e}")

    def __del__(self):
        """Ensure GPIO is cleaned up on object destruction."""
        self.cleanup()
