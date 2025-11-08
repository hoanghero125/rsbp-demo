# Development Guide - Disability Support System

This guide provides information for developers working on or extending the system.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Main Application                      │
│              (main.py - DisabilitySupportSystem)         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Button     │  │   Audio      │  │   Image      │  │
│  │  Handler     │  │  Recorder    │  │  Capture     │  │
│  │ (GPIO pin17) │  │  (ReSpeaker) │  │  (Camera)    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┼──────────────────┘          │
│                           │                             │
│                    ┌──────▼──────┐                      │
│                    │ LLM Client   │                      │
│                    │ - STT        │                      │
│                    │ - Analysis   │                      │
│                    │ - TTS        │                      │
│                    └──────┬───────┘                      │
│                           │                             │
│                    ┌──────▼──────────┐                  │
│                    │ Audio Playback  │                  │
│                    │ (Speaker)       │                  │
│                    └─────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

## Module Dependencies

```
main.py
├── audio_recorder.py
│   ├── pyaudio
│   ├── wave
│   ├── threading
│   └── pathlib
├── image_capture.py
│   ├── subprocess
│   └── pathlib
├── audio_playback.py
│   ├── pyaudio
│   ├── wave
│   ├── subprocess
│   └── threading
├── llm_client.py
│   ├── requests
│   └── pathlib
├── button_handler.py
│   └── RPi.GPIO
├── config.py
│   └── (no external dependencies)
└── logging (built-in)
```

## Code Style Guide

### General Principles

- Follow PEP 8 style guide
- Use type hints for all function parameters and returns
- Document all classes and public methods with docstrings
- Use meaningful variable names
- Keep functions focused on single responsibility

### Docstring Format

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.

    Longer description with more details if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    pass
```

### Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed diagnostic information")
logger.info("General informational message")
logger.warning("Warning message for potential issues")
logger.error("Error message for failures")
logger.critical("Critical system error")
```

### Important Code Comments

Mark important sections with `IMPORTANT:` comments:

```python
# IMPORTANT: This section handles GPIO initialization
# Changes here may affect system startup reliability
```

## Adding New Features

### 1. Create a New Module

```python
# IMPORTANT: New Feature Module
# Description: [What this module does]

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class NewFeature:
    """Description of the new feature."""

    def __init__(self):
        """Initialize the feature."""
        logger.info("NewFeature initialized")

    def process(self) -> Optional[str]:
        """Process something.

        Returns:
            Result string or None if failed
        """
        try:
            # Implementation
            logger.info("Processing complete")
            return "result"
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
```

### 2. Update main.py

Add to imports:
```python
from new_feature import NewFeature
```

Add to `DisabilitySupportSystem.__init__`:
```python
self.new_feature = NewFeature()
```

### 3. Update config.py

Add configuration section:
```python
NEW_FEATURE_CONFIG = {
    "param1": "value1",
    "param2": "value2",
}
```

### 4. Add Tests

Update `test_modules.py`:
```python
def test_new_feature():
    """Test new feature initialization."""
    logger.info("=" * 60)
    logger.info("Testing NewFeature...")
    logger.info("=" * 60)

    try:
        from new_feature import NewFeature
        feature = NewFeature()
        logger.info("✓ NewFeature initialized")
        return True
    except Exception as e:
        logger.error(f"✗ NewFeature test failed: {e}")
        return False
```

## Testing

### Unit Testing

Run individual module tests:

```bash
# Test imports
python3 << 'EOF'
from audio_recorder import AudioRecorder
from image_capture import ImageCapture
print("All imports successful")
EOF
```

### Integration Testing

Run the full test suite:
```bash
python3 test_modules.py
```

### Manual Testing

Test individual components interactively:

```python
# Test audio recorder
python3 << 'EOF'
from audio_recorder import AudioRecorder
recorder = AudioRecorder()
file = recorder.start_recording()
import time; time.sleep(3)
saved = recorder.stop_recording()
print(f"Saved to: {saved}")
EOF
```

## Performance Optimization

### Memory Optimization

- Use generators for large data processing
- Close file handles promptly
- Clear temporary buffers after use

```python
# Good: File automatically closes
with open(file_path, 'rb') as f:
    data = f.read()

# Avoid: File may not close properly
f = open(file_path, 'rb')
data = f.read()
```

### CPU Optimization

- Use threading for I/O bound operations (done in audio_recorder.py)
- Avoid blocking operations in main loop
- Cache API responses when appropriate

### Network Optimization

- Set appropriate timeout values (currently 30s for LLM API)
- Implement retry logic for network failures
- Compress audio/image data if needed

## Debugging

### Enable Debug Logging

Edit `config.py`:
```python
LOGGING_CONFIG = {
    "level": "DEBUG",  # Verbose output
    # ... rest of config
}
```

### Check System State

```bash
# Monitor logs in real-time
journalctl -u rsbp-system -f

# Check GPIO state
gpio readall

# Monitor resource usage
top
```

### Profiling

```python
import cProfile
import pstats

# Profile the main application
cProfile.run('main()', 'stats')
stats = pstats.Stats('stats')
stats.sort_stats('cumulative').print_stats(10)
```

## Error Handling Patterns

### Graceful Degradation

```python
try:
    primary_method()
except PrimaryMethodError:
    logger.warning("Primary method failed, trying fallback")
    try:
        fallback_method()
    except FallbackMethodError:
        logger.error("Both methods failed")
        return None
```

### Resource Cleanup

```python
resource = None
try:
    resource = acquire_resource()
    use_resource(resource)
finally:
    if resource:
        release_resource(resource)
```

## Future Enhancement Ideas

### Short Term (Next Release)

- [ ] Add audio gain control for microphone
- [ ] Implement file encryption for sensitive recordings
- [ ] Add battery status monitoring
- [ ] Create web dashboard for monitoring
- [ ] Add support for multiple languages in TTS

### Medium Term

- [ ] Implement local LLM processing (reduce cloud dependency)
- [ ] Add edge caching for API responses
- [ ] Support multiple camera angles
- [ ] Implement gesture recognition
- [ ] Add real-time transcription display

### Long Term

- [ ] Mobile app companion for remote monitoring
- [ ] Integration with smart home systems
- [ ] Advanced AI for proactive assistance
- [ ] Multi-device coordination
- [ ] Offline mode with sync capability

## Common Issues and Solutions

### Issue: Audio Recording Quality Poor

**Solution:**
1. Check microphone connection
2. Adjust gain in ReSpeaker settings
3. Reduce background noise
4. Check sample rate in config.py

### Issue: Slow Response Times

**Solution:**
1. Check network connectivity
2. Monitor system resources (RAM, CPU)
3. Review LLM API logs
4. Consider caching results

### Issue: Memory Leaks

**Solution:**
1. Ensure all files are closed properly
2. Clear circular references
3. Profile with memory_profiler
4. Check for unclosed threads

## Tools and Dependencies

### Development Tools

```bash
# Code formatting
pip3 install black autopep8

# Linting
pip3 install pylint flake8

# Type checking
pip3 install mypy

# Testing
pip3 install pytest pytest-cov

# Documentation
pip3 install sphinx
```

### Useful Commands

```bash
# Format code
black *.py

# Check code quality
pylint *.py

# Type checking
mypy *.py

# Run tests
pytest test_*.py -v --cov
```

## Version Control

### Commit Message Format

```
[TYPE] Short description (50 chars max)

Longer description explaining the changes.
Wrap at 72 characters.

Fixes #123
```

Types: FEAT, FIX, DOCS, REFACTOR, TEST, CONFIG

## API Documentation

### External API: LLM Service

Base URL: `http://203.162.88.105/pvlm-api`

Request/Response examples in [llm_client.py](llm_client.py)

### Configuration API

All configuration in [config.py](config.py) - centralized for easy modification

## Contact and Support

For development questions:
1. Check existing documentation
2. Review code comments and docstrings
3. Run test_modules.py to identify issues
4. Check system logs: /var/log/rsbp_system.log

## License and Attribution

This system is designed for accessibility and disability support.
All code follows professional standards for reliability and robustness.
