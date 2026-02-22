#!/usr/bin/env python3
"""
Test script for Patta OCR functionality
Run this to test the OCR service independently
"""

import os
import json
from digitization.ocr_service import PattaOCRService

def test_ocr_service():
    """Test the OCR service with a sample image"""
    
    # Initialize OCR service
    ocr_service = PattaOCRService()
    
    # Check if there are any images in uploads directory
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        image_files = [f for f in os.listdir(uploads_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
        
        if image_files:
            print(f"Found {len(image_files)} image(s) in uploads directory:")
            for img_file in image_files:
                print(f"  - {img_file}")
            
            # Test with the first image
            test_image = os.path.join(uploads_dir, image_files[0])
            print(f"\nTesting OCR with: {test_image}")
            
            # Extract data
            result = ocr_service.extract_patta_data(test_image)
            
            # Display results
            print("\n" + "="*50)
            print("EXTRACTED PATTA DATA:")
            print("="*50)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # Save to file
            output_file = "test_patta_extraction.json"
            ocr_service.save_extracted_data(result, output_file)
            print(f"\nData saved to: {output_file}")
            
        else:
            print("No image files found in uploads directory.")
            print("Please upload a Patta document image to test OCR functionality.")
    else:
        print("Uploads directory not found. Creating it...")
        os.makedirs(uploads_dir, exist_ok=True)
        print("Please place a Patta document image in the 'uploads' directory and run this test again.")

if __name__ == "__main__":
    test_ocr_service()

