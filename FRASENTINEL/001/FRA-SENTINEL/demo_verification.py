#!/usr/bin/env python3
"""
Demo script for Patta Document Verification System
Shows how to use the verification system with sample data
"""

import os
import sys
import json
from datetime import datetime

def demo_verification_process():
    """Demonstrate the complete verification process"""
    
    print("🔍 Patta Document Verification System Demo")
    print("=" * 50)
    
    # Simulate the verification process
    print("\n📋 Step 1: Document Upload")
    print("  User uploads a Patta document (PDF/Image)")
    print("  System validates file format and size")
    
    print("\n🔍 Step 2: OCR Extraction")
    print("  Extracting text from document using Tesseract OCR")
    print("  Looking for required fields:")
    
    sample_extracted_data = {
        "patta_number": "12345",
        "survey_number": "678/1", 
        "district": "Chennai",
        "taluk": "Tambaram",
        "village": "Sample Village",
        "owner_name": "Rajesh Kumar",
        "land_type": "Dry",
        "extent": "2.5 hectares",
        "coordinates": "12.9716°N, 77.5946°E"
    }
    
    for field, value in sample_extracted_data.items():
        print(f"    ✅ {field.replace('_', ' ').title()}: {value}")
    
    print("\n🌐 Step 3: Portal Verification")
    print("  Connecting to Tamil Nadu e-Services portal...")
    print("  Verifying Patta Number: 12345")
    print("  Cross-checking with official records...")
    print("  ✅ Portal verification successful")
    print("  ✅ Owner name matches: Rajesh Kumar")
    print("  ✅ Land details match: Dry, 2.5 hectares")
    
    print("\n🗺️ Step 4: GIS Verification")
    print("  Validating geographical coordinates...")
    print("  Document coordinates: 12.9716°N, 77.5946°E")
    print("  Portal coordinates: 12.9716°N, 77.5946°E")
    print("  Distance: 0.0 meters")
    print("  ✅ GIS coordinates match perfectly")
    
    print("\n🔐 Step 5: Authentication Checks")
    print("  Checking for QR code...")
    print("  ✅ QR code found and valid")
    print("  Checking for watermark...")
    print("  ✅ Official watermark detected")
    print("  Checking for digital signature...")
    print("  ⚠️ No digital signature (acceptable)")
    print("  Checking for tampering...")
    print("  ✅ No signs of tampering detected")
    print("  Authentication Score: 80/100")
    
    print("\n📜 Step 6: Encumbrance Certificate Check")
    print("  Checking with Registrar Office records...")
    print("  ✅ No legal disputes found")
    print("  ✅ No loan liens present")
    print("  ✅ Owner name matches EC records")
    
    print("\n⚖️ Step 7: Final Decision")
    print("  Calculating verification score...")
    print("  OCR Quality: 20/20 points")
    print("  Required Fields: 20/20 points")
    print("  Portal Verification: 25/25 points")
    print("  Data Matches: 10/10 points")
    print("  GIS Verification: 15/15 points")
    print("  Authentication: 20/20 points")
    print("  EC Validation: 10/10 points")
    print("  Total Score: 120/120 (100%)")
    
    print("\n🎯 FINAL DECISION: ACCEPTED")
    print("  Confidence: 100%")
    print("  Status: ✅ Document is verified and accepted")
    print("  Recommendation: Proceed with transaction")
    
    print("\n📊 Verification Summary:")
    print("  Document Hash: a1b2c3d4e5f6...")
    print("  Verification ID: VER_20241215_143022")
    print("  Processing Time: 8.5 seconds")
    print("  All checks passed successfully")

def demo_rejection_scenario():
    """Demonstrate a rejection scenario"""
    
    print("\n\n❌ Rejection Scenario Demo")
    print("=" * 30)
    
    print("\n📋 Document with Issues:")
    print("  Patta Number: INVALID123")
    print("  Survey Number: Missing")
    print("  Owner Name: John Doe (mismatch)")
    print("  Coordinates: 0.0°N, 0.0°E (invalid)")
    
    print("\n🔍 Verification Results:")
    print("  OCR Quality: 15/20 points (poor quality)")
    print("  Required Fields: 0/20 points (missing fields)")
    print("  Portal Verification: 0/25 points (not found)")
    print("  GIS Verification: 0/15 points (invalid coordinates)")
    print("  Authentication: 10/20 points (no QR code)")
    print("  Total Score: 25/120 (21%)")
    
    print("\n🎯 FINAL DECISION: REJECTED")
    print("  Confidence: 21%")
    print("  Status: ❌ Document verification failed")
    print("  Recommendation: Do not proceed with transaction")
    print("  Issues: Missing required fields, portal verification failed")

def demo_api_usage():
    """Demonstrate API usage"""
    
    print("\n\n🌐 API Usage Demo")
    print("=" * 20)
    
    print("\n📤 Upload and Verify Document:")
    print("  POST /api/verification/upload_and_verify")
    print("  Content-Type: multipart/form-data")
    print("  Form Data:")
    print("    - file: patta_document.pdf")
    print("    - state: Tamil Nadu")
    print("    - verification_type: full")
    
    print("\n📥 Response:")
    sample_response = {
        "success": True,
        "verification_results": {
            "status": "completed",
            "final_decision": {
                "status": "ACCEPTED",
                "confidence": 95,
                "reasoning": [
                    "✅ High OCR quality",
                    "✅ All required fields present and valid",
                    "✅ Portal verification successful"
                ],
                "recommendations": [
                    "Document is verified and accepted"
                ]
            }
        }
    }
    
    print(json.dumps(sample_response, indent=2))

def main():
    """Main demo function"""
    
    print("🎭 Patta Document Verification System Demo")
    print("This demo shows how the verification system works")
    print("=" * 60)
    
    # Run demos
    demo_verification_process()
    demo_rejection_scenario()
    demo_api_usage()
    
    print("\n\n🚀 Getting Started:")
    print("1. Run setup: python setup_verification_system.py")
    print("2. Start app: cd webgis && python simple_working_app.py")
    print("3. Open browser: http://localhost:5000")
    print("4. Upload a Patta document for verification")
    
    print("\n📚 For more information:")
    print("- Read patta_verification/README.md")
    print("- Run tests: python patta_verification/test_verification.py")
    print("- Check API docs in verification_api.py")

if __name__ == "__main__":
    main()









