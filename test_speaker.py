#!/usr/bin/env python3
"""
Test Speaker/Audio Playback
Debug audio output issues.
"""

import subprocess
import sys
from pathlib import Path
import wave

def print_section(title):
    """Print a section header."""
    print("\n" + "="*60)
    print(title)
    print("="*60)

def test_audio_devices():
    """List all audio devices."""
    print_section("TEST 1: Audio Devices")

    print("Listing playback devices:")
    try:
        result = subprocess.run(
            ["aplay", "-l"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except Exception as e:
        print(f"ERROR: {e}")

def test_volume():
    """Check volume settings."""
    print_section("TEST 2: Volume Settings")

    print("Checking volume with amixer:")
    try:
        result = subprocess.run(
            ["amixer", "sget", "Master"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout)

        # Check if muted
        if "[off]" in result.stdout:
            print("\n⚠️  WARNING: Audio is MUTED!")
            print("Run: amixer sset Master unmute")
    except Exception as e:
        print(f"ERROR: {e}")

def test_file_exists():
    """Check if audio files exist."""
    print_section("TEST 3: Audio Files")

    # Check for test TTS output
    audio_dir = Path(__file__).parent / "audio"

    print(f"Audio directory: {audio_dir}")

    if not audio_dir.exists():
        print("❌ Audio directory does not exist!")
        return None

    # Find audio files
    wav_files = list(audio_dir.glob("*.wav"))

    if not wav_files:
        print("❌ No WAV files found in audio directory")
        return None

    print(f"\n✓ Found {len(wav_files)} WAV file(s):")

    # Sort by modification time, newest first
    wav_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    for i, f in enumerate(wav_files[:5]):  # Show only latest 5
        size = f.stat().st_size
        print(f"  {i+1}. {f.name} ({size} bytes)")

    # Return latest file
    latest = wav_files[0]
    print(f"\n➜ Using latest file: {latest.name}")
    return latest

def test_file_format(audio_file):
    """Check audio file format."""
    print_section("TEST 4: Audio File Format")

    try:
        with wave.open(str(audio_file), 'rb') as wf:
            print(f"File: {audio_file.name}")
            print(f"  Channels: {wf.getnchannels()}")
            print(f"  Sample width: {wf.getsampwidth()} bytes")
            print(f"  Frame rate: {wf.getframerate()} Hz")
            print(f"  Frames: {wf.getnframes()}")
            duration = wf.getnframes() / wf.getframerate()
            print(f"  Duration: {duration:.2f} seconds")

            if wf.getnframes() == 0:
                print("\n❌ WARNING: File has 0 frames! File might be corrupted or empty.")
                return False

            return True
    except Exception as e:
        print(f"❌ ERROR reading file: {e}")
        return False

def test_aplay_default(audio_file):
    """Test playing with aplay (default device)."""
    print_section("TEST 5: Play with aplay (default device)")

    print(f"Playing: {audio_file.name}")
    print("Command: aplay <file>")
    print()

    try:
        result = subprocess.run(
            ["aplay", str(audio_file)],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✓ aplay completed successfully")
            print("Did you hear sound? (Check speaker)")
            return True
        else:
            print(f"❌ aplay failed with return code {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ aplay timed out")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_aplay_specific_device(audio_file):
    """Test playing with specific device."""
    print_section("TEST 6: Play with aplay (specific device)")

    # Common ReSpeaker device specifications
    devices_to_try = [
        ("hw:2,0", "ReSpeaker - Device 2, Subdevice 0"),
        ("plughw:2,0", "ReSpeaker - plughw wrapper"),
        ("hw:0,0", "Default device"),
        ("plughw:0,0", "Default device - plughw wrapper"),
    ]

    for device, description in devices_to_try:
        print(f"\nTrying device: {device} ({description})")
        print(f"Command: aplay -D {device} <file>")

        try:
            result = subprocess.run(
                ["aplay", "-D", device, str(audio_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"✓ SUCCESS with device: {device}")
                print("Did you hear sound?")
                return device
            else:
                print(f"✗ Failed: {result.stderr[:200]}")
        except Exception as e:
            print(f"✗ Error: {e}")

    return None

def test_speaker_test():
    """Test with speaker-test utility."""
    print_section("TEST 7: Speaker Test Utility")

    print("Running speaker-test (2 seconds, 440Hz tone)")
    print("Command: speaker-test -t sine -f 440 -l 1")
    print()

    try:
        result = subprocess.run(
            ["speaker-test", "-t", "sine", "-f", "440", "-l", "1"],
            capture_output=True,
            text=True,
            timeout=5
        )

        print("Output:", result.stdout[:500])
        print("\nDid you hear a tone?")

    except FileNotFoundError:
        print("speaker-test not installed")
        print("Install with: sudo apt install alsa-utils")
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Main test function."""
    print("\n" + "="*60)
    print("SPEAKER / AUDIO PLAYBACK DEBUG TOOL")
    print("="*60)

    # Test 1: List devices
    test_audio_devices()

    # Test 2: Check volume
    test_volume()

    # Test 3: Find audio file
    audio_file = test_file_exists()

    if not audio_file:
        print("\n❌ No audio file to test. Generate one first:")
        print("   python3 test_tts.py")
        return

    # Test 4: Check file format
    if not test_file_format(audio_file):
        print("\n❌ Audio file has issues. Cannot continue.")
        return

    # Test 5: Try default device
    print("\n" + "-"*60)
    input("Press Enter to test audio playback (default device)...")
    success_default = test_aplay_default(audio_file)

    # Test 6: Try specific devices
    if not success_default:
        print("\n" + "-"*60)
        input("Press Enter to test different audio devices...")
        working_device = test_aplay_specific_device(audio_file)

        if working_device:
            print("\n" + "="*60)
            print("✓ SOLUTION FOUND!")
            print("="*60)
            print(f"Working device: {working_device}")
            print("\nTo fix audio_playback.py:")
            print(f"  Change aplay command to: aplay -D {working_device} <file>")

    # Test 7: Speaker test
    print("\n" + "-"*60)
    input("Press Enter to run speaker-test utility...")
    test_speaker_test()

    # Summary
    print("\n" + "="*60)
    print("TROUBLESHOOTING TIPS")
    print("="*60)
    print()
    print("If no sound:")
    print("  1. Check speaker is connected to ReSpeaker HAT")
    print("  2. Check volume: amixer sget Master")
    print("  3. Unmute if needed: amixer sset Master unmute")
    print("  4. Set volume: amixer sset Master 80%")
    print("  5. Check audio device in aplay -l")
    print("  6. Try different device with: aplay -D hw:X,Y file.wav")
    print()
    print("If running as systemd service:")
    print("  - Service may not have access to audio devices")
    print("  - Check journalctl logs: sudo journalctl -u disability-support -n 50")
    print("  - Try adding User to 'audio' group: sudo usermod -a -G audio pi")
    print()

if __name__ == "__main__":
    main()
