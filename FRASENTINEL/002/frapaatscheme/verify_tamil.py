#!/usr/bin/env python3
"""
Verify Tamil language installation
"""

import os
import pytesseract

def verify_tamil_installation():
    """Verify Tamil language is properly installed"""
    
    print("🔍 Verifying Tamil Language Installation")
    print("=" * 50)
    
    # Configure Tesseract path
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    # Check if Tamil data file exists
    tam_file = r"C:\Program Files\Tesseract-OCR\tessdata\tam.traineddata"
    
    if os.path.exists(tam_file):
        file_size = os.path.getsize(tam_file) / (1024 * 1024)
        print(f"✅ Tamil data file found: {tam_file}")
        print(f"📊 File size: {file_size:.2f} MB")
    else:
        print(f"❌ Tamil data file not found: {tam_file}")
        print("Please install Tamil language data first")
        return False
    
    # Test Tesseract languages
    try:
        languages = pytesseract.get_languages()
        print(f"📋 Available languages: {', '.join(languages)}")
        
        if 'tam' in languages:
            print("🎉 Tamil language support is available!")
            return True
        else:
            print("❌ Tamil language not recognized by Tesseract")
            return False
            
    except Exception as e:
        print(f"❌ Error testing languages: {e}")
        return False

if __name__ == "__main__":
    if verify_tamil_installation():
        print("\n✅ Tamil language is ready to use!")
        print("The OCR service will now use Tamil+English for better extraction")
    else:
        print("\n❌ Tamil language installation incomplete")
        print("Please follow the manual installation steps")

