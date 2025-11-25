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

        logger.info(f"ButtonHandler created for GPIO pin {self.pin}")

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
            # Step 1: Clean up any existing GPIO state first
            logger.debug("Cleaning up any existing GPIO state...")
            self._cleanup_gpio_state()

            # Step 2: Set GPIO mode to BCM (Broadcom SOC channel numbering)
            # This might fail if another process already set a different mode
            try:
                GPIO.setmode(GPIO.BCM)
                logger.debug("GPIO mode set to BCM")
            except ValueError as e:
                # Mode already set, check if it's BCM
                current_mode = GPIO.getmode()
                if current_mode == GPIO.BCM:
                    logger.debug("GPIO already in BCM mode (OK)")
                else:
                    logger.error(f"GPIO is in wrong mode: {current_mode}. Need BCM mode.")
                    raise

            # Step 3: Disable warnings about GPIO channels already in use
            GPIO.setwarnings(False)

            # Step 4: Set up button pin as input with pull-up resistor
            # Pull-up means button press will pull pin LOW (falling edge)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            logger.debug(f"GPIO pin {self.pin} configured as INPUT with PULL-UP")

            # Step 5: Set up event detection for button press
            GPIO.add_event_detect(
                self.pin,
                GPIO.FALLING,  # Trigger on falling edge (button press)
                callback=self._button_callback,
                bouncetime=self.debounce_ms
            )
            logger.debug(f"Event detection added on pin {self.pin}")

            self.is_initialized = True
            logger.info(f"GPIO initialized successfully on pin {self.pin}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            logger.exception("Full traceback:")
            return False

    def _cleanup_gpio_state(self):
        """
        Clean up any existing GPIO state on our pin.
        This is called before initialization to ensure clean slate.
        """
        try:
            # Try to remove any existing event detection on this pin
            GPIO.remove_event_detect(self.pin)
            logger.debug(f"Removed existing event detection on pin {self.pin}")
        except Exception:
            # No event detection was set, which is fine
            pass

        try:
            # Clean up the specific pin
            GPIO.cleanup(self.pin)
            logger.debug(f"Cleaned up GPIO pin {self.pin}")
        except Exception:
            # Pin wasn't set up, which is fine
            pass

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
            timeout_ms = int(timeout * 1000) if timeout else None
            result = GPIO.wait_for_edge(self.pin, GPIO.FALLING, timeout=timeout_ms)
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
        if not GPIO_AVAILABLE:
            return

        logger.info("Cleaning up button handler...")

        try:
            # Remove event detection first
            if self.is_initialized:
                try:
                    GPIO.remove_event_detect(self.pin)
                    logger.debug(f"Removed event detection on pin {self.pin}")
                except Exception as e:
                    logger.debug(f"Could not remove event detection: {e}")

            # Then cleanup the GPIO pin
            try:
                GPIO.cleanup(self.pin)
                logger.debug(f"Cleaned up GPIO pin {self.pin}")
            except Exception as e:
                logger.debug(f"Could not cleanup GPIO pin: {e}")

            self.is_initialized = False
            logger.info("GPIO cleaned up successfully")

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
