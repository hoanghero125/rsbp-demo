#!/usr/bin/env python3
"""
Simple test to check what the button actually reads.
This will help us verify the correct logic.
"""

import RPi.GPIO as GPIO
import time

BUTTON_PIN = 17

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("="*60)
print("SIMPLE BUTTON TEST")
print("="*60)
print(f"Reading GPIO pin {BUTTON_PIN}...")
print("Press and hold the button, then release it")
print("Press Ctrl+C to exit")
print()

try:
    while True:
        state = GPIO.input(BUTTON_PIN)
        print(f"Pin state: {state} ({'HIGH' if state == 1 else 'LOW'})", end='\r')
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nCleaning up...")
    GPIO.cleanup(BUTTON_PIN)
    print("Done!")
