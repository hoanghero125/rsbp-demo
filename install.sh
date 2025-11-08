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
echo "Step 3: Install audio packages..."
apt-get install -y alsa-utils pulseaudio python3-pyaudio portaudio19-dev

echo ""
echo "Step 4: Install camera tools..."
apt-get install -y libraspberrypi-bin libraspberrypi-dev libraspberrypi0
apt-get install -y rpicam-apps

echo ""
echo "Step 5: Install GPIO library..."
pip3 install RPi.GPIO

echo ""
echo "Step 6: Install Python requirements..."
pip3 install -r requirements.txt

echo ""
echo "Step 7: Create recording directories..."
mkdir -p /home/pi/recordings
mkdir -p /home/pi/Pictures
chown pi:pi /home/pi/recordings
chown pi:pi /home/pi/Pictures
chmod 755 /home/pi/recordings
chmod 755 /home/pi/Pictures

echo ""
echo "Step 8: Copy application files..."
cp rsbp-system.service /etc/systemd/system/
systemctl daemon-reload

echo ""
echo "Step 9: Configure ReSpeaker (if not already done)..."
echo "Installing ReSpeaker driver..."
git clone https://github.com/respeaker/seeed-voicecard.git /tmp/seeed-voicecard
cd /tmp/seeed-voicecard
bash install.sh
cd - > /dev/null

echo ""
echo "Step 10: Configure sound card..."
# Set ReSpeaker as default input device
echo "PCM card: Setting ReSpeaker as default audio device..."

echo ""
echo "Step 11: Enable services..."
systemctl enable rsbp-system.service

echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Reboot the Raspberry Pi: sudo reboot"
echo "2. Test the system: python3 test_modules.py"
echo "3. Start the service: sudo systemctl start rsbp-system"
echo "4. View logs: journalctl -u rsbp-system -f"
echo ""
echo "To run directly without service:"
echo "  python3 /home/pi/rsbp-demo/main.py"
echo ""
echo "To disable autostart:"
echo "  sudo systemctl disable rsbp-system.service"
echo ""
