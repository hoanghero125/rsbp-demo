"""
LED Controller for ReSpeaker 2-Mics HAT
Controls 3 APA102 RGB LEDs to display system status.
"""

import logging
import time
from threading import Thread

logger = logging.getLogger(__name__)

# Try to import apa102 library
# NOTE: apa102-pi library uses apa102_pi.driver.apa102
try:
    from apa102_pi.driver import apa102
    APA102_AVAILABLE = True
except ImportError:
    APA102_AVAILABLE = False
    logger.warning("apa102 library not found - LED control will be disabled")


class LEDController:
    """
    Controls ReSpeaker 2-Mics HAT LEDs to display system status.

    Hardware: 3x APA102 RGB LEDs

    States and Colors:
    - IDLE: Green - Waiting for user input
    - RECORDING: Red - Recording audio
    - CAPTURING: Yellow - Capturing image
    - PROCESSING: Cyan - Processing with VLM/STT/TTS
    - SPEAKING: Blue (pulsing) - Playing audio response
    - ERROR: Red (blinking) - System error
    """

    # LED color definitions (R, G, B) - values 0-255
    COLORS = {
        'OFF': (0, 0, 0),
        'GREEN': (0, 255, 0),      # IDLE
        'RED': (255, 0, 0),        # RECORDING / ERROR
        'YELLOW': (255, 255, 0),   # CAPTURING
        'CYAN': (0, 255, 255),     # PROCESSING
        'BLUE': (0, 0, 255),       # SPEAKING
        'PURPLE': (128, 0, 128),   # Alternative processing
        'WHITE': (255, 255, 255),  # System ready
    }

    # System states
    STATE_IDLE = 'idle'
    STATE_RECORDING = 'recording'
    STATE_CAPTURING = 'capturing'
    STATE_PROCESSING = 'processing'
    STATE_SPEAKING = 'speaking'
    STATE_ERROR = 'error'

    def __init__(self, num_leds=3):
        """
        Initialize LED controller.

        Args:
            num_leds: Number of LEDs on the board (default: 3)
        """
        self.num_leds = num_leds
        self.strip = None
        self.is_initialized = False
        self.current_state = None
        self.animation_thread = None
        self.animation_running = False

        logger.info(f"LED Controller initialized with {num_leds} LEDs")

    def initialize(self):
        """
        Initialize the APA102 LED strip.

        Returns:
            bool: True if successful, False otherwise
        """
        if not APA102_AVAILABLE:
            logger.warning("apa102 library not available - LED disabled")
            return False

        try:
            # Initialize APA102 strip
            # Parameters: num_led, global_brightness (0-31), order='rgb'
            self.strip = apa102.APA102(num_led=self.num_leds,
                                       global_brightness=10,  # Brightness 0-31 (10 = moderate)
                                       order='rgb')

            # Turn off all LEDs initially
            self.clear()

            self.is_initialized = True
            logger.info("LED strip initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize LED strip: {e}")
            return False

    def set_state(self, state):
        """
        Set LED display based on system state.

        Args:
            state: One of STATE_* constants
        """
        if not self.is_initialized:
            return

        # Stop any running animation
        self.stop_animation()

        self.current_state = state

        try:
            if state == self.STATE_IDLE:
                self.show_idle()
            elif state == self.STATE_RECORDING:
                self.show_recording()
            elif state == self.STATE_CAPTURING:
                self.show_capturing()
            elif state == self.STATE_PROCESSING:
                self.show_processing()
            elif state == self.STATE_SPEAKING:
                self.show_speaking()
            elif state == self.STATE_ERROR:
                self.show_error()
            else:
                logger.warning(f"Unknown state: {state}")

        except Exception as e:
            logger.error(f"Error setting LED state: {e}")

    def show_idle(self):
        """Display IDLE state - solid green."""
        logger.debug("LED: IDLE (Green)")
        self.set_all_leds(self.COLORS['GREEN'])

    def show_recording(self):
        """Display RECORDING state - solid red."""
        logger.debug("LED: RECORDING (Red)")
        self.set_all_leds(self.COLORS['RED'])

    def show_capturing(self):
        """Display CAPTURING state - solid yellow."""
        logger.debug("LED: CAPTURING (Yellow)")
        self.set_all_leds(self.COLORS['YELLOW'])

    def show_processing(self):
        """Display PROCESSING state - rotating cyan."""
        logger.debug("LED: PROCESSING (Rotating Cyan)")
        self.start_animation(self._animate_processing)

    def show_speaking(self):
        """Display SPEAKING state - pulsing blue."""
        logger.debug("LED: SPEAKING (Pulsing Blue)")
        self.start_animation(self._animate_speaking)

    def show_error(self):
        """Display ERROR state - blinking red."""
        logger.debug("LED: ERROR (Blinking Red)")
        self.start_animation(self._animate_error)

    def set_all_leds(self, color):
        """
        Set all LEDs to the same color.

        Args:
            color: RGB tuple (r, g, b)
        """
        if not self.is_initialized or not self.strip:
            return

        try:
            for i in range(self.num_leds):
                self.strip.set_pixel(i, color[0], color[1], color[2])
            self.strip.show()
        except Exception as e:
            logger.error(f"Error setting LEDs: {e}")

    def set_led(self, index, color):
        """
        Set a single LED to a specific color.

        Args:
            index: LED index (0-2)
            color: RGB tuple (r, g, b)
        """
        if not self.is_initialized or not self.strip:
            return

        try:
            if 0 <= index < self.num_leds:
                self.strip.set_pixel(index, color[0], color[1], color[2])
                self.strip.show()
        except Exception as e:
            logger.error(f"Error setting LED {index}: {e}")

    def clear(self):
        """Turn off all LEDs."""
        if not self.is_initialized or not self.strip:
            return

        try:
            self.strip.clear_strip()
            self.strip.show()
        except Exception as e:
            logger.error(f"Error clearing LEDs: {e}")

    def start_animation(self, animation_func):
        """
        Start an LED animation in a background thread.

        Args:
            animation_func: Function to run in background thread
        """
        self.stop_animation()

        self.animation_running = True
        self.animation_thread = Thread(target=animation_func, daemon=True)
        self.animation_thread.start()

    def stop_animation(self):
        """Stop any running animation."""
        if self.animation_running:
            self.animation_running = False
            if self.animation_thread:
                self.animation_thread.join(timeout=1.0)
                self.animation_thread = None

    def _animate_processing(self):
        """Animation for PROCESSING state - rotating cyan lights."""
        while self.animation_running:
            try:
                for i in range(self.num_leds):
                    if not self.animation_running:
                        break

                    # Turn all LEDs off
                    for j in range(self.num_leds):
                        self.strip.set_pixel(j, 0, 0, 0)

                    # Turn on current LED in cyan
                    self.strip.set_pixel(i,
                                       self.COLORS['CYAN'][0],
                                       self.COLORS['CYAN'][1],
                                       self.COLORS['CYAN'][2])
                    self.strip.show()
                    time.sleep(0.2)

            except Exception as e:
                logger.error(f"Error in processing animation: {e}")
                break

    def _animate_speaking(self):
        """Animation for SPEAKING state - pulsing blue."""
        brightness_levels = list(range(0, 256, 15)) + list(range(255, -1, -15))

        while self.animation_running:
            try:
                for brightness in brightness_levels:
                    if not self.animation_running:
                        break

                    # Calculate blue color with varying brightness
                    scaled_blue = int(self.COLORS['BLUE'][2] * brightness / 255)

                    for i in range(self.num_leds):
                        self.strip.set_pixel(i, 0, 0, scaled_blue)

                    self.strip.show()
                    time.sleep(0.03)

            except Exception as e:
                logger.error(f"Error in speaking animation: {e}")
                break

    def _animate_error(self):
        """Animation for ERROR state - blinking red."""
        while self.animation_running:
            try:
                # Turn on red
                self.set_all_leds(self.COLORS['RED'])
                time.sleep(0.3)

                if not self.animation_running:
                    break

                # Turn off
                self.clear()
                time.sleep(0.3)

            except Exception as e:
                logger.error(f"Error in error animation: {e}")
                break

    def test_leds(self):
        """
        Test all LEDs by cycling through colors.
        Useful for debugging and verification.
        """
        if not self.is_initialized:
            logger.warning("LEDs not initialized - cannot test")
            return False

        logger.info("Testing LEDs...")

        try:
            # Test each color
            colors = ['RED', 'GREEN', 'BLUE', 'YELLOW', 'CYAN', 'PURPLE', 'WHITE']

            for color_name in colors:
                logger.info(f"  Testing color: {color_name}")
                self.set_all_leds(self.COLORS[color_name])
                time.sleep(0.5)

            # Test individual LEDs
            logger.info("  Testing individual LEDs")
            for i in range(self.num_leds):
                self.clear()
                self.set_led(i, self.COLORS['WHITE'])
                time.sleep(0.3)

            # Clear at the end
            self.clear()
            logger.info("LED test complete")
            return True

        except Exception as e:
            logger.error(f"LED test failed: {e}")
            return False

    def cleanup(self):
        """Clean up LED resources."""
        logger.info("Cleaning up LED controller")

        # Stop any running animation
        self.stop_animation()

        # Turn off all LEDs
        if self.is_initialized:
            self.clear()

            # Clean up APA102 strip
            if self.strip:
                try:
                    self.strip.cleanup()
                except Exception as e:
                    logger.error(f"Error during LED cleanup: {e}")

        self.is_initialized = False
        logger.info("LED controller cleanup complete")


if __name__ == "__main__":
    """Test LED controller."""
    logging.basicConfig(level=logging.INFO)

    print("Testing LED Controller...")
    led = LEDController(num_leds=3)

    if led.initialize():
        print("LED initialized successfully")

        # Test all LEDs
        led.test_leds()

        # Test states
        states = [
            ('IDLE', led.STATE_IDLE, 2),
            ('RECORDING', led.STATE_RECORDING, 2),
            ('CAPTURING', led.STATE_CAPTURING, 2),
            ('PROCESSING', led.STATE_PROCESSING, 3),
            ('SPEAKING', led.STATE_SPEAKING, 3),
            ('ERROR', led.STATE_ERROR, 2),
        ]

        for name, state, duration in states:
            print(f"Testing {name} state...")
            led.set_state(state)
            time.sleep(duration)

        # Clean up
        led.cleanup()
        print("Test complete!")
    else:
        print("Failed to initialize LED controller")
