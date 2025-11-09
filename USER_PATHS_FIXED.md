# User Paths Fixed - All Directories Updated

## Summary

All directory paths have been updated to use the correct user `thuongvv` and keep everything inside the `rsbp-demo` folder.

## Changes Made

### config.py - Updated All Paths

#### Recording Directory
```python
# BEFORE:
"output_dir": "/home/pi/recordings"

# AFTER:
"output_dir": "/home/thuongvv/rsbp-demo/recordings"
```

#### Image Directory
```python
# BEFORE:
"output_dir": "/home/pi/Pictures"

# AFTER:
"output_dir": "/home/thuongvv/rsbp-demo/pictures"
```

#### Logging Directory
```python
# BEFORE:
"log_file": "/var/log/rsbp_system.log"

# AFTER:
"log_file": "/home/thuongvv/rsbp-demo/logs/rsbp_system.log"
```

### install.sh - Updated Directory Creation

#### Before (Step 7):
```bash
mkdir -p /home/pi/recordings
mkdir -p /home/pi/Pictures
chown pi:pi /home/pi/recordings
chown pi:pi /home/pi/Pictures
```

#### After (Step 7):
```bash
mkdir -p /home/thuongvv/rsbp-demo/recordings
mkdir -p /home/thuongvv/rsbp-demo/pictures
mkdir -p /home/thuongvv/rsbp-demo/logs
chmod 755 /home/thuongvv/rsbp-demo/recordings
chmod 755 /home/thuongvv/rsbp-demo/pictures
chmod 755 /home/thuongvv/rsbp-demo/logs
```

## Directory Structure

After running the installation script, you will have:

```
/home/thuongvv/rsbp-demo/
├── recordings/          # Audio files (WAV)
├── pictures/            # Image files (JPEG)
├── logs/                # System logs
│   └── rsbp_system.log
├── main.py
├── audio_recorder.py
├── image_capture.py
├── audio_playback.py
├── llm_client.py
├── button_handler.py
├── config.py
├── test_modules.py
├── install.sh
├── requirements.txt
├── rsbp-system.service
└── (all other project files)
```

## What You Need to Create Manually

Run these commands as user `thuongvv`:

```bash
cd /home/thuongvv/rsbp-demo
mkdir -p recordings
mkdir -p pictures
mkdir -p logs
```

Or let the install.sh do it automatically:

```bash
cd /home/thuongvv/rsbp-demo
sudo bash install.sh
```

## File Storage Locations

### Audio Recordings
- Location: `/home/thuongvv/rsbp-demo/recordings/`
- Files: `audio_YYYYMMDD_HHMMSS.wav`

### Camera Images
- Location: `/home/thuongvv/rsbp-demo/pictures/`
- Files: `recording_YYYYMMDD_HHMMSS.jpg`

### System Logs
- Location: `/home/thuongvv/rsbp-demo/logs/`
- Files: `rsbp_system.log`

## Verification

After installation, verify the directories exist:

```bash
ls -la /home/thuongvv/rsbp-demo/
```

You should see:
```
drwxr-xr-x  recordings
drwxr-xr-x  pictures
drwxr-xr-x  logs
```

## Configuration Verification

Check that config.py has the correct paths:

```bash
grep "output_dir\|log_file" /home/thuongvv/rsbp-demo/config.py
```

Output should show:
```
    "output_dir": "/home/thuongvv/rsbp-demo/recordings",
    "output_dir": "/home/thuongvv/rsbp-demo/pictures",
    "log_file": "/home/thuongvv/rsbp-demo/logs/rsbp_system.log",
```

## Important Notes

- All data stays within the `rsbp-demo` folder
- No scattered files in system directories
- Easy to backup (just backup the entire folder)
- Easy to move (all relative paths are internal)
- Clean and organized structure
- User `thuongvv` can manage all files without sudo

## Next Steps

1. Navigate to the project folder:
   ```bash
   cd /home/thuongvv/rsbp-demo
   ```

2. Create the required directories:
   ```bash
   mkdir -p recordings pictures logs
   ```

3. Or run the installation script which will do it automatically

4. Verify everything is in place:
   ```bash
   ls -la
   ```

All paths are now correctly configured for user `thuongvv`!
