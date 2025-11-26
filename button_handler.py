"""
Button Handler module for the Disability Support System.
Handles GPIO button input for recording control.
Based on ReSpeaker 2-Mics Pi HAT official specifications.
"""

import logging
import time

import config

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    logger.warning("RPi.GPIO not available - button functionality will be simulated")
    GPIO_AVAILABLE = False


class ButtonHandler:
    """
    Handles GPIO button input for controlling recording start/stop.

    ReSpeaker 2-Mics Pi HAT Button Specifications:
    - GPIO Pin: 17 (BCM mode)
    - Pull-up resistor: Yes (built-in to RPi)
    - Active state: LOW (button pressed = GPIO reads 0)
    - Idle state: HIGH (button not pressed = GPIO reads 1)
    - Edge detection: FALLING (HIGH → LOW when button is pressed)
    """

    def __init__(self, callback=None):
        """
        Initialize the button handler.

        Args:
            callback: Function to call when button is pressed. Should accept no arguments.
        """
        self.pin = config.BUTTON_CONFIG["pin"]
        self.debounce_ms = config.BUTTON_CONFIG["debounce_ms"]
        self.callback = callback
        self.is_initialized = False
        self.last_press_time = 0

        logger.info(f"ButtonHandler created for GPIO pin {self.pin}")

    def initialize(self):
        """
        Initialize GPIO and set up button.
        Simple implementation based on ReSpeaker 2-Mics Pi HAT specifications.

        Returns:
            True if initialization successful, False otherwise
        """
        if not GPIO_AVAILABLE:
            logger.warning("GPIO not available - running in simulation mode")
            return False

        try:
            # Set GPIO numbering mode to BCM (Broadcom chip-specific pin numbers)
            current_mode = GPIO.getmode()
            if current_mode is None:
                GPIO.setmode(GPIO.BCM)
                logger.debug("GPIO mode set to BCM")
            elif current_mode == GPIO.BCM:
                logger.debug("GPIO already in BCM mode")
            else:
                logger.error(f"GPIO in incompatible mode: {current_mode}")
                return False

            # Disable GPIO warnings
            GPIO.setwarnings(False)

            # Configure the button pin
            # GPIO.IN = Input mode
            # GPIO.PUD_UP = Pull-up resistor (pin reads HIGH when button not pressed)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            logger.debug(f"GPIO pin {self.pin} configured: INPUT with PULL-UP")

            # Add event detection for button press
            # GPIO.FALLING = Detect when pin goes from HIGH to LOW (button pressed)
            # bouncetime = Ignore additional triggers for this many milliseconds
            GPIO.add_event_detect(
                self.pin,
                GPIO.FALLING,
                callback=self._button_callback,
                bouncetime=self.debounce_ms
            )
            logger.debug(f"Event detection added: FALLING edge, {self.debounce_ms}ms debounce")

            self.is_initialized = True
            logger.info(f"GPIO button initialized successfully on pin {self.pin}")
            return True

        except RuntimeError as e:
            logger.error(f"GPIO RuntimeError: {e}")
            logger.info("Attempting to clean up and retry...")

            # Try to cleanup and retry once
            try:
                GPIO.cleanup(self.pin)
                time.sleep(0.2)

                # Retry initialization
                GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(
                    self.pin,
                    GPIO.FALLING,
                    callback=self._button_callback,
                    bouncetime=self.debounce_ms
                )

                self.is_initialized = True
                logger.info("GPIO button initialized successfully (retry)")
                return True

            except Exception as retry_error:
                logger.error(f"Retry failed: {retry_error}")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            logger.exception("Full traceback:")
            return False

    def _button_callback(self, channel):
        """
        Internal callback triggered by GPIO event (FALLING edge).
        Called automatically when button is pressed.

        Args:
            channel: GPIO channel number (provided by RPi.GPIO)
        """
        current_time = time.time()

        # Additional software debouncing (in addition to hardware bouncetime)
        if current_time - self.last_press_time < (self.debounce_ms / 1000.0):
            logger.debug("Button press ignored (debounce)")
            return

        self.last_press_time = current_time
        logger.info(f"Button pressed on GPIO {channel}")

        # Call user-provided callback
        if self.callback:
            try:
                self.callback()
            except Exception as e:
                logger.error(f"Error in button callback: {e}")
                logger.exception("Callback exception:")

    def set_callback(self, callback):
        """
        Set or update the callback function for button presses.

        Args:
            callback: Function to call when button is pressed
        """
        self.callback = callback
        logger.info("Button callback updated")

    def wait_for_press(self, timeout=None):
        """
        Block and wait for a button press.
        Used for testing and synchronous button operations.

        Args:
            timeout: Optional timeout in seconds. None means wait forever.

        Returns:
            True if button was pressed, False if timeout occurred
        """
        if not GPIO_AVAILABLE or not self.is_initialized:
            logger.warning("GPIO not available or not initialized")
            return False

        try:
            logger.info(f"Waiting for button press (timeout: {timeout}s)...")
            timeout_ms = int(timeout * 1000) if timeout else None

            # Wait for FALLING edge (button press)
            result = GPIO.wait_for_edge(self.pin, GPIO.FALLING, timeout=timeout_ms)

            if result is not None:
                logger.info("Button press detected!")
                return True
            else:
                logger.debug("Button wait timed out")
                return False

        except Exception as e:
            logger.error(f"Error waiting for button press: {e}")
            return False

    def is_pressed(self):
        """
        Check if button is currently pressed (polling mode).
        Returns True if button is being held down right now.

        Returns:
            True if button is pressed, False otherwise
        """
        if not GPIO_AVAILABLE or not self.is_initialized:
            return False

        try:
            # With pull-up resistor: GPIO.LOW (0) means button is pressed
            return GPIO.input(self.pin) == GPIO.LOW
        except Exception as e:
            logger.error(f"Error reading button state: {e}")
            return False

    def cleanup(self):
        """
        Clean up GPIO resources.
        Should be called when shutting down the system.
        """
        if not GPIO_AVAILABLE:
            return

        logger.info("Cleaning up button handler...")

        try:
            if self.is_initialized:
                # Remove event detection
                try:
                    GPIO.remove_event_detect(self.pin)
                    logger.debug(f"Removed event detection on pin {self.pin}")
                except Exception as e:
                    logger.debug(f"Could not remove event detection: {e}")

                # Cleanup the specific pin
                try:
                    GPIO.cleanup(self.pin)
                    logger.debug(f"Cleaned up GPIO pin {self.pin}")
                except Exception as e:
                    logger.debug(f"Could not cleanup GPIO pin: {e}")

                self.is_initialized = False
                logger.info("Button handler cleanup complete")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def test_button(self, timeout=5):
        """
        Test button functionality by waiting for a press.

        Args:
            timeout: How long to wait for button press (seconds)

        Returns:
            True if button press detected, False otherwise
        """
        logger.info(f"Testing button - press within {timeout} seconds")
        return self.wait_for_press(timeout=timeout)
