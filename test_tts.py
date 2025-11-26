#!/usr/bin/env python3
"""
Test TTS (Text-to-Speech) API endpoint.
Tests /tts/generate to convert text to speech audio.
"""

import requests
import json
import sys
from pathlib import Path

# API Configuration
API_BASE_URL = "http://203.162.88.105/pvlm-api"
TTS_ENDPOINT = f"{API_BASE_URL}/tts/generate"

def test_tts(text, output_file="test_tts_output.wav"):
    """
    Test TTS endpoint with text.

    Args:
        text: Text to convert to speech
        output_file: Where to save the audio file
    """
    print("="*60)
    print("TESTING TTS API")
    print("="*60)
    print(f"Endpoint: {TTS_ENDPOINT}")
    print(f"Text: {text}")
    print(f"Output: {output_file}")
    print()

    try:
        print("=" * 40)
        print("TEST 1: JSON payload with 'text' field")
        print("=" * 40)

        payload = {'text': text}
        print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
        print()

        response = requests.post(
            TTS_ENDPOINT,
            json=payload,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print()

        if response.status_code == 200:
            print("✓ SUCCESS with JSON {'text': ...}")

            # Check if response is audio
            if 'audio' in response.headers.get('Content-Type', ''):
                print("✓ Response is audio file")
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"✓ Audio saved to: {output_file}")
                print(f"  Size: {len(response.content)} bytes")
                return True
            else:
                # Response might be JSON with audio data/URL
                try:
                    result = response.json()
                    print("Response is JSON:")
                    print(json.dumps(result, indent=2, ensure_ascii=False)[:500])

                    # Check for audio data
                    if 'audio' in result or 'data' in result or 'url' in result:
                        print("✓ JSON contains audio reference")
                        return True
                except:
                    print("Response is not JSON, showing raw text:")
                    print(response.text[:500])
        else:
            print(f"✗ FAILED with status {response.status_code}")
            print("Response text:")
            print(response.text[:500])
            print()

        # Try alternative payload formats
        print()
        print("=" * 40)
        print("TEST 2: JSON payload with 'prompt' field")
        print("=" * 40)

        payload2 = {'prompt': text}
        print(f"Payload: {json.dumps(payload2, ensure_ascii=False)}")
        print()

        response2 = requests.post(
            TTS_ENDPOINT,
            json=payload2,
            timeout=30
        )

        print(f"Status Code: {response2.status_code}")
        if response2.status_code == 200:
            print("✓ SUCCESS with JSON {'prompt': ...}")
            return True
        else:
            print(f"✗ FAILED with status {response2.status_code}")
            print("Response text:")
            print(response2.text[:500])

        print()
        print("=" * 40)
        print("TEST 3: Form data with 'text' field")
        print("=" * 40)

        data = {'text': text}
        print(f"Form data: {data}")
        print()

        response3 = requests.post(
            TTS_ENDPOINT,
            data=data,
            timeout=30
        )

        print(f"Status Code: {response3.status_code}")
        if response3.status_code == 200:
            print("✓ SUCCESS with form data {'text': ...}")

            # Save audio if binary
            if 'audio' in response3.headers.get('Content-Type', ''):
                with open(output_file, 'wb') as f:
                    f.write(response3.content)
                print(f"✓ Audio saved to: {output_file}")
            return True
        else:
            print(f"✗ FAILED with status {response3.status_code}")
            print("Response text:")
            print(response3.text[:500])

        print()
        print("=" * 40)
        print("TEST 4: Different field names")
        print("=" * 40)

        # Try other possible field names
        for field_name in ['message', 'content', 'input', 'query']:
            payload_test = {field_name: text}
            print(f"Trying: {json.dumps(payload_test, ensure_ascii=False)[:100]}")

            response_test = requests.post(
                TTS_ENDPOINT,
                json=payload_test,
                timeout=30
            )

            print(f"  Status: {response_test.status_code}")

            if response_test.status_code == 200:
                print(f"  ✓ SUCCESS with field '{field_name}'!")
                return True

    except requests.exceptions.Timeout:
        print("ERROR: Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    return False


def main():
    """Main test function."""
    print()
    print("TTS API Test Tool")
    print()

    # Get text to test
    if len(sys.argv) >= 2:
        text = sys.argv[1]
    else:
        # Use sample Vietnamese text
        text = "Xin chào, đây là thử nghiệm chuyển văn bản thành giọng nói."

    print(f"Test text: {text}")
    print()

    # Output file
    output_file = Path(__file__).parent / "audio" / "test_tts_output.wav"
    output_file.parent.mkdir(exist_ok=True)

    # Run test
    success = test_tts(text, str(output_file))

    print()
    print("="*60)
    if success:
        print("✓ At least one test method succeeded!")
        print(f"Check audio file: {output_file}")
    else:
        print("✗ All test methods failed")
        print()
        print("Possible issues:")
        print("  - API endpoint URL is wrong")
        print("  - API requires authentication")
        print("  - API expects different request format")
        print("  - Text is too long or has invalid characters")
    print("="*60)


if __name__ == "__main__":
    main()
