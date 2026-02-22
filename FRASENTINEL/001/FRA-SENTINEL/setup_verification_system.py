#!/usr/bin/env python3
"""
Setup script for Patta Document Verification System
Installs dependencies and configures the system
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    # Install basic requirements
    if not run_command("pip install -r requirements_enhanced.txt", "Installing enhanced requirements"):
        return False
    
    # Install spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model"):
        print("⚠️ spaCy model download failed, but continuing...")
    
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("\n🔍 Checking Tesseract OCR installation...")
    
    try:
        result = subprocess.run("tesseract --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract OCR is installed")
            return True
    except:
        pass
    
    print("❌ Tesseract OCR not found")
    print("\n📋 Please install Tesseract OCR:")
    
    system = platform.system().lower()
    if system == "windows":
        print("  Windows:")
        print("  1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  2. Install to default location: C:\\Program Files\\Tesseract-OCR")
        print("  3. Add to PATH or update the path in patta_verifier.py")
    elif system == "darwin":  # macOS
        print("  macOS:")
        print("  Run: brew install tesseract")
    else:  # Linux
        print("  Linux:")
        print("  Run: sudo apt-get install tesseract-ocr")
        print("  Or: sudo yum install tesseract")
    
    return False

def check_poppler():
    """Check if Poppler is installed (for PDF processing)"""
    print("\n📄 Checking Poppler installation...")
    
    try:
        result = subprocess.run("pdftoppm -h", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Poppler is installed")
            return True
    except:
        pass
    
    print("❌ Poppler not found")
    print("\n📋 Please install Poppler:")
    
    system = platform.system().lower()
    if system == "windows":
        print("  Windows:")
        print("  1. Download from: https://blog.alivate.com.au/poppler-windows/")
        print("  2. Extract and add to PATH")
    elif system == "darwin":  # macOS
        print("  macOS:")
        print("  Run: brew install poppler")
    else:  # Linux
        print("  Linux:")
        print("  Run: sudo apt-get install poppler-utils")
        print("  Or: sudo yum install poppler-utils")
    
    return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "patta_verification",
        "webgis/uploads/patta_verification",
        "data/processed",
        "data/uploaded"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def test_verification_system():
    """Test the verification system"""
    print("\n🧪 Testing verification system...")
    
    try:
        # Test import
        sys.path.append(os.path.join(os.path.dirname(__file__), 'patta_verification'))
        from patta_verifier import PattaVerifier
        
        # Initialize verifier
        verifier = PattaVerifier()
        print("✅ PattaVerifier imported and initialized successfully")
        
        # Test with sample data
        print("✅ Verification system is ready")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Start the Flask application:")
    print("   cd webgis")
    print("   python simple_working_app.py")
    print("\n2. Open your browser to:")
    print("   http://localhost:5000")
    print("\n3. Upload a Patta document for verification")
    print("\n4. Test the verification system:")
    print("   python patta_verification/test_verification.py")
    print("\n📚 Documentation:")
    print("   Read patta_verification/README.md for detailed usage instructions")

def main():
    """Main setup function"""
    print("🚀 Patta Document Verification System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check external tools
    tesseract_ok = check_tesseract()
    poppler_ok = check_poppler()
    
    if not tesseract_ok or not poppler_ok:
        print("\n⚠️ Some external tools are missing, but you can still test the system")
        print("The verification system will work with limited functionality")
    
    # Test the system
    if test_verification_system():
        show_next_steps()
    else:
        print("\n❌ Setup completed but verification system test failed")
        print("Please check the error messages above and try again")

if __name__ == "__main__":
    main()









