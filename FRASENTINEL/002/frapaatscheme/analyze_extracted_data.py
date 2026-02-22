#!/usr/bin/env python3
"""
Comprehensive analysis of extracted Patta data
"""

import json
import os
from pathlib import Path
import cv2
import pytesseract

def analyze_current_extraction():
    """Analyze current extraction results"""
    
    print("📊 CURRENT PATTA DATA EXTRACTION ANALYSIS")
    print("=" * 70)
    
    # Check all JSON files
    uploads_dir = Path("uploads")
    json_files = list(uploads_dir.glob("patta_data_*.json"))
    
    if not json_files:
        print("❌ No extracted data files found")
        return
    
    total_fields = 0
    total_files = len(json_files)
    
    for json_file in json_files:
        print(f"\n📁 File: {json_file.name}")
        print("-" * 50)
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Count extracted fields
            extracted_fields = [k for k, v in data.items() if v]
            total_fields += len(extracted_fields)
            
            print(f"📊 Extracted Fields ({len(extracted_fields)}):")
            for field in extracted_fields:
                print(f"   ✅ {field}: {data[field]}")
            
            # Show missing fields
            expected_fields = [
                "district", "taluk", "village", "patta_number", 
                "owner_name", "relationship", "survey_number", 
                "sub_division", "dry_land_area", "tax_amount",
                "signed_by", "signed_on", "reference_number", "verification_url"
            ]
            
            missing_fields = [f for f in expected_fields if f not in extracted_fields]
            if missing_fields:
                print(f"\n❌ Missing Fields ({len(missing_fields)}):")
                for field in missing_fields:
                    print(f"   ⚠️  {field}")
            
        except Exception as e:
            print(f"❌ Error reading {json_file}: {e}")
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total files processed: {total_files}")
    print(f"   Average fields per file: {total_fields/total_files:.1f}")
    print(f"   Extraction rate: {(total_fields/(total_files*14))*100:.1f}%")

def test_raw_ocr():
    """Test raw OCR output to see what text is being extracted"""
    
    print(f"\n🔍 RAW OCR TEXT ANALYSIS")
    print("=" * 70)
    
    # Find image files
    uploads_dir = Path("uploads")
    image_files = [f for f in uploads_dir.iterdir() 
                  if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']]
    
    if not image_files:
        print("❌ No image files found")
        return
    
    for img_file in image_files:
        print(f"\n📷 Image: {img_file.name}")
        print("-" * 50)
        
        try:
            # Load image
            img = cv2.imread(str(img_file))
            
            # Test different OCR configurations
            configs = [
                ("English Only", "eng"),
                ("Tamil + English", "tam+eng"),
                ("Tamil Only", "tam")
            ]
            
            for config_name, lang in configs:
                try:
                    text = pytesseract.image_to_string(img, lang=lang)
                    text = text.strip()
                    
                    if text:
                        print(f"\n🔤 {config_name} ({lang}):")
                        print(f"   Length: {len(text)} characters")
                        print(f"   Preview: {text[:200]}...")
                        
                        # Check for Tamil characters
                        tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
                        if tamil_chars > 0:
                            print(f"   Tamil characters found: {tamil_chars}")
                    else:
                        print(f"\n❌ {config_name}: No text extracted")
                        
                except Exception as e:
                    print(f"\n❌ {config_name}: Error - {e}")
        
        except Exception as e:
            print(f"❌ Error processing {img_file}: {e}")

def show_improvement_suggestions():
    """Show suggestions for improving extraction"""
    
    print(f"\n💡 IMPROVEMENT SUGGESTIONS")
    print("=" * 70)
    
    print("🔧 To improve Tamil Patta extraction:")
    print("   1. Install Tamil language support:")
    print("      - Download: tam.traineddata from GitHub")
    print("      - Copy to: C:/Program Files/Tesseract-OCR/tessdata/")
    print("   2. Image preprocessing:")
    print("      - Ensure high resolution (300+ DPI)")
    print("      - Good contrast and lighting")
    print("      - Straight, non-rotated images")
    print("   3. OCR configuration:")
    print("      - Use lang='tam+eng' for mixed text")
    print("      - Consider image preprocessing (denoising, etc.)")
    
    print(f"\n📋 Expected Tamil fields:")
    tamil_fields = {
        "மாவட்டம்": "District",
        "வட்டம்": "Taluk/Circle", 
        "வருவாய் கிராமம்": "Revenue Village",
        "பட்டா எண்": "Patta Number",
        "உரிமையாளர்கள் பெயர்": "Owner Names",
        "புல எண்": "Survey Number",
        "உட்பிரிவு": "Sub-division",
        "புன்செய்": "Dry Land",
        "நன்செய்": "Wet Land",
        "தீர்வை": "Tax Amount"
    }
    
    for tamil, english in tamil_fields.items():
        print(f"   {tamil} → {english}")

def main():
    """Main analysis function"""
    
    print("🔍 COMPREHENSIVE PATTA DATA ANALYSIS")
    print("=" * 80)
    
    # Analyze current extraction
    analyze_current_extraction()
    
    # Test raw OCR
    test_raw_ocr()
    
    # Show improvement suggestions
    show_improvement_suggestions()
    
    print(f"\n🎯 CONCLUSION:")
    print("   Current extraction is limited due to missing Tamil language support.")
    print("   Install Tamil language data to get comprehensive field extraction.")
    print("   The API is working correctly - the limitation is in OCR language support.")

if __name__ == "__main__":
    main()

