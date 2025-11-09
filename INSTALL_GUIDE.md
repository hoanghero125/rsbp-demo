# Installation Guide - Disability Support System

Complete step-by-step installation guide for Raspberry Pi.

## Prerequisites

### Hardware
- Raspberry Pi 3 Model B+ (or newer: 4, 5)
- ReSpeaker 2-Microphone HAT v2
- Raspberry Pi Camera Module v3
- GPIO button (connected to pin 17)
- Speaker (connected to ReSpeaker HAT)
- Micro SD card (16GB minimum)
- Internet connection

### Software
- Raspberry Pi OS (Debian-based, latest version recommended)
- SSH access to Raspberry Pi

## Installation Overview

The installation has been optimized to avoid common Debian/Raspberry Pi OS issues:

### Key Changes from Original Installation

1. **Externally-managed-environment Error Fix**
   - All Python packages installed via `apt-get` where available
   - Avoids `--break-system-packages` flag
   - Uses system-managed Python packages for RPi.GPIO and requests

2. **Build Dependencies**
   - Added `build-essential`, `libatlas-base-dev`, `libjack-jackd2-dev`
   - PyAudio needs these to compile from source if binary unavailable

3. **ReSpeaker Device Tree**
   - Detection prevents duplicate installation
   - Device tree overlay modifications require reboot
   - Official Seeed installer handles kernel module loading

4. **Simplified requirements.txt**
   - Only `requests` (pure Python library)
   - RPi.GPIO installed via apt-get
   - PyAudio installed via apt-get

## Step-by-Step Installation

### Step 1: Prepare Your Raspberry Pi

Update your system to latest version:

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

Enable required interfaces (camera, SPI for LEDs):

```bash
sudo raspi-config
```

Navigate to:
- **Interface Options** → **Camera** → Enable
- **Interface Options** → **SPI** → Enable (for ReSpeaker LEDs)
- Save and exit

### Step 2: Clone/Copy Project Files

Transfer the project to your Raspberry Pi:

```bash
# Option A: Using git
git clone <repository-url> /home/pi/rsbp-demo

# Option B: Using SCP
scp -r rsbp-demo pi@<your-pi-ip>:/home/pi/
```

Navigate to project:

```bash
cd /home/pi/rsbp-demo
```

### Step 3: Run Installation Script

Run the automated installation script:

```bash
sudo bash install.sh
```

This script will:

1. **Update system packages** (apt-get update/upgrade)
2. **Install Python tools** (python3, pip, python3-dev)
3. **Install audio dependencies**
   - Build tools: build-essential, libatlas-base-dev, libjack-jackd2-dev
   - Audio libraries: alsa-utils, pulseaudio, portaudio19-dev
   - Python audio: python3-pyaudio
4. **Install camera tools** (libraspberrypi-bin, rpicam-apps)
5. **Install Python packages** (python3-rpi.gpio, python3-requests)
6. **Verify Python dependencies** (check imports)
7. **Create directories** (/home/pi/recordings, /home/pi/Pictures)
8. **Install systemd service** (rsbp-system.service)
9. **Install ReSpeaker driver**
   - Clones seeed-voicecard repository
   - Runs official installation script
   - Modifies device tree overlay
10. **Enable system service** (autostart on boot)

Expected output:
```
==================================================
Disability Support System - Installation Script
==================================================

Step 1: Update system packages...
Step 2: Install Python dependencies...
...
Step 10: Enable system service...
✓ Service enabled for autostart

==================================================
Installation Complete!
==================================================
```

### Step 4: Reboot (IMPORTANT)

The ReSpeaker device tree overlay requires a reboot to load:

```bash
sudo reboot
```

Wait 1-2 minutes for Raspberry Pi to restart.

### Step 5: Verify Audio Devices

After reboot, check that audio devices are detected:

```bash
# List input devices (should show ReSpeaker)
arecord -l

# List output devices (should show ReSpeaker)
aplay -l
```

Expected output:
```
**** List of CAPTURE Hardware Devices ****
card 1: seeed2micvoicec [seeed-2mic-voicecard], device 0: ...
  Subdevices: 1/1
  Subdevice #0: subdevice #0

**** List of PLAYBACK Hardware Devices ****
card 1: seeed2micvoicec [seeed-2mic-voicecard], device 0: ...
```

### Step 6: Test Python Dependencies

Verify all required Python packages are available:

```bash
python3 test_modules.py
```

Expected output (all tests passing):
```
==================================================
Disability Support System - Module Test Suite
==================================================

Testing module imports...
✓ AudioRecorder imported successfully
✓ ImageCapture imported successfully
✓ AudioPlayback imported successfully
✓ LLMClient imported successfully
✓ ButtonHandler imported successfully
✓ Config imported successfully

Testing configuration...
✓ Configuration loaded successfully

...

==============================
TEST SUMMARY
==============================
✓ PASS: Imports
✓ PASS: Configuration
✓ PASS: AudioRecorder
✓ PASS: ImageCapture
✓ PASS: AudioPlayback
✓ PASS: LLMClient
✓ PASS: ButtonHandler
✓ PASS: Directories

Results: 8/8 tests passed
==============================
```

### Step 7: Start the Service

Start the system service:

```bash
sudo systemctl start rsbp-system
```

Check service status:

```bash
sudo systemctl status rsbp-system
```

Expected output:
```
● rsbp-system.service - Disability Support System (RSBP)
     Loaded: loaded (/etc/systemd/system/rsbp-system.service; enabled; ...)
     Active: active (running) since ...
     Main PID: 1234 (python3)
```

### Step 8: Monitor Logs

View real-time logs to verify operation:

```bash
journalctl -u rsbp-system -f
```

You should see:
```
Nov 08 12:34:56 raspberrypi rsbp-system[1234]: ============================================================
Nov 08 12:34:56 raspberrypi rsbp-system[1234]: Initializing Disability Support System
Nov 08 12:34:56 raspberrypi rsbp-system[1234]: ============================================================
Nov 08 12:34:56 raspberrypi rsbp-system[1234]: System initialization complete
Nov 08 12:34:56 raspberrypi rsbp-system[1234]: System ready and listening for button presses
```

## Installation Issues & Solutions

### Issue 1: "externally-managed-environment" Error

**Error Message:**
```
error: externally-managed-environment
This environment is externally managed
```

**Cause:** Modern Debian/Raspberry Pi OS prevent pip from installing globally.

**Solution:** Fixed in new install.sh - uses `apt-get` for all packages instead of pip.

**Verification:**
```bash
python3 -c "import RPi.GPIO; print('OK')"
python3 -c "import requests; print('OK')"
```

### Issue 2: ReSpeaker Not Detected

**Error Message:**
```
No device found when listing audio devices
arecord -l shows no ReSpeaker
```

**Causes:**
- Device tree overlay not loaded (needs reboot)
- ReSpeaker not properly seated
- Wrong USB connection

**Solution:**
1. Ensure ReSpeaker HAT is properly aligned and seated
2. Reboot: `sudo reboot`
3. Check device tree loaded: `cat /boot/firmware/config.txt | grep seeed`
4. Check kernel module: `lsmod | grep snd_soc_seeed`

**Debug:**
```bash
# Check device tree overlay
dtc -I fs /proc/device-tree | grep -i seeed

# Check kernel messages
dmesg | grep -i seeed

# Reload sound modules
sudo rmmod snd_soc_seeed2micvoicecard
sudo modprobe snd_soc_seeed2micvoicecard
```

### Issue 3: Camera Not Working

**Error Message:**
```
Image capture error: rpicam-jpeg not found
```

**Cause:** Camera not enabled or not connected.

**Solution:**
1. Enable camera: `sudo raspi-config` → Interface Options → Camera → Enable
2. Check connection: Look at CSI ribbon cable
3. Reboot: `sudo reboot`

**Verification:**
```bash
# Test camera
raspistill -o test.jpg

# List cameras
libcamera-hello --list-cameras
```

### Issue 4: GPIO Button Not Responding

**Error Message:**
```
Failed to initialize GPIO button handler
```

**Cause:** GPIO access issues or wrong pin configuration.

**Solution:**
1. Check GPIO permissions:
   ```bash
   sudo usermod -a -G gpio pi
   ```
2. Reboot: `sudo reboot`
3. Verify pin 17: `gpio readall` (should show BCM 17)

**Debug:**
```bash
# Manual GPIO test
python3 << 'EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print("GPIO 17 value:", GPIO.input(17))
GPIO.cleanup()
EOF
```

### Issue 5: PyAudio Build Fails

**Error Message:**
```
error: Microsoft Visual C++ 14.0 or greater is required
Or: cannot find portaudio.h
```

**Cause:** Missing build dependencies or portaudio.

**Solution:** Already fixed in install.sh - installs:
- `build-essential`
- `libatlas-base-dev`
- `libjack-jackd2-dev`
- `portaudio19-dev`

**If still failing:**
```bash
# Install precompiled PyAudio
sudo apt-get install python3-pyaudio

# Verify
python3 -c "import pyaudio; print('OK')"
```

### Issue 6: Service Fails to Start

**Error Message:**
```
systemctl status rsbp-system shows failed
```

**Solutions:**

Check logs:
```bash
journalctl -u rsbp-system -n 50
```

Common causes:
1. Python import errors - run `python3 test_modules.py`
2. Directory permission issues - check `/home/pi/recordings` ownership
3. GPIO permission - add user to gpio group
4. File not found - verify project files copied correctly

Fix permissions:
```bash
sudo chown -R pi:pi /home/pi/rsbp-demo
sudo chown -R pi:pi /home/pi/recordings
sudo usermod -a -G gpio pi
```

### Issue 7: API Connection Timeout

**Error Message:**
```
LLM API error: Connection timeout
```

**Cause:** API unreachable or network issue.

**Solution:**
1. Check internet: `ping 8.8.8.8`
2. Test API: `curl http://203.162.88.105/pvlm-api`
3. Check firewall rules
4. Verify URL in config.py

## Verification Checklist

After installation, verify everything works:

- [ ] Raspberry Pi rebooted
- [ ] Audio devices detected (`arecord -l`, `aplay -l`)
- [ ] Camera working (`raspistill -o test.jpg`)
- [ ] Tests pass (`python3 test_modules.py`)
- [ ] Service running (`systemctl status rsbp-system`)
- [ ] Logs show no errors (`journalctl -u rsbp-system`)
- [ ] Button can trigger events (check GPIO pin 17)
- [ ] API reachable (`curl http://203.162.88.105/pvlm-api`)

## Manual Installation (If Automated Fails)

If `install.sh` fails, you can install manually:

```bash
# 1. Update system
sudo apt-get update
sudo apt-get upgrade -y

# 2. Install dependencies
sudo apt-get install -y python3 python3-pip python3-dev
sudo apt-get install -y build-essential libatlas-base-dev libjack-jackd2-dev
sudo apt-get install -y alsa-utils pulseaudio portaudio19-dev python3-pyaudio
sudo apt-get install -y libraspberrypi-bin libraspberrypi-dev libraspberrypi0 rpicam-apps
sudo apt-get install -y python3-rpi.gpio python3-requests

# 3. Create directories
mkdir -p /home/pi/recordings /home/pi/Pictures

# 4. Install ReSpeaker driver
git clone https://github.com/respeaker/seeed-voicecard.git /tmp/seeed-voicecard
cd /tmp/seeed-voicecard
sudo bash install.sh
cd -

# 5. Copy service file
sudo cp rsbp-system.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rsbp-system

# 6. Reboot
sudo reboot
```

## Post-Installation Configuration

### Customize Settings

Edit `config.py` to customize:
- Microphone device index
- Recording directory
- Camera resolution
- Button GPIO pin
- API endpoint
- Logging level

```bash
nano config.py
```

Then restart:
```bash
sudo systemctl restart rsbp-system
```

### Enable Autostart

Service is already enabled by default. To disable:

```bash
sudo systemctl disable rsbp-system.service
```

To enable:

```bash
sudo systemctl enable rsbp-system.service
```

### Run Without Service

For development/testing:

```bash
python3 main.py
```

Press Ctrl+C to stop.

## Troubleshooting Commands

Quick reference for common diagnostic commands:

```bash
# System info
uname -a
cat /etc/os-release

# Check audio
arecord -l
aplay -l
alsamixer

# Check camera
libcamera-hello --list-cameras
raspistill -o test.jpg

# Check GPIO
gpio readall
python3 -c "import RPi.GPIO; print('GPIO OK')"

# Check Python imports
python3 -c "import requests; print('requests OK')"
python3 -c "import pyaudio; print('PyAudio OK')"

# Check service
systemctl status rsbp-system
journalctl -u rsbp-system -n 100

# Check disk space
df -h

# Check temperature
vcgencmd measure_temp

# Test API
curl http://203.162.88.105/pvlm-api
```

## Support Resources

- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [ReSpeaker Documentation](https://wiki.seeedstudio.com/respeaker_2_mics_pi_hat_raspberry_v2/)
- [System README](README.md)
- [Quick Start Guide](QUICKSTART.md)

## Next Steps

Once installation is complete:

1. Read [QUICKSTART.md](QUICKSTART.md) for operation instructions
2. Review [README.md](README.md) for detailed documentation
3. Check [config.py](config.py) for configuration options
4. Run `python3 test_modules.py` anytime to verify system health

---

Installation complete! Your Disability Support System is ready to use.
