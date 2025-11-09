#!/bin/bash
# Installation script for Disability Support System
# Run this script with: sudo bash install.sh

set -e

echo "=================================================="
echo "Disability Support System - Installation Script"
echo "=================================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run as root (use sudo)"
    exit 1
fi

echo "Step 1: Update system packages..."
apt-get update
apt-get upgrade -y

echo ""
echo "Step 2: Install Python dependencies..."
apt-get install -y python3 python3-pip python3-dev

echo ""
echo "Step 3: Install build tools and audio dependencies..."
# IMPORTANT: These are required before building PyAudio
apt-get install -y build-essential libatlas-base-dev libjack-jackd2-dev
apt-get install -y alsa-utils pulseaudio portaudio19-dev
apt-get install -y python3-pyaudio

echo ""
echo "Step 4: Install camera tools..."
apt-get install -y libraspberrypi-bin libraspberrypi-dev libraspberrypi0
apt-get install -y rpicam-apps

echo ""
echo "Step 5: Install Python system packages..."
# IMPORTANT: Use apt-get for these to avoid externally-managed-environment errors
# This avoids pip conflicts with system-managed Python
apt-get install -y python3-rpi.gpio python3-requests

echo ""
echo "Step 6: Verify Python dependencies..."
# Verify all required packages are available
echo "Checking installed Python packages..."
python3 -c "import RPi.GPIO; print('✓ RPi.GPIO')" 2>/dev/null || echo "⚠ Warning: RPi.GPIO not found"
python3 -c "import requests; print('✓ requests')" 2>/dev/null || echo "⚠ Warning: requests not found"
python3 -c "import pyaudio; print('✓ PyAudio')" 2>/dev/null || echo "⚠ Warning: PyAudio not found"

echo ""
echo "Step 7: Create recording directories..."
mkdir -p /home/pi/recordings
mkdir -p /home/pi/Pictures
chown pi:pi /home/pi/recordings
chown pi:pi /home/pi/Pictures
chmod 755 /home/pi/recordings
chmod 755 /home/pi/Pictures
echo "✓ Directories created"

echo ""
echo "Step 8: Copy application files..."
cp rsbp-system.service /etc/systemd/system/
systemctl daemon-reload
echo "✓ Service file installed"

echo ""
echo "Step 9: Install and configure ReSpeaker..."
# IMPORTANT: ReSpeaker requires device tree overlay and kernel module
# The official install script handles this
if ! grep -q "seeed-2mic-voicecard" /boot/firmware/config.txt 2>/dev/null; then
    echo "Installing ReSpeaker device tree and drivers..."
    if [ -d /tmp/seeed-voicecard ]; then
        rm -rf /tmp/seeed-voicecard
    fi
    git clone https://github.com/respeaker/seeed-voicecard.git /tmp/seeed-voicecard
    cd /tmp/seeed-voicecard

    # Run the official installation script
    bash install.sh

    cd - > /dev/null
    echo "✓ ReSpeaker installation complete"
    echo "⚠ REBOOT REQUIRED: Device tree changes need reboot to take effect"
else
    echo "✓ ReSpeaker already configured"
fi

echo ""
echo "Step 10: Enable system service..."
systemctl enable rsbp-system.service
echo "✓ Service enabled for autostart"

echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. REBOOT THE SYSTEM (required for ReSpeaker device tree changes):"
echo "   sudo reboot"
echo ""
echo "2. After reboot, verify audio devices:"
echo "   arecord -l    # Check microphone"
echo "   aplay -l      # Check speaker"
echo ""
echo "3. Test the system:"
echo "   python3 test_modules.py"
echo ""
echo "4. Start the service:"
echo "   sudo systemctl start rsbp-system"
echo ""
echo "5. Monitor logs:"
echo "   journalctl -u rsbp-system -f"
echo ""
echo "6. Run directly without service:"
echo "   python3 /home/pi/rsbp-demo/main.py"
echo ""
echo "To disable autostart:"
echo "   sudo systemctl disable rsbp-system.service"
echo ""
