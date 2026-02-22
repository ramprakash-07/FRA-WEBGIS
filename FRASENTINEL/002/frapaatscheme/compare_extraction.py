#!/usr/bin/env python3
"""
Compare expected vs extracted Patta data
"""

def compare_extraction():
    """Compare expected data with actual extraction"""
    
    print("🔍 COMPARISON: EXPECTED vs EXTRACTED DATA")
    print("=" * 60)
    
    # Expected data
    expected = {
        "district": "Cuddalore",
        "taluk": "Kurinjipadi", 
        "village": "Arugampattu",
        "patta_number": "366",
        "owner_name": "Anandha Priya",
        "relationship": "Wife of Ramasundaran",
        "survey_number": "8",
        "extent_acres": "1.08",
        "signed_by": "Annadurai P, Tahsildar",
        "signed_on": "01/02/2016 09:04:32 PM"
    }
    
    # Actually extracted data
    extracted = {
        "relationship": "Wife of ஆனந்தபிரியா",
        "signed_on": "01/02/2016 09:04:32:PM",
        "reference_number": "RTR1482/15",
        "verification_url": "https://eservices.tn.gov.in"
    }
    
    print("\n📋 EXPECTED DATA:")
    for key, value in expected.items():
        print(f"   {key}: {value}")
    
    print("\n📊 ACTUALLY EXTRACTED:")
    for key, value in extracted.items():
        print(f"   {key}: {value}")
    
    print("\n🔍 DETAILED ANALYSIS:")
    print("-" * 40)
    
    # Check each field
    matches = 0
    partial_matches = 0
    missing = 0
    
    for key, expected_value in expected.items():
        if key in extracted:
            extracted_value = extracted[key]
            if expected_value == extracted_value:
                print(f"✅ {key}: Perfect match")
                matches += 1
            elif key == "signed_on" and "01/02/2016" in extracted_value:
                print(f"⚠️  {key}: Partial match (date correct)")
                partial_matches += 1
            else:
                print(f"❌ {key}: Mismatch")
                print(f"   Expected: {expected_value}")
                print(f"   Got: {extracted_value}")
        else:
            print(f"❌ {key}: Missing")
            missing += 1
    
    print(f"\n📈 SUMMARY:")
    print(f"   Perfect matches: {matches}")
    print(f"   Partial matches: {partial_matches}")
    print(f"   Missing fields: {missing}")
    print(f"   Extraction rate: {((matches + partial_matches) / len(expected)) * 100:.1f}%")
    
    print(f"\n🎯 ISSUES IDENTIFIED:")
    print("   1. OCR regex patterns need improvement")
    print("   2. Tamil text recognition incomplete")
    print("   3. Missing field extraction for key data")
    print("   4. Owner name extraction needs refinement")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("   1. Improve regex patterns for Tamil text")
    print("   2. Add image preprocessing for better OCR")
    print("   3. Enhance field-specific extraction logic")
    print("   4. Test with higher resolution images")

if __name__ == "__main__":
    compare_extraction()

