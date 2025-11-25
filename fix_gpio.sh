#!/bin/bash

# GPIO Fix Script for Disability Support System
# This script fixes GPIO permission issues in existing virtual environments
# by using system-installed RPi.GPIO instead of pip-installed version

set -e  # Exit on error

echo "=========================================="
echo "GPIO Fix Script"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Install system RPi.GPIO package"
echo "2. Recreate virtual environment with system site packages"
echo "3. Reinstall Python dependencies"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "Step 1: Installing system RPi.GPIO package..."
sudo apt update
sudo apt install -y python3-rpi.gpio

echo ""
echo "Step 2: Backing up and removing existing venv..."
if [ -d "venv" ]; then
    if [ -d "venv.backup" ]; then
        echo "Removing old backup..."
        rm -rf venv.backup
    fi
    echo "Creating backup at venv.backup..."
    mv venv venv.backup
    echo "Existing venv backed up"
else
    echo "No existing venv found"
fi

echo ""
echo "Step 3: Creating new virtual environment with system site packages..."
python3 -m venv --system-site-packages venv
echo "Virtual environment created"

echo ""
echo "Step 4: Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Dependencies installed"

echo ""
echo "Step 5: Testing GPIO access..."
python3 << 'PYTEST'
try:
    import RPi.GPIO as GPIO
    print("SUCCESS: RPi.GPIO imported successfully")
    GPIO.setmode(GPIO.BCM)
    print("SUCCESS: GPIO mode set successfully")
    GPIO.cleanup()
    print("SUCCESS: GPIO is working properly!")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
PYTEST

deactivate

echo ""
echo "=========================================="
echo "GPIO fix completed successfully!"
echo "=========================================="
echo ""
echo "You can now run: source venv/bin/activate && python3 test_hardware.py"
echo ""
echo "The old venv is backed up at venv.backup (you can delete it later)"
echo ""
