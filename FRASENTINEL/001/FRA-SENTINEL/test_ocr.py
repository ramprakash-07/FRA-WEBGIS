#!/usr/bin/env python3
"""
OCR Test Script for FRA-SENTINEL
Demonstrates OCR functionality with sample documents
"""

import os
import sys
from digitization.enhanced_ocr import process_document, batch_process_documents

def test_ocr_functionality():
    """Test OCR functionality with sample documents"""
    
    print("🔍 FRA-SENTINEL OCR Testing")
    print("=" * 50)
    
    # Check if sample files exist
    sample_files = [
        'sample_data/sample_patta_1.pdf',
        'sample_data/sample_patta_2.pdf', 
        'sample_data/sample_patta_3.pdf'
    ]
    
    existing_files = [f for f in sample_files if os.path.exists(f)]
    
    if not existing_files:
        print("❌ No sample files found. Please run: python demo_data.py")
        return
    
    print(f"📄 Found {len(existing_files)} sample files")
    print()
    
    # Test single document processing
    print("🔸 Testing Single Document Processing:")
    print("-" * 40)
    
    for i, file_path in enumerate(existing_files[:1], 1):  # Test first file
        print(f"Processing: {file_path}")
        
        try:
            result = process_document(file_path)
            
            print(f"✅ Success: {result['success']}")
            print(f"⏱️  Processing Time: {result['processing_time']:.2f}s")
            
            if result['success']:
                print("\n📋 Extracted Data:")
                for field, value in result['data'].items():
                    if value:
                        print(f"  {field}: {value}")
                
                print("\n🎯 Confidence Scores:")
                for field, score in result['confidence'].items():
                    if score > 0:
                        print(f"  {field}: {score:.2f}")
            else:
                print(f"❌ Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()
    
    # Test batch processing
    print("🔸 Testing Batch Processing:")
    print("-" * 40)
    
    try:
        results = batch_process_documents(existing_files)
        
        successful = len([r for r in results if r['success']])
        failed = len([r for r in results if not r['success']])
        
        print(f"📊 Batch Results:")
        print(f"  Total Files: {len(results)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        
        if successful > 0:
            print(f"\n📋 Sample Extracted Data:")
            for i, result in enumerate(results[:2], 1):  # Show first 2 results
                if result['success']:
                    print(f"\n  Document {i}:")
                    for field, value in result['data'].items():
                        if value:
                            print(f"    {field}: {value}")
        
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ OCR Testing Complete!")
    
    # Show OCR capabilities
    print("\n🔧 OCR Capabilities:")
    print("  • Supported Formats: PDF, JPG, JPEG, PNG, TIFF, BMP")
    print("  • Languages: English + Tamil")
    print("  • Extraction Fields: 11 different data fields")
    print("  • Batch Processing: Multiple files simultaneously")
    print("  • Confidence Scoring: Accuracy assessment")
    print("  • Error Handling: Retry mechanisms")

if __name__ == "__main__":
    test_ocr_functionality()









