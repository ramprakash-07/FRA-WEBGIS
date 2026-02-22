#!/usr/bin/env python3
"""
Download Tamil language data for Tesseract OCR
"""

import urllib.request
import os
import shutil
from pathlib import Path

def download_tamil_data():
    """Download Tamil language data file"""
    
    print("🌐 Downloading Tamil Language Data for Tesseract OCR")
    print("=" * 60)
    
    # Tamil language data URL
    tam_url = "https://github.com/tesseract-ocr/tessdata/raw/main/tam.traineddata"
    
    # Download to current directory first
    local_file = "tam.traineddata"
    
    print(f"📥 Downloading from: {tam_url}")
    print(f"📁 Saving to: {local_file}")
    
    try:
        # Download the file
        urllib.request.urlretrieve(tam_url, local_file)
        
        # Check if download was successful
        if os.path.exists(local_file) and os.path.getsize(local_file) > 0:
            file_size = os.path.getsize(local_file) / (1024 * 1024)  # MB
            print(f"✅ Download successful!")
            print(f"📊 File size: {file_size:.2f} MB")
            return local_file
        else:
            print("❌ Download failed - file is empty or doesn't exist")
            return None
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def install_tamil_data(tam_file):
    """Install Tamil data to Tesseract directory"""
    
    print(f"\n🔧 Installing Tamil language data...")
    
    # Tesseract data directory
    tesseract_data_dir = Path("C:/Program Files/Tesseract-OCR/tessdata")
    
    if not tesseract_data_dir.exists():
        print(f"❌ Tesseract data directory not found: {tesseract_data_dir}")
        print("Please install Tesseract OCR first")
        return False
    
    # Destination file
    dest_file = tesseract_data_dir / "tam.traineddata"
    
    try:
        # Copy file to Tesseract directory
        shutil.copy2(tam_file, dest_file)
        
        if dest_file.exists():
            print(f"✅ Tamil data installed successfully!")
            print(f"📁 Location: {dest_file}")
            return True
        else:
            print("❌ Installation failed")
            return False
            
    except PermissionError:
        print("❌ Permission denied - need administrator privileges")
        print("\n📋 Manual installation steps:")
        print(f"1. Copy '{tam_file}' to '{dest_file}'")
        print("2. Run PowerShell as Administrator")
        print(f"3. Run: copy \"{os.path.abspath(tam_file)}\" \"{dest_file}\"")
        return False
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def test_tamil_support():
    """Test if Tamil language is now available"""
    
    print(f"\n🧪 Testing Tamil language support...")
    
    try:
        import pytesseract
        
        # Configure Tesseract path
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        # Get available languages
        languages = pytesseract.get_languages()
        print(f"📋 Available languages: {', '.join(languages)}")
        
        if 'tam' in languages:
            print("🎉 Tamil language support is now available!")
            return True
        else:
            print("❌ Tamil language support still not available")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def cleanup_temp_file(tam_file):
    """Clean up temporary downloaded file"""
    try:
        if os.path.exists(tam_file):
            os.remove(tam_file)
            print(f"🧹 Cleaned up temporary file: {tam_file}")
    except Exception as e:
        print(f"⚠️  Could not clean up {tam_file}: {e}")

if __name__ == "__main__":
    print("🚀 Tamil Language Installation for Tesseract OCR")
    print("=" * 70)
    
    # Download Tamil data
    tam_file = download_tamil_data()
    
    if tam_file:
        # Install Tamil data
        if install_tamil_data(tam_file):
            # Test Tamil support
            if test_tamil_support():
                print("\n🎉 SUCCESS! Tamil language support is now installed!")
                print("\n📋 Next steps:")
                print("1. The OCR service will automatically use Tamil+English")
                print("2. Test with your Patta image at: http://127.0.0.1:8000/docs")
                print("3. You should now get much better extraction results!")
            else:
                print("\n❌ Tamil support test failed")
        else:
            print("\n❌ Installation failed - try manual installation")
        
        # Clean up
        cleanup_temp_file(tam_file)
    else:
        print("\n❌ Download failed - please try manual installation")
        print("\n📋 Manual steps:")
        print("1. Go to: https://github.com/tesseract-ocr/tessdata")
        print("2. Download: tam.traineddata")
        print("3. Copy to: C:/Program Files/Tesseract-OCR/tessdata/")

