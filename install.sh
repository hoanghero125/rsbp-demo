#!/bin/bash

# Disability Support System - Installation Script
# This script automates the installation and setup process on Raspberry Pi

set -e  # Exit on error

echo "=========================================="
echo "Disability Support System - Installation"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Error: Please do not run this script as root"
    echo "Run as: ./install.sh"
    exit 1
fi

echo "Step 1: Updating system packages..."
sudo apt update

echo ""
echo "Step 2: Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y alsa-utils portaudio19-dev
sudo apt install -y rpicam-apps

echo ""
echo "Step 3: Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo "Virtual environment created"
fi

echo ""
echo "Step 4: Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo ""
echo "Step 5: Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env file created from template"
else
    echo ".env file already exists"
fi

echo ""
echo "Step 6: Ensuring directories exist..."
mkdir -p audio images logs
echo "Directories created"

echo ""
echo "Step 7: Setting permissions..."
# Ensure user is in necessary groups
sudo usermod -a -G audio,video,gpio $USER || true

echo ""
echo "Step 8: Testing installation..."
source venv/bin/activate
python3 test_modules.py
TEST_RESULT=$?
deactivate

echo ""
echo "=========================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo "Installation completed successfully!"
else
    echo "Installation completed with warnings"
    echo "Please check test output above"
fi
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review and edit .env if needed"
echo "2. Ensure camera is enabled: sudo raspi-config"
echo "3. Ensure hardware is connected:"
echo "   - ReSpeaker HAT"
echo "   - Camera Module"
echo "   - Button on GPIO pin 17"
echo "   - Speaker"
echo "4. Run the system: python3 main.py"
echo "   (Make sure to activate venv first: source venv/bin/activate)"
echo ""
echo "Optional: Set up as systemd service"
echo "See README.md for instructions"
echo ""
echo "Note: You may need to logout and login again for group changes to take effect"
