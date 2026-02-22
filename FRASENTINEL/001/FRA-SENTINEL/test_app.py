#!/usr/bin/env python3
"""
Simple test script to identify Flask app issues
"""

import requests
import json

def test_app():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing FRA-SENTINEL App...")
    print("=" * 40)
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Home page: {response.status_code}")
    except Exception as e:
        print(f"❌ Home page error: {e}")
    
    # Test 2: Upload page
    try:
        response = requests.get(f"{base_url}/upload")
        print(f"✅ Upload page: {response.status_code}")
    except Exception as e:
        print(f"❌ Upload page error: {e}")
    
    # Test 3: API endpoints
    try:
        response = requests.get(f"{base_url}/api/villages")
        print(f"✅ Villages API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Features count: {len(data.get('features', []))}")
    except Exception as e:
        print(f"❌ Villages API error: {e}")
    
    # Test 4: Health check
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   🏥 Status: {data.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print("\n🎯 App testing complete!")

if __name__ == "__main__":
    test_app()









