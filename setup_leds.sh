#!/bin/bash
# Quick setup script for LED functionality on ReSpeaker 2-Mics HAT

set -e  # Exit on error

echo "=========================================="
echo "ReSpeaker 2-Mics HAT LED Setup Script"
echo "=========================================="
echo ""

# Step 1: Check if SPI is enabled
echo "Step 1: Checking SPI interface..."
if [ -e /dev/spidev0.0 ]; then
    echo "✓ SPI interface is enabled"
else
    echo "✗ SPI interface is NOT enabled"
    echo ""
    echo "Enabling SPI interface..."
    sudo raspi-config nonint do_spi 0

    if [ $? -eq 0 ]; then
        echo "✓ SPI enabled successfully"
        echo ""
        echo "⚠️  REBOOT REQUIRED!"
        echo "Please run: sudo reboot"
        echo "Then run this script again after reboot."
        exit 0
    else
        echo "✗ Failed to enable SPI"
        echo "Please enable manually: sudo raspi-config → Interfacing Options → SPI"
        exit 1
    fi
fi

# Step 2: Check user in spi group
echo ""
echo "Step 2: Checking SPI permissions..."
if groups $USER | grep -q "\bspi\b"; then
    echo "✓ User $USER is in spi group"
else
    echo "✗ User $USER is NOT in spi group"
    echo "Adding user to spi group..."
    sudo usermod -a -G spi $USER

    if [ $? -eq 0 ]; then
        echo "✓ User added to spi group successfully"
        echo ""
        echo "⚠️  LOGOUT/LOGIN REQUIRED!"
        echo "Please logout and login again (or reboot)"
        echo "Then run this script again."
        exit 0
    else
        echo "✗ Failed to add user to spi group"
        exit 1
    fi
fi

# Step 3: Install apa102-pi library
echo ""
echo "Step 3: Installing apa102-pi library..."
cd ~/rsbp-demo

if [ ! -d "venv" ]; then
    echo "✗ Virtual environment not found!"
    echo "Please create venv first: python3 -m venv --system-site-packages venv"
    exit 1
fi

source venv/bin/activate

if python3 -c "import apa102" 2>/dev/null; then
    echo "✓ apa102-pi is already installed"
else
    echo "Installing apa102-pi..."
    pip install apa102-pi

    if [ $? -eq 0 ]; then
        echo "✓ apa102-pi installed successfully"
    else
        echo "✗ Failed to install apa102-pi"
        exit 1
    fi
fi

# Step 4: Test LED
echo ""
echo "Step 4: Testing LED controller..."
if python3 led_controller.py; then
    echo ""
    echo "✓ LED test completed successfully!"
else
    echo ""
    echo "✗ LED test failed!"
    echo "Check the error messages above"
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "✓ LED Setup Complete!"
echo "=========================================="
echo ""
echo "LED is now ready to use!"
echo ""
echo "Color states:"
echo "  🟢 Green (IDLE)       - Waiting for input"
echo "  🔴 Red (RECORDING)    - Recording audio"
echo "  🟡 Yellow (CAPTURING) - Taking photo"
echo "  🔵 Cyan (PROCESSING)  - Processing with AI"
echo "  🔵 Blue (SPEAKING)    - Playing audio"
echo "  🔴 Red Blink (ERROR)  - System error"
echo ""
echo "Next steps:"
echo "  1. Run main.py: python3 main.py"
echo "  2. Observe LED colors change during operation"
echo "  3. Enjoy visual feedback! 🎨"
echo ""
