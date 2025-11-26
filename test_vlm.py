#!/usr/bin/env python3
"""
Test VLM (Vision-Language Model) API endpoint.
Tests /image/analyze-image with both image and text prompt.
"""

import requests
import json
import sys
from pathlib import Path

# API Configuration
API_BASE_URL = "http://203.162.88.105/pvlm-api"
VLM_ENDPOINT = f"{API_BASE_URL}/image/analyze-image"

def test_vlm(image_path, prompt):
    """
    Test VLM endpoint with image and prompt.

    Args:
        image_path: Path to image file
        prompt: Text prompt/question
    """
    print("="*60)
    print("TESTING VLM API")
    print("="*60)
    print(f"Endpoint: {VLM_ENDPOINT}")
    print(f"Image: {image_path}")
    print(f"Prompt: {prompt}")
    print()

    # Check if image exists
    img_path = Path(image_path)
    if not img_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return

    try:
        # Prepare request
        print("Sending request to VLM...")

        with open(img_path, 'rb') as img_file:
            files = {'file': (img_path.name, img_file, 'image/jpeg')}
            data = {'prompt': prompt}

            # Send POST request
            response = requests.post(
                VLM_ENDPOINT,
                files=files,
                data=data,
                timeout=30
            )

        print(f"Status Code: {response.status_code}")
        print()

        # Check response
        if response.status_code == 200:
            print("SUCCESS: Got response from VLM")
            print()

            # Try to parse JSON
            try:
                result = response.json()
                print("Response JSON:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                print()

                # Try different keys to extract response
                print("Checking for response in different keys:")
                possible_keys = ['response', 'answer', 'text', 'description', 'analysis', 'result', 'output']

                for key in possible_keys:
                    if key in result:
                        print(f"  ✓ Found '{key}': {result[key]}")
                    else:
                        print(f"  ✗ No '{key}' key")

                print()
                print("All keys in response:", list(result.keys()))

            except json.JSONDecodeError:
                print("ERROR: Response is not JSON")
                print("Raw response:")
                print(response.text[:500])
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print("Response:")
            print(response.text[:500])

    except requests.exceptions.Timeout:
        print("ERROR: Request timed out")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API")
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    """Main test function."""
    print()
    print("VLM API Test Tool")
    print()

    # Check if arguments provided
    if len(sys.argv) >= 3:
        image_path = sys.argv[1]
        prompt = sys.argv[2]
    else:
        # Use defaults - find latest image and use sample prompt
        images_dir = Path(__file__).parent / "images"

        # Find latest image
        images = sorted(images_dir.glob("capture_*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)

        if not images:
            print("ERROR: No test images found in images/")
            print()
            print("Usage:")
            print(f"  python3 {Path(__file__).name} <image_path> <prompt>")
            print()
            print("Example:")
            print(f"  python3 {Path(__file__).name} images/capture_20251126_192730.jpg 'What do you see?'")
            return

        image_path = str(images[0])
        prompt = "Tôi đang nhìn thấy gì vậy?"

        print(f"Using latest image: {image_path}")
        print(f"Using default prompt: {prompt}")
        print()

    # Run test
    test_vlm(image_path, prompt)

    print()
    print("="*60)
    print("Test complete")
    print("="*60)


if __name__ == "__main__":
    main()
