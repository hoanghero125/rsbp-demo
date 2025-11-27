#!/usr/bin/env python3
"""
Simple LED test to verify apa102-pi library is working correctly.
This is a minimal test without the full LEDController class.
"""

import time

print("Testing APA102 LED import and basic functionality...")

try:
    from apa102_pi.driver import apa102
    print("✓ Successfully imported apa102_pi.driver.apa102")
except ImportError as e:
    print(f"✗ Failed to import apa102: {e}")
    exit(1)

try:
    # Initialize strip with 3 LEDs
    print("\nInitializing strip with 3 LEDs...")
    strip = apa102.APA102(num_led=3, global_brightness=10, order='rgb')
    print("✓ Strip initialized successfully")

    # Turn off all LEDs first
    print("\nClearing all LEDs...")
    strip.clear_strip()
    strip.show()
    time.sleep(1)

    # Test RED
    print("\nTesting RED...")
    for i in range(3):
        strip.set_pixel(i, 255, 0, 0)  # Red
    strip.show()
    time.sleep(2)

    # Test GREEN
    print("Testing GREEN...")
    for i in range(3):
        strip.set_pixel(i, 0, 255, 0)  # Green
    strip.show()
    time.sleep(2)

    # Test BLUE
    print("Testing BLUE...")
    for i in range(3):
        strip.set_pixel(i, 0, 0, 255)  # Blue
    strip.show()
    time.sleep(2)

    # Test YELLOW
    print("Testing YELLOW...")
    for i in range(3):
        strip.set_pixel(i, 255, 255, 0)  # Yellow
    strip.show()
    time.sleep(2)

    # Test CYAN
    print("Testing CYAN...")
    for i in range(3):
        strip.set_pixel(i, 0, 255, 255)  # Cyan
    strip.show()
    time.sleep(2)

    # Test individual LEDs
    print("\nTesting individual LEDs...")
    strip.clear_strip()
    strip.show()
    time.sleep(0.5)

    for i in range(3):
        print(f"  LED {i}")
        strip.set_pixel(i, 255, 255, 255)  # White
        strip.show()
        time.sleep(0.5)
        strip.set_pixel(i, 0, 0, 0)  # Off
        strip.show()
        time.sleep(0.3)

    # Clean up
    print("\nCleaning up...")
    strip.clear_strip()
    strip.show()
    strip.cleanup()

    print("✓ All tests passed successfully!")
    print("\nThe LED strip is working correctly! 🎉")

except Exception as e:
    print(f"\n✗ Test failed with error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
