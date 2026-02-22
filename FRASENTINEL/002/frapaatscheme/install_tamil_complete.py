#!/usr/bin/env python3
"""
Complete Tamil language installation for Tesseract OCR
"""

import os
import urllib.request
import shutil
import subprocess
import sys
from pathlib import Path

def download_tamil_data():
    """Download Tamil language data"""
    print("📥 Downloading Tamil language data...")
    
    tam_url = "https://github.com/tesseract-ocr/tessdata/raw/main/tam.traineddata"
    local_file = "tam.traineddata"
    
    try:
        urllib.request.urlretrieve(tam_url, local_file)
        
        if os.path.exists(local_file) and os.path.getsize(local_file) > 0:
            file_size = os.path.getsize(local_file) / (1024 * 1024)
            print(f"✅ Downloaded successfully: {file_size:.2f} MB")
            return local_file
        else:
            print("❌ Download failed")
            return None
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None

def install_with_admin():
    """Install Tamil data using administrator privileges"""
    print("🔧 Installing Tamil language data...")
    
    # Source and destination paths
    source_file = os.path.abspath("tam.traineddata")
    dest_dir = r"C:\Program Files\Tesseract-OCR\tessdata"
    dest_file = os.path.join(dest_dir, "tam.traineddata")
    
    print(f"📁 Source: {source_file}")
    print(f"📁 Destination: {dest_file}")
    
    # Check if destination directory exists
    if not os.path.exists(dest_dir):
        print(f"❌ Tesseract directory not found: {dest_dir}")
        return False
    
    # Try to copy with elevated privileges
    try:
        # Use PowerShell with elevation
        ps_command = f'''
        Start-Process powershell -ArgumentList "-Command", "Copy-Item '{source_file}' '{dest_file}' -Force; if (Test-Path '{dest_file}') {{ Write-Host 'SUCCESS: Tamil data installed' }} else {{ Write-Host 'ERROR: Installation failed' }}" -Verb RunAs -Wait
        '''
        
        print("🚀 Running PowerShell as Administrator...")
        result = subprocess.run(["powershell", "-Command", ps_command], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PowerShell command executed")
            # Check if file was copied
            if os.path.exists(dest_file):
                print("🎉 Tamil language data installed successfully!")
                return True
            else:
                print("❌ File not found after installation")
                return False
        else:
            print(f"❌ PowerShell error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def manual_install_instructions():
    """Provide manual installation instructions"""
    print("\n📋 MANUAL INSTALLATION INSTRUCTIONS")
    print("=" * 60)
    
    source_file = os.path.abspath("tam.traineddata")
    dest_file = r"C:\Program Files\Tesseract-OCR\tessdata\tam.traineddata"
    
    print("🔧 Step-by-step manual installation:")
    print(f"1. Right-click on PowerShell → 'Run as Administrator'")
    print(f"2. Run this command:")
    print(f"   copy \"{source_file}\" \"{dest_file}\"")
    print(f"3. Verify installation:")
    print(f"   python verify_tamil.py")
    
    print(f"\n📁 File locations:")
    print(f"   Source: {source_file}")
    print(f"   Destination: {dest_file}")
    
    # Check if source file exists
    if os.path.exists(source_file):
        file_size = os.path.getsize(source_file) / (1024 * 1024)
        print(f"   ✅ Source file ready: {file_size:.2f} MB")
    else:
        print(f"   ❌ Source file not found")

def verify_installation():
    """Verify Tamil language installation"""
    print("\n🧪 Verifying Tamil language installation...")
    
    try:
        import pytesseract
        
        # Configure Tesseract path
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        # Check if Tamil data file exists
        tam_file = r"C:\Program Files\Tesseract-OCR\tessdata\tam.traineddata"
        if os.path.exists(tam_file):
            file_size = os.path.getsize(tam_file) / (1024 * 1024)
            print(f"✅ Tamil data file found: {file_size:.2f} MB")
        else:
            print(f"❌ Tamil data file not found: {tam_file}")
            return False
        
        # Test Tesseract languages
        languages = pytesseract.get_languages()
        print(f"📋 Available languages: {', '.join(languages)}")
        
        if 'tam' in languages:
            print("🎉 Tamil language support is available!")
            return True
        else:
            print("❌ Tamil language not recognized by Tesseract")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 TAMIL LANGUAGE INSTALLATION FOR TESSERACT OCR")
    print("=" * 70)
    
    # Step 1: Download Tamil data
    tam_file = download_tamil_data()
    if not tam_file:
        print("❌ Failed to download Tamil data")
        return
    
    # Step 2: Try automatic installation
    print(f"\n🔧 Attempting automatic installation...")
    if install_with_admin():
        # Step 3: Verify installation
        if verify_installation():
            print("\n🎉 SUCCESS! Tamil language support is now installed!")
            print("\n📋 Next steps:")
            print("1. Your FastAPI server will automatically use Tamil+English")
            print("2. Test with your Patta image at: http://127.0.0.1:8000/docs")
            print("3. You should now get comprehensive field extraction!")
        else:
            print("\n❌ Installation verification failed")
    else:
        # Provide manual instructions
        manual_install_instructions()
        print(f"\n⏳ After manual installation, run: python verify_tamil.py")

if __name__ == "__main__":
    main()

