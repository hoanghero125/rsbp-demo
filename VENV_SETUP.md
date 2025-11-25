# Virtual Environment Setup Guide

## IMPORTANT: Manual Setup Only
This guide provides step-by-step manual instructions. DO NOT use any shell scripts.

## Prerequisites

Update system packages:
```bash
sudo apt update
```

## Step 1: Install System Packages

Install RPi.GPIO via system package manager (REQUIRED for GPIO permissions):
```bash
sudo apt install -y python3-rpi.gpio
```

Optional: Install PyAudio as system package (recommended if pip install fails):
```bash
sudo apt install -y python3-pyaudio
```

## Step 2: Create Virtual Environment

**CRITICAL:** You MUST use the `--system-site-packages` flag to access system-installed RPi.GPIO:

```bash
python3 -m venv --system-site-packages venv
```

Why `--system-site-packages`?
- RPi.GPIO installed via pip lacks GPIO permissions
- System package has proper `/dev/gpiomem` access
- Venv needs to access the system RPi.GPIO package

## Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

Your prompt should now show `(venv)` prefix.

## Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

If PyAudio fails to install:
- You can skip it if you already installed `python3-pyaudio` (Step 1)
- Or install portaudio dev files: `sudo apt install portaudio19-dev`

## Step 5: Verify Installation

### Test RPi.GPIO import:
```bash
python3 -c "import RPi.GPIO as GPIO; print('GPIO available:', GPIO.VERSION)"
```

Expected output: `GPIO available: 0.7.1` (or similar)

### Test all hardware:
```bash
python3 test_hardware.py
```

Select option 4 to test the button.

## Troubleshooting

### "No module named 'RPi.GPIO'"
- Did you install system package? `sudo apt install python3-rpi.gpio`
- Did you create venv with `--system-site-packages` flag?
- Recreate venv:
  ```bash
  rm -rf venv
  python3 -m venv --system-site-packages venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

### "Failed to add edge detection"
- Previous GPIO state not cleaned up
- The new button_handler.py should fix this automatically
- Manual cleanup: `sudo python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"`

### "Permission denied" on GPIO
- RPi.GPIO must be system package, not pip package
- Check: `pip list | grep RPi.GPIO` should show nothing
- Check: `python3 -c "import RPi.GPIO; print(RPi.GPIO.__file__)"` should show `/usr/lib/` path

## Starting Fresh

If you need to completely reset your venv:

```bash
# 1. Remove existing venv
rm -rf venv

# 2. Clean up GPIO state
sudo python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"

# 3. Ensure system package is installed
sudo apt install -y python3-rpi.gpio

# 4. Create new venv with system-site-packages
python3 -m venv --system-site-packages venv

# 5. Activate and install requirements
source venv/bin/activate
pip install -r requirements.txt

# 6. Test
python3 test_hardware.py
```

## API Configuration

Set your API endpoint:
```bash
export API_KEY="your-api-base-url-here"
```

Add to `~/.bashrc` to make it permanent:
```bash
echo 'export API_KEY="your-api-base-url-here"' >> ~/.bashrc
source ~/.bashrc
```

## Running Tests

```bash
# Activate venv
source venv/bin/activate

# Run hardware tests
python3 test_hardware.py
```

## Running Main Application

```bash
# Activate venv
source venv/bin/activate

# Run main application
python3 main.py
```

Press Ctrl+C to stop.
