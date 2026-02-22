#!/usr/bin/env python3
"""
Script to download Tamil language data for Tesseract OCR
"""

import os
import urllib.request
import shutil
from pathlib import Path

def download_tamil_language_data():
    """Download Tamil language data for Tesseract"""
    
    # Tesseract data directory
    tesseract_data_dir = Path("C:/Program Files/Tesseract-OCR/tessdata")
    
    if not tesseract_data_dir.exists():
        print("❌ Tesseract data directory not found")
        print("Please install Tesseract OCR first")
        return False
    
    # Tamil language data URL
    tam_url = "https://github.com/tesseract-ocr/tessdata/raw/main/tam.traineddata"
    tam_file = tesseract_data_dir / "tam.traineddata"
    
    print("📥 Downloading Tamil language data...")
    print(f"URL: {tam_url}")
    print(f"Destination: {tam_file}")
    
    try:
        # Download the file
        urllib.request.urlretrieve(tam_url, tam_file)
        print("✅ Tamil language data downloaded successfully")
        
        # Verify the file
        if tam_file.exists() and tam_file.stat().st_size > 0:
            print(f"✅ File verified: {tam_file.stat().st_size} bytes")
            return True
        else:
            print("❌ Downloaded file is empty or corrupted")
            return False
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def test_tamil_support():
    """Test if Tamil language is now available"""
    try:
        import pytesseract
        
        # Configure Tesseract path
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        # Get available languages
        languages = pytesseract.get_languages()
        print(f"Available languages: {', '.join(languages)}")
        
        if 'tam' in languages:
            print("✅ Tamil language support is now available!")
            return True
        else:
            print("❌ Tamil language support still not available")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🌐 Installing Tamil Language Support for Tesseract")
    print("=" * 60)
    
    # Download Tamil language data
    if download_tamil_language_data():
        print("\n🧪 Testing Tamil language support...")
        if test_tamil_support():
            print("\n🎉 Tamil language support installed successfully!")
            print("\n📋 Next steps:")
            print("1. Restart your FastAPI server: uvicorn main:app --reload")
            print("2. Test with a Tamil Patta image at: http://127.0.0.1:8000/docs")
        else:
            print("\n❌ Tamil language support installation failed")
    else:
        print("\n❌ Failed to download Tamil language data")
        print("\n📋 Manual installation:")
        print("1. Go to: https://github.com/tesseract-ocr/tessdata")
        print("2. Download: tam.traineddata")
        print("3. Place in: C:/Program Files/Tesseract-OCR/tessdata/")

