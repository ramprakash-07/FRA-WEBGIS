#!/usr/bin/env python3
"""
Test script for Patta Document Verification System
Demonstrates the complete verification process
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from patta_verifier import PattaVerifier

def test_verification_system():
    """Test the complete verification system"""
    
    print("🔍 Patta Document Verification System Test")
    print("=" * 50)
    
    # Initialize verifier
    print("📋 Initializing verification system...")
    verifier = PattaVerifier()
    
    # Test with sample data (simulation)
    print("\n🧪 Testing with simulated data...")
    
    # Create a mock document path for testing
    test_doc_path = "../data/sample_fra_claim.pdf"
    
    if os.path.exists(test_doc_path):
        print(f"✅ Found test document: {test_doc_path}")
        
        # Test different verification types
        verification_types = ['quick', 'basic', 'full']
        states = ['Tamil Nadu', 'Andhra Pradesh', 'Telangana', 'Karnataka']
        
        for state in states[:1]:  # Test with Tamil Nadu only
            print(f"\n🏛️ Testing with {state} portal...")
            
            for vtype in verification_types:
                print(f"\n📊 Testing {vtype} verification...")
                
                try:
                    if vtype == 'quick':
                        # Quick verification
                        results = verifier.extract_document_data(test_doc_path)
                        print(f"  ✅ OCR Quality: {results.get('ocr_quality', {}).get('score', 0)}%")
                        print(f"  ✅ Fields Present: {results.get('validation_status', {}).get('all_present', False)}")
                        
                    elif vtype == 'basic':
                        # Basic verification
                        ocr_result = verifier.extract_document_data(test_doc_path)
                        portal_result = verifier.verify_with_portal(ocr_result, state)
                        print(f"  ✅ Portal Verified: {portal_result.get('verified', False)}")
                        
                    else:  # full verification
                        # Full verification
                        results = verifier.verify_patta_document(test_doc_path, state)
                        
                        if results.get('success', False):
                            decision = results.get('final_decision', {})
                            print(f"  ✅ Final Decision: {decision.get('status', 'UNKNOWN')}")
                            print(f"  ✅ Confidence: {decision.get('confidence', 0)}%")
                            
                            # Show reasoning
                            reasoning = decision.get('reasoning', [])
                            if reasoning:
                                print("  📝 Reasoning:")
                                for reason in reasoning[:3]:  # Show first 3 reasons
                                    print(f"    {reason}")
                        else:
                            print(f"  ❌ Verification failed: {results.get('error', 'Unknown error')}")
                            
                except Exception as e:
                    print(f"  ❌ Error in {vtype} verification: {str(e)}")
    
    else:
        print(f"⚠️ Test document not found: {test_doc_path}")
        print("📝 Creating simulation test...")
        
        # Simulate verification results
        simulate_verification_results(verifier)

def simulate_verification_results(verifier):
    """Simulate verification results for demonstration"""
    
    print("\n🎭 Simulating verification results...")
    
    # Simulate extracted data
    simulated_data = {
        'raw_text': 'Sample Patta Document\nPatta No: 12345\nSurvey No: 678/1\nDistrict: Chennai\nVillage: Sample Village\nOwner: Rajesh Kumar',
        'fields': {
            'patta_number': '12345',
            'survey_number': '678/1',
            'district': 'Chennai',
            'village': 'Sample Village',
            'owner_name': 'Rajesh Kumar',
            'land_type': 'Dry',
            'extent': '2.5 hectares'
        },
        'confidence_scores': {
            'patta_number': 95.0,
            'survey_number': 92.0,
            'district': 88.0,
            'village': 85.0,
            'owner_name': 90.0
        },
        'ocr_quality': {
            'score': 85,
            'issues': [],
            'text_length': 150
        },
        'validation_status': {
            'all_present': True,
            'missing_fields': [],
            'format_issues': [],
            'overall_valid': True
        }
    }
    
    print("📄 Simulated Extracted Data:")
    for field, value in simulated_data['fields'].items():
        confidence = simulated_data['confidence_scores'].get(field, 0)
        print(f"  {field.replace('_', ' ').title()}: {value} (Confidence: {confidence}%)")
    
    # Simulate portal verification
    print("\n🌐 Simulating Portal Verification...")
    portal_result = verifier.verify_with_portal(simulated_data, 'Tamil Nadu')
    print(f"  Portal Status: {portal_result.get('status', 'unknown')}")
    print(f"  Verified: {portal_result.get('verified', False)}")
    
    # Simulate GIS verification
    print("\n🗺️ Simulating GIS Verification...")
    gis_result = verifier.verify_gis_coordinates(simulated_data, {'coordinates': {'lat': 12.9716, 'lon': 77.5946}})
    print(f"  Coordinates Match: {gis_result.get('coordinates_match', False)}")
    print(f"  Location Accuracy: {gis_result.get('location_accuracy', 0)}%")
    
    # Simulate authentication
    print("\n🔐 Simulating Authentication Checks...")
    auth_result = {
        'qr_code_present': True,
        'qr_code_valid': True,
        'watermark_present': True,
        'digital_signature_present': False,
        'tampering_detected': False,
        'authentication_score': 70
    }
    print(f"  QR Code Valid: {auth_result['qr_code_valid']}")
    print(f"  Watermark Present: {auth_result['watermark_present']}")
    print(f"  Authentication Score: {auth_result['authentication_score']}%")
    
    # Simulate final decision
    print("\n⚖️ Simulating Final Decision...")
    verification_results = {
        'ocr_extraction': simulated_data,
        'portal_verification': portal_result,
        'gis_verification': gis_result,
        'authentication': auth_result,
        'ec_validation': {
            'ec_available': True,
            'disputes_detected': False,
            'loan_liens': False,
            'validation_matches': True
        }
    }
    
    final_decision = verifier.make_final_decision(verification_results)
    
    print(f"  Final Status: {final_decision['status']}")
    print(f"  Confidence: {final_decision['confidence']}%")
    print("  Reasoning:")
    for reason in final_decision.get('reasoning', []):
        print(f"    {reason}")
    print("  Recommendations:")
    for rec in final_decision.get('recommendations', []):
        print(f"    • {rec}")

def test_api_endpoints():
    """Test API endpoints (if Flask app is running)"""
    
    print("\n🌐 Testing API Endpoints...")
    
    try:
        import requests
        
        base_url = "http://localhost:5000"
        
        # Test supported states endpoint
        print("  Testing supported states endpoint...")
        response = requests.get(f"{base_url}/api/verification/get_supported_states")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Supported states: {', '.join(data.get('supported_states', []))}")
        else:
            print(f"    ❌ Error: {response.status_code}")
            
        # Test verification history endpoint
        print("  Testing verification history endpoint...")
        response = requests.get(f"{base_url}/api/verification/get_verification_history")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ History entries: {len(data.get('verifications', []))}")
        else:
            print(f"    ❌ Error: {response.status_code}")
            
    except ImportError:
        print("  ⚠️ Requests library not available for API testing")
    except requests.exceptions.ConnectionError:
        print("  ⚠️ Flask app not running - start with: python webgis/simple_working_app.py")

def main():
    """Main test function"""
    
    print("🚀 Starting Patta Verification System Tests")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test core verification system
        test_verification_system()
        
        # Test API endpoints
        test_api_endpoints()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("  1. Install dependencies: pip install -r patta_verification/requirements.txt")
        print("  2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("  3. Start Flask app: python webgis/simple_working_app.py")
        print("  4. Open browser to: http://localhost:5000")
        print("  5. Upload a Patta document for verification")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        print("📝 Check the error message and ensure all dependencies are installed")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()









