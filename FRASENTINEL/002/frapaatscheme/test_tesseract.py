#!/usr/bin/env python3
"""
Test script to verify Tesseract OCR installation
"""

import os
import sys
import shutil
import platform

def test_tesseract_installation():
    """Test if Tesseract is properly installed and configured"""
    
    print("🔍 Testing Tesseract OCR Installation")
    print("=" * 50)
    
    # Check if tesseract is in PATH
    tesseract_path = shutil.which('tesseract')
    if tesseract_path:
        print(f"✅ Tesseract found in PATH: {tesseract_path}")
    else:
        print("❌ Tesseract not found in PATH")
        
        # Check common Windows installation paths
        if platform.system() == "Windows":
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            
            found_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    found_path = path
                    print(f"✅ Tesseract found at: {path}")
                    break
            
            if not found_path:
                print("❌ Tesseract not found in common installation paths")
                print("\n📋 Installation Instructions:")
                print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
                print("2. Install with Tamil language support")
                print("3. Restart your terminal/application")
                return False
    
    # Test pytesseract import
    try:
        import pytesseract
        print("✅ pytesseract module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pytesseract: {e}")
        return False
    
    # Test Tesseract command
    try:
        # Configure path if needed
        if platform.system() == "Windows" and not tesseract_path:
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        
        # Test basic functionality
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        
        # Test language support
        try:
            languages = pytesseract.get_languages()
            print(f"✅ Available languages: {', '.join(languages)}")
            
            if 'tam' in languages:
                print("✅ Tamil language support available")
            else:
                print("⚠️  Tamil language support not found")
                print("   Please reinstall Tesseract with Tamil language pack")
                
        except Exception as e:
            print(f"⚠️  Could not check languages: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tesseract test failed: {e}")
        return False

def test_ocr_service():
    """Test the OCR service initialization"""
    print("\n🧪 Testing OCR Service")
    print("=" * 50)
    
    try:
        from digitization.ocr_service import PattaOCRService
        service = PattaOCRService()
        print("✅ OCR Service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ OCR Service initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Tesseract OCR Installation Test")
    print("=" * 60)
    
    # Test Tesseract installation
    tesseract_ok = test_tesseract_installation()
    
    # Test OCR service
    service_ok = test_ocr_service()
    
    print("\n" + "=" * 60)
    if tesseract_ok and service_ok:
        print("🎉 All tests passed! Tesseract OCR is ready to use.")
        print("\n📋 Next steps:")
        print("1. Restart your FastAPI server: uvicorn main:app --reload")
        print("2. Test with a Patta image at: http://127.0.0.1:8000/docs")
    else:
        print("❌ Some tests failed. Please install Tesseract OCR properly.")
        print("\n📋 Installation guide:")
        print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install with Tamil language support")
        print("3. Run this test again: python test_tesseract.py")

