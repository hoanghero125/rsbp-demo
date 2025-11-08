# Quick Start Guide - Disability Support System

This guide will get you up and running quickly.

## Prerequisites

- Raspberry Pi 3 Model B+ (or later)
- ReSpeaker 2-Microphone HAT installed
- Raspberry Pi Camera Module V3 connected
- GPIO button wired to pin 17
- Speaker connected to ReSpeaker HAT
- Stable internet connection

## Installation (5-10 minutes)

### Option 1: Automated Installation (Recommended)

```bash
cd /home/pi
git clone <repository-url> rsbp-demo
cd rsbp-demo
sudo bash install.sh
sudo reboot
```

The installation script will:
- Update system packages
- Install Python dependencies
- Configure ReSpeaker
- Set up directories
- Install systemd service

### Option 2: Manual Installation

```bash
# 1. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install dependencies
sudo apt-get install -y python3-pip alsa-utils
pip3 install -r requirements.txt

# 3. Create directories
mkdir -p ~/recordings ~/Pictures

# 4. Install ReSpeaker driver
git clone https://github.com/respeaker/seeed-voicecard.git /tmp/seeed-voicecard
sudo /tmp/seeed-voicecard/install.sh
sudo reboot
```

## Testing

Before deployment, verify everything works:

```bash
python3 test_modules.py
```

This will check:
- All Python modules load correctly
- ReSpeaker audio device is accessible
- Camera system is working
- API endpoints are reachable
- Directory structure is correct

## Running the Application

### Option 1: Manual Execution

```bash
python3 /home/pi/rsbp-demo/main.py
```

Press Ctrl+C to stop.

### Option 2: As a Service (Recommended for Production)

```bash
# Start the service
sudo systemctl start rsbp-system

# View logs in real-time
sudo journalctl -u rsbp-system -f

# Stop the service
sudo systemctl stop rsbp-system

# Check service status
sudo systemctl status rsbp-system
```

### Option 3: At Boot (Autostart)

```bash
# Enable autostart
sudo systemctl enable rsbp-system

# Disable autostart
sudo systemctl disable rsbp-system
```

## Basic Operation

1. **Start Recording**: Press GPIO button (pin 17)
2. **Speak Question**: Ask your question clearly into the microphone
3. **Stop Recording**: Press button again
4. **Processing**: System will:
   - Transcribe your audio to text (STT)
   - Analyze the captured image
   - Generate a text response
   - Convert response to speech (TTS)
5. **Listen to Response**: Audio plays through the speaker

## Troubleshooting

### Audio Not Working

```bash
# Check audio devices
arecord -l  # List input devices (should show ReSpeaker)
aplay -l    # List output devices

# Test recording
arecord -D default -f cd test.wav

# Test playback
aplay test.wav
```

### Camera Not Working

```bash
# Check camera status
raspistill -o test.jpg

# Verify camera is enabled
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

### Button Not Responding

```bash
# Test GPIO
python3 << 'EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print("GPIO 17 value:", GPIO.input(17))
GPIO.cleanup()
EOF
```

### API Connection Issues

```bash
# Test API connectivity
curl -I http://203.162.88.105/pvlm-api

# Check network
ping 8.8.8.8
```

### Permission Denied Errors

```bash
# Ensure pi user owns directories
sudo chown -R pi:pi /home/pi/rsbp-demo
sudo chown -R pi:pi /home/pi/recordings
sudo chown -R pi:pi /home/pi/Pictures

# Add pi user to gpio group
sudo usermod -a -G gpio pi
sudo usermod -a -G audio pi
```

## Monitoring

### View Real-time Logs

```bash
# System service logs
sudo journalctl -u rsbp-system -f

# Application logs
tail -f /var/log/rsbp_system.log
```

### Check Resource Usage

```bash
# Monitor CPU and memory
top

# Monitor disk space
df -h

# Check temperature
vcgencmd measure_temp
```

## Configuration

Edit `config.py` to customize:

```python
# Microphone input device
AUDIO_CONFIG["respeaker_device_index"] = 2

# Recording save location
RECORDING_CONFIG["output_dir"] = "/home/pi/recordings"

# Camera resolution
IMAGE_CONFIG["width"] = 1920
IMAGE_CONFIG["height"] = 1440

# LLM API endpoint
LLM_API_CONFIG["base_url"] = "http://203.162.88.105/pvlm-api"

# GPIO button pin
BUTTON_CONFIG["pin"] = 17

# Logging level
LOGGING_CONFIG["level"] = "INFO"  # DEBUG for verbose logs
```

Then restart the service:

```bash
sudo systemctl restart rsbp-system
```

## File Management

### Clearing Old Recordings

```bash
# Remove recordings older than 7 days
find /home/pi/recordings -mtime +7 -delete

# Remove all recordings
rm /home/pi/recordings/*.wav

# Same for images
rm /home/pi/Pictures/*.jpg
```

### Checking Storage Usage

```bash
# Total usage
du -sh /home/pi/recordings /home/pi/Pictures

# Largest files
du -sh /home/pi/recordings/* | sort -hr | head -10
```

## Performance Optimization

### Reduce Audio Quality (for lower bandwidth)

Edit `config.py`:
```python
AUDIO_CONFIG["sample_rate"] = 8000  # 8kHz instead of 16kHz
```

### Increase Recording Quality

```python
IMAGE_CONFIG["quality"] = 95  # Higher JPEG quality
IMAGE_CONFIG["width"] = 2560
IMAGE_CONFIG["height"] = 1920
```

### Adjust Logging Level

For production, reduce logging verbosity:
```python
LOGGING_CONFIG["level"] = "WARNING"  # Only warnings and errors
```

## Maintenance

### Weekly Tasks

```bash
# Check disk space
df -h

# Review error logs
journalctl -u rsbp-system -p err

# Backup important audio files
tar -czf recordings_backup.tar.gz /home/pi/recordings
```

### Monthly Tasks

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Update Python packages
pip3 install -U pip
pip3 install -r requirements.txt --upgrade

# Clean up old files (older than 30 days)
find /home/pi/recordings -mtime +30 -delete
find /home/pi/Pictures -mtime +30 -delete
```

## Safety

- Always test in a safe environment first
- Keep API credentials secure
- Regularly backup important audio/image data
- Monitor system resource usage
- Check logs for errors regularly

## Getting Help

If you encounter issues:

1. Check the logs: `sudo journalctl -u rsbp-system -n 50`
2. Run tests: `python3 test_modules.py`
3. Check troubleshooting section above
4. Consult README.md for detailed documentation

## Next Steps

- Review [README.md](README.md) for detailed documentation
- Check [CLAUDE.md](CLAUDE.md) for development notes
- Customize [config.py](config.py) for your environment
