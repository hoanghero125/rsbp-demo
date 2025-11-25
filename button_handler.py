"""
Button Handler module for the Disability Support System.
Handles GPIO button input for recording control using RPi.GPIO.
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
    IMPORTANT: Button on GPIO pin 17 (BCM mode) with 500ms debounce.
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

        logger.info(f"ButtonHandler initialized for GPIO pin {self.pin}")

    def initialize(self):
        """
        Initialize GPIO and set up button event detection.
        IMPORTANT: Must be called before button can be used.

        Returns:
            True if initialization successful, False otherwise
        """
        if not GPIO_AVAILABLE:
            logger.warning("GPIO not available - running in simulation mode")
            return False

        try:
            # IMPORTANT: Set GPIO mode to BCM (Broadcom SOC channel numbering)
            GPIO.setmode(GPIO.BCM)

            # Disable warnings about GPIO channels already in use
            GPIO.setwarnings(False)

            # IMPORTANT: Set up button pin as input with pull-up resistor
            # Pull-up means button press will pull pin LOW (falling edge)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Remove any existing event detection on this pin (from previous runs)
            try:
                GPIO.remove_event_detect(self.pin)
            except Exception:
                pass  # Pin may not have event detection, which is fine

            # Set up event detection for button press
            GPIO.add_event_detect(
                self.pin,
                GPIO.FALLING,  # Trigger on falling edge (button press)
                callback=self._button_callback,
                bouncetime=self.debounce_ms
            )

            self.is_initialized = True
            logger.info(f"GPIO initialized successfully on pin {self.pin}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            return False

    def _button_callback(self, channel):
        """
        Internal callback triggered by GPIO event.
        IMPORTANT: Handles debouncing and calls user-provided callback.

        Args:
            channel: GPIO channel number (provided by RPi.GPIO)
        """
        current_time = time.time()

        # Additional software debouncing
        if current_time - self.last_press_time < (self.debounce_ms / 1000.0):
            logger.debug("Button press ignored (debounce)")
            return

        self.last_press_time = current_time

        logger.info(f"Button pressed on GPIO {channel}")

        # Call user-provided callback if set
        if self.callback:
            try:
                self.callback()
            except Exception as e:
                logger.error(f"Error in button callback: {e}")

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
        Block and wait for a button press (for testing/debugging).

        Args:
            timeout: Optional timeout in seconds. None means wait forever.

        Returns:
            True if button was pressed, False if timeout occurred
        """
        if not GPIO_AVAILABLE or not self.is_initialized:
            logger.warning("GPIO not available or not initialized")
            return False

        try:
            logger.info("Waiting for button press...")
            result = GPIO.wait_for_edge(self.pin, GPIO.FALLING, timeout=int(timeout * 1000) if timeout else None)
            return result is not None
        except Exception as e:
            logger.error(f"Error waiting for button press: {e}")
            return False

    def is_pressed(self):
        """
        Check if button is currently pressed (for polling).

        Returns:
            True if button is pressed, False otherwise
        """
        if not GPIO_AVAILABLE or not self.is_initialized:
            return False

        try:
            # Button is pressed when pin reads LOW (due to pull-up resistor)
            return GPIO.input(self.pin) == GPIO.LOW
        except Exception as e:
            logger.error(f"Error reading button state: {e}")
            return False

    def cleanup(self):
        """
        Clean up GPIO resources.
        IMPORTANT: Should be called when shutting down the system.
        """
        if GPIO_AVAILABLE and self.is_initialized:
            try:
                # Remove event detection first
                try:
                    GPIO.remove_event_detect(self.pin)
                except Exception:
                    pass  # Event detection may already be removed

                # Then cleanup the GPIO pin
                GPIO.cleanup(self.pin)
                self.is_initialized = False
                logger.info("GPIO cleaned up")
            except Exception as e:
                logger.error(f"Error during GPIO cleanup: {e}")

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
