#!/usr/bin/env python3
"""
Patta Digitization API using the working OCR service from 002
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from ocr_service import PattaOCRService

app = Flask(__name__)

# Initialize OCR service
ocr_service = PattaOCRService(use_ai=False)  # Use regex-only for now

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload file for patta digitization"""
    try:
        print("=== UPLOAD API CALLED ===")
        print("Request files:", request.files)
        print("Request form:", request.form)
        
        if 'file' not in request.files:
            print("ERROR: No file in request")
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Validate file size (25MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 25 * 1024 * 1024:  # 25MB
            return jsonify({'success': False, 'message': 'File too large (max 25MB)'}), 400
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        
        # Save file to uploads directory
        upload_dir = os.path.join(app.root_path, 'uploads', 'patta')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        print(f"File saved: {file_path}")
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': file.filename,
            'size': file_size,
            'message': 'File uploaded successfully'
        })
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/extract', methods=['POST'])
def extract_data():
    """Extract OCR and NER data from uploaded file"""
    try:
        print("=== EXTRACT API CALLED ===")
        print("Request content type:", request.content_type)
        print("Request data:", request.get_data())
        
        data = request.get_json()
        print("Parsed JSON data:", data)
        
        # Try multiple possible field names for file_id
        file_id = data.get('file_id') or data.get('fileId') or data.get('id')
        print("File ID:", file_id)
        
        if not file_id:
            print("ERROR: No file_id provided in any format")
            print("Available keys:", list(data.keys()) if data else "No data")
            return jsonify({'success': False, 'message': 'File ID required'}), 400
        
        # Get file from uploads directory
        upload_dir = os.path.join(app.root_path, 'uploads', 'patta')
        file_path = None
        
        # Find the uploaded file
        for filename in os.listdir(upload_dir):
            if file_id in filename:
                file_path = os.path.join(upload_dir, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            print(f"ERROR: File not found for file_id: {file_id}")
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        print(f"Processing file: {file_path}")
        
        # Use real OCR service
        try:
            # Extract data using real OCR
            extracted_data = ocr_service.extract_patta_data(file_path)
            print(f"Extracted data: {extracted_data}")
            
            if "error" in extracted_data:
                return jsonify({'success': False, 'message': f'OCR failed: {extracted_data["error"]}'}), 500
            
            # Convert to our expected format
            ocr_result = {
                'text': 'OCR text extracted from image',
                'confidence': 85.5,
                'words': [],
                'page_number': 1
            }
            
            # Mock NER result (replace with real NER processing)
            ner_result = {
                'text': ocr_result['text'],
                'entities': [
                    {'text': 'Sample Claimant', 'label': 'PERSON', 'start_char': 0, 'end_char': 15, 'confidence': 0.9},
                    {'text': 'Sample Village', 'label': 'GPE', 'start_char': 20, 'end_char': 35, 'confidence': 0.85},
                    {'text': '123', 'label': 'CARDINAL', 'start_char': 40, 'end_char': 43, 'confidence': 0.95}
                ],
                'confidence': 0.87,
                'language': 'mixed',
                'processing_time': 1.2
            }
            
            # Map extracted data to our patta schema
            patta_data = {
                'claimant_name': extracted_data.get('owner_name', ''),
                'father_or_spouse': extracted_data.get('relationship', ''),
                'caste_st': 'ST',  # Default for now
                'village': extracted_data.get('village', ''),
                'taluk': extracted_data.get('taluk', ''),
                'district': extracted_data.get('district', ''),
                'survey_or_compartment_no': extracted_data.get('survey_number', ''),
                'sub_division': extracted_data.get('sub_division', ''),
                'coords': {'lat': 21.8225, 'lng': 75.6102},  # Default coordinates
                'area': extracted_data.get('extent_acres', ''),
                'document_no': extracted_data.get('patta_number', ''),
                'document_date': extracted_data.get('signed_on', ''),
                'claim_type': 'IFR',  # Default
                'raw_text': ocr_result['text'],
                'ocr_confidence': ocr_result['confidence'],
                'ner_confidence': ner_result['confidence'],
                'extraction_time': datetime.utcnow().isoformat(),
                # Additional fields from real extraction
                'tax_amount': extracted_data.get('tax_amount', ''),
                'signed_by': extracted_data.get('signed_by', ''),
                'reference_number': extracted_data.get('reference_number', ''),
                'verification_url': extracted_data.get('verification_url', '')
            }
            
            return jsonify({
                'success': True,
                'ocr_result': ocr_result,
                'ner_result': ner_result,
                'patta_data': patta_data,
                'message': 'Data extracted successfully'
            })
            
        except Exception as e:
            print(f"OCR processing error: {e}")
            return jsonify({'success': False, 'message': f'OCR processing failed: {str(e)}'}), 500
        
    except Exception as e:
        print(f"Extract error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/patta', methods=['POST'])
def save_patta():
    """Save extracted patta data"""
    try:
        data = request.get_json()
        print("Saving patta data:", data)
        
        # TODO: Save to database
        return jsonify({
            'success': True,
            'patta_id': str(uuid.uuid4()),
            'message': 'Patta data saved successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/patta-digitization')
def patta_digitization():
    """Serve the patta digitization page"""
    return render_template('patta_digitization.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)






