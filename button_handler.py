"""
Button Handler module for the Disability Support System.
Simple direct state checking - no event detection, no threading complexity.
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
    Simple button handler using direct GPIO state reading.

    Button logic (with pull-up resistor):
    - Unpressed: GPIO.input() = 1 (HIGH)
    - Pressed: GPIO.input() = 0 (LOW)
    """

    def __init__(self, callback=None):
        """
        Initialize the button handler.

        Args:
            callback: Function to call when button is pressed.
        """
        self.pin = config.BUTTON_CONFIG["pin"]
        self.debounce_ms = config.BUTTON_CONFIG["debounce_ms"]
        self.callback = callback
        self.is_initialized = False
        self.last_press_time = 0
        self.was_pressed = False

        # Background monitoring thread
        self.monitor_thread = None
        self.monitoring = False

        logger.info(f"ButtonHandler created for GPIO pin {self.pin}")

    def initialize(self):
        """
        Initialize GPIO - just setup the pin as input.

        Returns:
            True if initialization successful, False otherwise
        """
        if not GPIO_AVAILABLE:
            logger.warning("GPIO not available")
            return False

        try:
            # Set GPIO mode
            if GPIO.getmode() is None:
                GPIO.setmode(GPIO.BCM)

            GPIO.setwarnings(False)

            # Setup pin: INPUT with PULL-UP resistor
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            self.is_initialized = True
            logger.info(f"GPIO pin {self.pin} initialized: INPUT with PULL-UP")

            # Start monitoring thread if callback provided
            if self.callback:
                self._start_monitoring()

            return True

        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            return False

    def _start_monitoring(self):
        """Start background thread to monitor button."""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.debug("Button monitoring started")

    def _stop_monitoring(self):
        """Stop monitoring thread."""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=1.0)
            logger.debug("Button monitoring stopped")

    def _monitor_loop(self):
        """Background loop that checks button state."""
        while self.monitoring and self.is_initialized:
            try:
                # Check if button is pressed (pin = 0)
                is_pressed_now = GPIO.input(self.pin) == 0

                # Detect button press (transition from not pressed to pressed)
                if is_pressed_now and not self.was_pressed:
                    current_time = time.time()

                    # Debouncing
                    if current_time - self.last_press_time >= (self.debounce_ms / 1000.0):
                        self.last_press_time = current_time
                        logger.info(f"Button pressed on GPIO {self.pin}")

                        if self.callback:
                            try:
                                self.callback()
                            except Exception as e:
                                logger.error(f"Error in callback: {e}")

                self.was_pressed = is_pressed_now
                time.sleep(0.01)  # Check every 10ms

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(0.1)

    def wait_for_press(self, timeout=None):
        """
        Wait for button press. Simple polling.

        Args:
            timeout: Timeout in seconds, None = wait forever

        Returns:
            True if button pressed, False if timeout
        """
        if not self.is_initialized:
            logger.warning("GPIO not initialized")
            return False

        logger.info(f"Waiting for button press (timeout: {timeout}s)...")
        start_time = time.time()
        was_pressed = GPIO.input(self.pin) == 0

        while True:
            # Check if button is pressed (pin = 0)
            is_pressed = GPIO.input(self.pin) == 0

            # Detect press (transition from not pressed to pressed)
            if is_pressed and not was_pressed:
                logger.info("Button pressed!")
                time.sleep(self.debounce_ms / 1000.0)  # Debounce
                return True

            was_pressed = is_pressed

            # Check timeout
            if timeout and (time.time() - start_time > timeout):
                logger.debug("Timeout")
                return False

            time.sleep(0.01)  # Poll every 10ms

    def is_pressed(self):
        """
        Check if button is currently pressed.

        Returns:
            True if pressed (pin = 0), False otherwise
        """
        if not self.is_initialized:
            return False

        try:
            return GPIO.input(self.pin) == 0
        except:
            return False

    def cleanup(self):
        """Clean up GPIO."""
        if not GPIO_AVAILABLE:
            return

        logger.info("Cleaning up button handler...")

        self._stop_monitoring()

        if self.is_initialized:
            try:
                GPIO.cleanup(self.pin)
                logger.debug(f"Cleaned up GPIO pin {self.pin}")
            except:
                pass

            self.is_initialized = False

    def set_callback(self, callback):
        """Set callback for button presses."""
        self.callback = callback
        if self.is_initialized and not self.monitoring:
            self._start_monitoring()

    def test_button(self, timeout=5):
        """Test button by waiting for press."""
        logger.info(f"Testing button - press within {timeout} seconds")
        return self.wait_for_press(timeout=timeout)
