# Hardware Testing Guide

This guide helps you test all hardware components independently before the API is ready.

## Quick Start

```bash
cd /home/thuongvv/rsbp-demo
source venv/bin/activate
python3 test_hardware.py
```

## Interactive Menu

When you run the script, you'll see:

```
==============================================================
DISABILITY SUPPORT SYSTEM - HARDWARE TEST
==============================================================

Select a test to run:
1. Test Camera
2. Test Microphone (record 3 seconds)
3. Test Speaker (playback recorded audio)
4. Test Button
5. Test Complete Workflow
6. Run All Tests
0. Exit

Enter choice (0-6):
```

## Individual Tests

### Test 1: Camera
- Captures a test image from the Raspberry Pi Camera
- Saves to `images/` directory
- Shows file size to confirm capture

**What to check:**
- No error messages
- Image file is created in `images/` folder
- File size is reasonable (not 0 bytes)

### Test 2: Microphone
- Records 3 seconds of audio
- Prompts you to speak
- Saves to `audio/` directory

**What to do:**
1. Select option 2
2. When prompted, speak clearly into the ReSpeaker HAT
3. Wait for "SUCCESS" message
4. Note the audio file path

**What to check:**
- Recording starts without errors
- You see the file path printed
- File size is reasonable (not 0 bytes)

### Test 3: Speaker
- Plays back the recorded audio from Test 2
- Uses aplay (ALSA) or PyAudio fallback

**What to do:**
1. First run Test 2 to record audio
2. Then run Test 3
3. Listen for your voice playing back

**What to check:**
- You hear your voice from the speaker
- Audio is clear and understandable
- No distortion or cutting out

### Test 4: Button
- Tests GPIO button on pin 17
- Waits 10 seconds for button press
- Detects falling edge (button press down)

**What to do:**
1. Select option 4
2. Within 10 seconds, press the physical button
3. Watch for "Button press detected!" message

**What to check:**
- Button press is detected immediately
- No need to press multiple times
- Works consistently

### Test 5: Complete Workflow
- Simulates the real system workflow
- Tests button -> record -> capture -> playback

**What to do:**
1. Select option 5
2. Press button once to start recording
3. Speak your question
4. Press button again to stop
5. System captures image automatically
6. Listen to your voice play back

**What to check:**
- Button triggers recording start/stop
- Image is captured when recording stops
- Recorded audio plays back correctly
- All components work together

### Test 6: Run All Tests
- Runs tests 1-4 automatically
- Provides summary at the end

**What to check:**
- All tests show "PASSED" status
- No critical errors
- All hardware is functional

## Common Issues

### Camera Not Working

```bash
# Check if camera is enabled
vcgencmd get_camera

# Should show: supported=1 detected=1

# If not enabled:
sudo raspi-config
# Interface Options -> Camera -> Enable
# Reboot
```

### Microphone Not Recording

```bash
# List audio input devices
arecord -l

# Should show ReSpeaker HAT

# Test manual recording
arecord -D plughw:2,0 -f S16_LE -r 16000 test.wav -d 3
aplay test.wav
```

### Speaker Not Playing

```bash
# List audio output devices
aplay -l

# Should show ReSpeaker HAT or HDMI

# Test manual playback
speaker-test -t wav -c 1
```

### Button Not Responding

```bash
# Check GPIO status
gpio readall

# Verify pin 17 shows as INPUT

# Check user groups
groups

# Should include: gpio, audio, video

# If not, add user to groups:
sudo usermod -a -G gpio,audio,video $USER
# Then logout and login again
```

## File Locations

After testing, you'll find:

- **Images**: `images/capture_YYYYMMDD_HHMMSS.jpg`
- **Audio**: `audio/recording_YYYYMMDD_HHMMSS.wav`
- **Logs**: `logs/system.log` (when running main system)

## Next Steps

Once all hardware tests pass:

1. Verify API is available: `curl http://203.162.88.105/pvlm-api`
2. Run module tests: `python3 test_modules.py`
3. Start the main system: `python3 main.py`

## Tips

- Run hardware tests after any physical changes (reconnecting wires, etc.)
- If a test fails, run it individually to see detailed error messages
- Check `logs/system.log` for detailed debugging information
- Test in a quiet environment for best audio quality
- Ensure good lighting for camera tests
