#!/usr/bin/env python3
"""
Test script for Patta API endpoint
"""

import requests
import json

def test_patta_api(image_path):
    """Test the Patta API with an image file"""
    
    url = "http://127.0.0.1:8000/digitization/upload_patta/"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print("="*50)
            print("EXTRACTED PATTA DATA:")
            print("="*50)
            print(json.dumps(result['extracted_data'], ensure_ascii=False, indent=2))
            print("\n" + "="*50)
            print("FILE INFO:")
            print("="*50)
            print(f"Filename: {result['filename']}")
            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")
            print(f"JSON Output: {result['json_output']}")
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
            
    except FileNotFoundError:
        print(f"❌ File not found: {image_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Replace with your actual Patta image path
    image_path = "your_patta_image.jpg"  # Change this to your image file
    print(f"Testing with image: {image_path}")
    test_patta_api(image_path)

