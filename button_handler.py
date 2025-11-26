"""
Button Handler module for the Disability Support System.
Handles GPIO button input for recording control.
Based on ReSpeaker 2-Mics Pi HAT specifications - POLLING approach.
"""

import logging
import time
import threading

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

    NOTE: This implementation uses POLLING instead of event detection
    to avoid "Failed to add edge detection" errors that occur when
    the GPIO pin state is locked from previous runs.
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
        self.last_state = GPIO.HIGH if GPIO_AVAILABLE else 1

        # Threading for polling
        self.polling_thread = None
        self.polling_active = False

        logger.info(f"ButtonHandler created for GPIO pin {self.pin} (polling mode)")

    def initialize(self):
        """
        Initialize GPIO for button input using polling approach.
        This avoids edge detection issues.

        Returns:
            True if initialization successful, False otherwise
        """
        if not GPIO_AVAILABLE:
            logger.warning("GPIO not available - running in simulation mode")
            return False

        try:
            # Set GPIO numbering mode to BCM
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

            # Configure the button pin - INPUT with PULL-UP
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            logger.debug(f"GPIO pin {self.pin} configured: INPUT with PULL-UP")

            # Read initial state
            self.last_state = GPIO.input(self.pin)
            logger.debug(f"Initial button state: {'HIGH (not pressed)' if self.last_state else 'LOW (pressed)'}")

            self.is_initialized = True

            # Start polling thread if callback is provided
            if self.callback:
                self._start_polling()

            logger.info(f"GPIO button initialized successfully on pin {self.pin}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            logger.exception("Full traceback:")
            return False

    def _start_polling(self):
        """Start the polling thread to monitor button state."""
        if self.polling_active:
            return

        self.polling_active = True
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        logger.debug("Button polling thread started")

    def _stop_polling(self):
        """Stop the polling thread."""
        if self.polling_active:
            self.polling_active = False
            if self.polling_thread:
                self.polling_thread.join(timeout=1.0)
            logger.debug("Button polling thread stopped")

    def _polling_loop(self):
        """
        Polling loop that continuously monitors button state.
        Runs in a separate thread.
        """
        logger.debug("Polling loop started")

        while self.polling_active and self.is_initialized:
            try:
                current_state = GPIO.input(self.pin)

                # Detect FALLING edge (HIGH -> LOW = button pressed)
                if self.last_state == GPIO.HIGH and current_state == GPIO.LOW:
                    current_time = time.time()

                    # Software debouncing
                    if current_time - self.last_press_time >= (self.debounce_ms / 1000.0):
                        self.last_press_time = current_time
                        logger.info(f"Button pressed on GPIO {self.pin}")

                        # Call the callback
                        if self.callback:
                            try:
                                self.callback()
                            except Exception as e:
                                logger.error(f"Error in button callback: {e}")
                                logger.exception("Callback exception:")

                self.last_state = current_state

                # Sleep briefly to avoid consuming too much CPU
                time.sleep(0.01)  # Poll every 10ms

            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(0.1)

        logger.debug("Polling loop exited")

    def set_callback(self, callback):
        """
        Set or update the callback function for button presses.
        Will start polling thread if not already running.

        Args:
            callback: Function to call when button is pressed
        """
        self.callback = callback
        logger.info("Button callback updated")

        # Start polling if initialized and not already polling
        if self.is_initialized and not self.polling_active:
            self._start_polling()

    def wait_for_press(self, timeout=None):
        """
        Block and wait for a button press.
        Uses direct polling, not the callback thread.

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
            start_time = time.time()
            last_state = GPIO.input(self.pin)

            while True:
                current_state = GPIO.input(self.pin)

                # Detect FALLING edge (button pressed)
                if last_state == GPIO.HIGH and current_state == GPIO.LOW:
                    logger.info("Button press detected!")
                    time.sleep(self.debounce_ms / 1000.0)  # Debounce delay
                    return True

                last_state = current_state

                # Check timeout
                if timeout is not None:
                    if time.time() - start_time > timeout:
                        logger.debug("Button wait timed out")
                        return False

                time.sleep(0.01)  # Poll every 10ms

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
            # Stop polling thread first
            self._stop_polling()

            # Cleanup the GPIO pin
            if self.is_initialized:
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
