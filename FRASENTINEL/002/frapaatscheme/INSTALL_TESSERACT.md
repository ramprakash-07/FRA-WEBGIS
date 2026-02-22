# Installing Tesseract OCR for Tamil Patta Processing

## 🚀 Quick Installation Guide

### **Step 1: Download Tesseract**
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

### **Step 2: Install with Tamil Support**
1. Run the installer as Administrator
2. **IMPORTANT**: During installation, make sure to check:
   - ✅ Tamil language pack
   - ✅ Add to PATH (if available)
3. Install to default location: `C:\Program Files\Tesseract-OCR\`

### **Step 3: Verify Installation**
Run this command to test:
```bash
python test_tesseract.py
```

### **Step 4: Restart Your FastAPI Server**
```bash
uvicorn main:app --reload
```

## 🔧 Alternative: Manual PATH Configuration

If Tesseract is installed but not in PATH, you can manually set the path in `digitization/ocr_service.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## 🧪 Testing

After installation, test with:
1. **Web Interface**: `http://127.0.0.1:8000/docs`
2. **Command Line**: `python test_tesseract.py`
3. **API Test**: `python test_api.py`

## 📋 Troubleshooting

- **Error**: "tesseract is not installed"
  - **Solution**: Install Tesseract OCR with Tamil language pack
  
- **Error**: "Tamil language not found"
  - **Solution**: Reinstall Tesseract and ensure Tamil language pack is selected
  
- **Error**: "Permission denied"
  - **Solution**: Run installer as Administrator

