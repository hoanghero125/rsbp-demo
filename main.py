import RPi.GPIO as GPIO
import pyaudio
import wave
import subprocess
from datetime import datetime
import threading

BUTTON_PIN = 17
RESPEAKER_INDEX = 2  # Change this to match your device index
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000

# State variables
recording = False
frames = []
stream = None
audio = None

def take_picture():
    """Take a picture using rpicam-jpeg"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/home/pi/Pictures/recording_{timestamp}.jpg"
    
    try:
        subprocess.run([
            "rpicam-jpeg",
            "-o", filename,
            "-t", "1000"
        ], check=True)
        print(f"Picture saved: {filename}")
        return filename
    except subprocess.CalledProcessError as e:
        print(f"Error taking picture: {e}")
        return None

def start_recording():
    """Start audio recording"""
    global recording, frames, stream, audio
    
    frames = []
    audio = pyaudio.PyAudio()
    
    try:
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=RESPEAKER_INDEX,
            frames_per_buffer=CHUNK
        )
        
        recording = True
        print("🎙️  Recording started...")
        
        # Record in a separate thread
        def record():
            while recording:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"Recording error: {e}")
                    break
        
        record_thread = threading.Thread(target=record)
        record_thread.start()
        
    except Exception as e:
        print(f"Error starting recording: {e}")
        recording = False

def stop_recording():
    """Stop recording and save the audio file"""
    global recording, frames, stream, audio
    
    recording = False
    print("⏹️  Recording stopped...")
    
    if stream:
        stream.stop_stream()
        stream.close()
    
    if audio:
        audio.terminate()
    
    # Save the recorded audio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/home/pi/recordings/audio_{timestamp}.wav"
    
    try:
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT) if audio else 2)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Audio saved: {filename}")
    except Exception as e:
        print(f"Error saving audio: {e}")
    
    # Take picture after saving audio
    print("📸 Taking picture...")
    take_picture()

def button_callback(channel):
    """Handle button press"""
    global recording
    
    if not recording:
        start_recording()
    else:
        stop_recording()

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Add button press detection (falling edge = button pushed)
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                     callback=button_callback, 
                     bouncetime=500)  # 500ms debounce

print("=" * 50)
print("Audio Recording + Picture Capture System")
print("=" * 50)
print("Press the button to start recording")
print("Press again to stop recording and take a picture")
print("Press Ctrl+C to exit")
print("=" * 50)

try:
    # Create recordings directory if it doesn't exist
    subprocess.run(["mkdir", "-p", "/home/pi/recordings"], check=False)
    subprocess.run(["mkdir", "-p", "/home/pi/Pictures"], check=False)
    
    # Keep the script running
    while True:
        import time
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("\nExiting...")
    if recording:
        stop_recording()
    GPIO.cleanup()