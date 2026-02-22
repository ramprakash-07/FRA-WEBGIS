# Patta Document Verification System

A comprehensive system for verifying Patta documents online with OCR, portal verification, GIS validation, and authentication checks.

## 🎯 Overview

This system implements all the rules and conditions for online Patta verification as specified:

### ✅ Features Implemented

1. **OCR Extraction with 90%+ Confidence Validation**
   - Extracts District, Taluk, Village, Survey Number, Patta Number, Owner Name
   - Validates OCR quality and confidence scores
   - Handles multiple document formats (PDF, PNG, JPG, JPEG, TIFF, BMP)

2. **Portal Verification**
   - Integration with state government portals:
     - Tamil Nadu: eservices.tn.gov.in
     - Andhra Pradesh: MeeBhoomi Portal
     - Telangana: Dharani Portal
     - Karnataka: Bhoomi RTC Portal
   - Cross-validates extracted data with official records

3. **GIS/Map Verification**
   - Validates geographical coordinates
   - Checks boundary accuracy
   - Calculates distance between document and portal coordinates

4. **Authentication Checks**
   - QR code detection and validation
   - Watermark detection
   - Digital signature verification
   - Tampering detection

5. **Cross-Validation with Encumbrance Certificate**
   - Checks for legal disputes
   - Validates loan liens
   - Confirms owner name matches

6. **Comprehensive Decision Logic**
   - Accept/Reject/Flag for Review decisions
   - Confidence scoring (0-100%)
   - Detailed reasoning and recommendations

## 🚀 Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r patta_verification/requirements.txt
```

2. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

3. Install Tesseract OCR:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

### Usage

#### Basic Usage
```python
from patta_verification.patta_verifier import PattaVerifier

# Initialize verifier
verifier = PattaVerifier()

# Verify document
results = verifier.verify_patta_document('path/to/patta.pdf', 'Tamil Nadu')

# Check results
print(f"Status: {results['final_decision']['status']}")
print(f"Confidence: {results['final_decision']['confidence']}%")
```

#### Web Interface
1. Start the Flask application:
```bash
cd webgis
python simple_working_app.py
```

2. Open browser to `http://localhost:5000`

3. Upload a Patta document and select verification options

## 📋 Verification Types

### 1. Full Verification
- Complete OCR extraction
- Portal verification
- GIS coordinate validation
- Authentication feature checks
- EC cross-validation
- Comprehensive decision logic

### 2. Basic Verification
- OCR extraction
- Portal verification
- Basic decision logic

### 3. Quick Verification
- OCR extraction only
- Basic field validation
- Quick decision

## 🔧 API Endpoints

### Upload and Verify
```
POST /api/verification/upload_and_verify
```
**Form Data:**
- `file`: Patta document
- `state`: State for verification (optional)
- `verification_type`: full/basic/quick (optional)

### Verify Existing Document
```
POST /api/verification/verify_existing
```
**JSON Data:**
```json
{
  "file_path": "/path/to/document.pdf",
  "state": "Tamil Nadu",
  "verification_type": "full"
}
```

### Get Verification Status
```
GET /api/verification/get_verification_status/<verification_id>
```

### Get Verification History
```
GET /api/verification/get_verification_history
```

### Get Supported States
```
GET /api/verification/get_supported_states
```

## 📊 Verification Results

### Response Format
```json
{
  "success": true,
  "verification_results": {
    "status": "completed",
    "final_decision": {
      "status": "ACCEPTED|REJECTED|FLAGGED_FOR_REVIEW",
      "confidence": 85,
      "reasoning": [
        "✅ High OCR quality",
        "✅ All required fields present and valid",
        "✅ Portal verification successful"
      ],
      "recommendations": [
        "Document is verified and accepted"
      ]
    },
    "ocr_extraction": {
      "fields": {
        "patta_number": "12345",
        "survey_number": "678/1",
        "district": "Chennai",
        "village": "Sample Village",
        "owner_name": "Rajesh Kumar"
      },
      "confidence_scores": {
        "patta_number": 95.0,
        "survey_number": 92.0
      }
    },
    "portal_verification": {
      "verified": true,
      "matches": {
        "owner_name": true,
        "land_type": true,
        "overall_match": true
      }
    },
    "gis_verification": {
      "coordinates_match": true,
      "location_accuracy": 95.0
    },
    "authentication": {
      "qr_code_valid": true,
      "watermark_present": true,
      "authentication_score": 80
    }
  }
}
```

## 🎯 Decision Rules

### Acceptance Criteria (Score ≥ 80)
- ✅ High OCR quality (≥80%)
- ✅ All required fields present and valid
- ✅ Portal verification successful
- ✅ Portal data matches document
- ✅ GIS coordinates match
- ✅ Strong authentication features (≥70%)
- ❌ No tampering detected
- ❌ No legal disputes in EC

### Flag for Review (Score 60-79)
- ⚠️ Moderate OCR quality (60-79%)
- ⚠️ Some portal data mismatches
- ⚠️ Moderate authentication features (40-69%)
- ⚠️ Loan liens present

### Rejection Criteria (Score < 60)
- ❌ Poor OCR quality (<60%)
- ❌ Missing required fields
- ❌ Portal verification failed
- ❌ GIS coordinate mismatch
- ❌ Weak authentication features (<40%)
- ❌ Document tampering detected
- ❌ Legal disputes detected

## 🔍 Field Extraction Patterns

The system uses regex patterns to extract:

- **Patta Number**: `Patta\s*[Nn]o[:\s]*([A-Z0-9/-]+)`
- **Survey Number**: `Survey\s*[Nn]o[:\s]*([A-Z0-9/-]+)`
- **District**: `District[:\s]*([A-Za-z\s]+)`
- **Taluk/Mandal**: `(?:Taluk|Mandal)[:\s]*([A-Za-z\s]+)`
- **Village**: `Village[:\s]*([A-Za-z\s]+)`
- **Owner Name**: `(?:Owner|Holder|Name)[:\s]*([A-Za-z\s.]+)`
- **Land Type**: `(?:Land\s*Type|Type)[:\s]*(Wet|Dry|Irrigated|Non-irrigated)`
- **Extent**: `(?:Extent|Area)[:\s]*([0-9.]+)\s*(?:hectares?|acres?|cents?)`
- **Coordinates**: `(\d+\.\d+)[°\s]*[NS][,\s]*(\d+\.\d+)[°\s]*[EW]`

## 🛠 Configuration

### State Portal Configuration
```python
state_portals = {
    'Tamil Nadu': {
        'url': 'https://eservices.tn.gov.in',
        'api_endpoint': '/api/patta-verification',
        'fields': ['district', 'taluk', 'village', 'survey_number', 'patta_number']
    },
    # Add more states as needed
}
```

### OCR Configuration
```python
# Tesseract path (adjust for your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# OCR confidence threshold
ocr_confidence_threshold = 90
```

## 🧪 Testing

### Test with Sample Document
```python
# Run the verification system
python patta_verification/patta_verifier.py
```

### Test API Endpoints
```bash
# Test upload and verify
curl -X POST -F "file=@sample_patta.pdf" -F "state=Tamil Nadu" -F "verification_type=full" http://localhost:5000/api/verification/upload_and_verify
```

## 📝 Logging

The system provides comprehensive logging:
- OCR extraction progress
- Portal verification status
- GIS validation results
- Authentication checks
- Final decision reasoning

## 🔒 Security Features

1. **File Validation**: Checks file type and size
2. **Tampering Detection**: Identifies document modifications
3. **Authentication Verification**: Validates QR codes and watermarks
4. **Portal Integration**: Cross-validates with official databases
5. **Audit Trail**: Maintains verification history

## 🚨 Error Handling

The system handles various error scenarios:
- Invalid file formats
- OCR extraction failures
- Portal connectivity issues
- GIS validation errors
- Authentication failures

## 📈 Performance

- **OCR Processing**: ~2-5 seconds per page
- **Portal Verification**: ~1-3 seconds
- **GIS Validation**: ~1-2 seconds
- **Authentication Checks**: ~1-2 seconds
- **Total Processing Time**: ~5-12 seconds per document

## 🔮 Future Enhancements

1. **Machine Learning**: Train models for better field extraction
2. **Blockchain Integration**: Store verification results on blockchain
3. **Mobile App**: Native mobile application
4. **Batch Processing**: Process multiple documents simultaneously
5. **Advanced Analytics**: Verification statistics and insights

## 📞 Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify all dependencies are installed correctly
3. Ensure Tesseract OCR is properly configured
4. Check network connectivity for portal verification

## 📄 License

This project is part of the FRA Sentinel system for Forest Rights Act document verification.









