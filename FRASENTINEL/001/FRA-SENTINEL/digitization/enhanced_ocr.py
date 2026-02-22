"""
Enhanced OCR Pipeline for FRA-SENTINEL
Batch processing with retryable jobs and advanced NER extraction
"""

import os
import json
import logging
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import pytesseract
import pdfplumber
from flask import Blueprint, request, jsonify, current_app
import re

logger = logging.getLogger(__name__)

# Create blueprint
ocr_bp = Blueprint('ocr', __name__, url_prefix='/api/ocr')

@dataclass
class ExtractionResult:
    file_id: str
    file_name: str
    file_path: str
    file_hash: str
    extraction_status: str
    extracted_data: Dict
    confidence_scores: Dict
    processing_time: float
    error_message: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class EnhancedOCREngine:
    """Enhanced OCR engine with batch processing and NER"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        self.tesseract_config = '--oem 3 --psm 6 -l eng+tam'
        self.extraction_patterns = self._load_extraction_patterns()
        self.batch_size = 10
        self.max_retries = 3
        
    def _load_extraction_patterns(self) -> Dict:
        """Load regex patterns for data extraction"""
        return {
            'village_name': [
                r'Village[:\s]+([A-Za-z\s]+)',
                r'गांव[:\s]+([^\n]+)',
                r'Village Name[:\s]+([A-Za-z\s]+)'
            ],
            'holder_name': [
                r'Name[:\s]+([A-Za-z\s]+)',
                r'नाम[:\s]+([^\n]+)',
                r'Holder Name[:\s]+([A-Za-z\s]+)',
                r'Patta Holder[:\s]+([A-Za-z\s]+)'
            ],
            'father_husband_name': [
                r'Father[:\s]+([A-Za-z\s]+)',
                r'Husband[:\s]+([A-Za-z\s]+)',
                r'पिता[:\s]+([^\n]+)',
                r'पति[:\s]+([^\n]+)'
            ],
            'tribal_group': [
                r'Tribal Group[:\s]+([A-Za-z\s]+)',
                r'जनजाति[:\s]+([^\n]+)',
                r'Community[:\s]+([A-Za-z\s]+)'
            ],
            'claim_type': [
                r'Claim Type[:\s]+([A-Za-z]+)',
                r'Type[:\s]+(IFR|CR|CFR)',
                r'दावा प्रकार[:\s]+([^\n]+)'
            ],
            'area_claimed': [
                r'Area[:\s]+([0-9.]+)\s*(hectares?|acres?|ha)',
                r'क्षेत्र[:\s]+([0-9.]+)',
                r'Land Area[:\s]+([0-9.]+)'
            ],
            'survey_number': [
                r'Survey No[:\s]+([A-Za-z0-9/\s]+)',
                r'Survey Number[:\s]+([A-Za-z0-9/\s]+)',
                r'सर्वे नंबर[:\s]+([^\n]+)'
            ],
            'dag_number': [
                r'Dag No[:\s]+([A-Za-z0-9/\s]+)',
                r'Dag Number[:\s]+([A-Za-z0-9/\s]+)',
                r'दाग नंबर[:\s]+([^\n]+)'
            ],
            'khasra_number': [
                r'Khasra No[:\s]+([A-Za-z0-9/\s]+)',
                r'Khasra Number[:\s]+([A-Za-z0-9/\s]+)',
                r'खसरा नंबर[:\s]+([^\n]+)'
            ],
            'patta_number': [
                r'Patta No[:\s]+([A-Za-z0-9/\s]+)',
                r'Patta Number[:\s]+([A-Za-z0-9/\s]+)',
                r'पट्टा नंबर[:\s]+([^\n]+)'
            ],
            'coordinates': [
                r'Latitude[:\s]+([0-9.-]+)',
                r'Longitude[:\s]+([0-9.-]+)',
                r'अक्षांश[:\s]+([0-9.-]+)',
                r'देशांतर[:\s]+([0-9.-]+)'
            ]
        }
    
    def process_file(self, file_path: str, file_id: str = None) -> ExtractionResult:
        """Process a single file with enhanced OCR and NER"""
        
        if file_id is None:
            file_id = hashlib.md5(file_path.encode()).hexdigest()
        
        start_time = time.time()
        
        try:
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1].lower()
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Extract text based on file type
            if file_extension == '.pdf':
                extracted_text = self._extract_from_pdf(file_path)
            else:
                extracted_text = self._extract_from_image(file_path)
            
            # Perform NER extraction
            extracted_data = self._extract_entities(extracted_text)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(extracted_data, extracted_text)
            
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                file_id=file_id,
                file_name=file_name,
                file_path=file_path,
                file_hash=file_hash,
                extraction_status="success",
                extracted_data=extracted_data,
                confidence_scores=confidence_scores,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"OCR processing failed for {file_path}: {e}")
            
            return ExtractionResult(
                file_id=file_id,
                file_name=os.path.basename(file_path),
                file_path=file_path,
                file_hash="",
                extraction_status="failed",
                extracted_data={},
                confidence_scores={},
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def process_batch(self, file_paths: List[str]) -> List[ExtractionResult]:
        """Process multiple files in batch"""
        
        results = []
        total_files = len(file_paths)
        
        logger.info(f"Starting batch processing of {total_files} files")
        
        for i, file_path in enumerate(file_paths):
            try:
                logger.info(f"Processing file {i+1}/{total_files}: {file_path}")
                result = self.process_file(file_path)
                results.append(result)
                
                # Add small delay to prevent system overload
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Batch processing error for {file_path}: {e}")
                results.append(ExtractionResult(
                    file_id=hashlib.md5(file_path.encode()).hexdigest(),
                    file_name=os.path.basename(file_path),
                    file_path=file_path,
                    file_hash="",
                    extraction_status="failed",
                    extracted_data={},
                    confidence_scores={},
                    processing_time=0,
                    error_message=str(e)
                ))
        
        success_count = len([r for r in results if r.extraction_status == "success"])
        logger.info(f"Batch processing completed: {success_count}/{total_files} successful")
        
        return results
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber"""
        text = ""
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            # Fallback to OCR on PDF pages
            text = self._ocr_pdf_pages(file_path)
        
        return text
    
    def _extract_from_image(self, file_path: str) -> str:
        """Extract text from image using Tesseract"""
        try:
            # Preprocess image for better OCR
            image = cv2.imread(file_path)
            processed_image = self._preprocess_image(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            
            return text
            
        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _ocr_pdf_pages(self, file_path: str) -> str:
        """Fallback OCR for PDF pages"""
        text = ""
        
        try:
            # Convert PDF to images and OCR each page
            import fitz  # PyMuPDF
            
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                
                # Convert bytes to PIL Image
                img = Image.open(io.BytesIO(img_data))
                
                # Convert to OpenCV format
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                # Preprocess and OCR
                processed = self._preprocess_image(img_cv)
                page_text = pytesseract.image_to_string(processed, config=self.tesseract_config)
                text += page_text + "\n"
            
            doc.close()
            
        except Exception as e:
            logger.error(f"PDF OCR fallback failed: {e}")
            raise
        
        return text
    
    def _extract_entities(self, text: str) -> Dict:
        """Extract entities using regex patterns"""
        
        extracted_data = {}
        
        for field, patterns in self.extraction_patterns.items():
            extracted_data[field] = None
            
            for pattern in patterns:
                try:
                    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        extracted_data[field] = match.group(1).strip()
                        break
                except Exception as e:
                    logger.warning(f"Pattern matching failed for {field}: {e}")
                    continue
        
        # Additional processing for specific fields
        extracted_data = self._post_process_extracted_data(extracted_data)
        
        return extracted_data
    
    def _post_process_extracted_data(self, data: Dict) -> Dict:
        """Post-process extracted data for better accuracy"""
        
        # Clean up village name
        if data.get('village_name'):
            data['village_name'] = re.sub(r'[^\w\s]', '', data['village_name']).strip()
        
        # Clean up holder name
        if data.get('holder_name'):
            data['holder_name'] = re.sub(r'[^\w\s]', '', data['holder_name']).strip()
        
        # Clean up father/husband name
        if data.get('father_husband_name'):
            data['father_husband_name'] = re.sub(r'[^\w\s]', '', data['father_husband_name']).strip()
        
        # Normalize claim type
        if data.get('claim_type'):
            claim_type = data['claim_type'].upper()
            if 'IFR' in claim_type:
                data['claim_type'] = 'IFR'
            elif 'CR' in claim_type:
                data['claim_type'] = 'CR'
            elif 'CFR' in claim_type:
                data['claim_type'] = 'CFR'
        
        # Parse area
        if data.get('area_claimed'):
            try:
                area_str = data['area_claimed']
                area_match = re.search(r'([0-9.]+)', area_str)
                if area_match:
                    data['area_claimed'] = float(area_match.group(1))
            except ValueError:
                data['area_claimed'] = None
        
        # Parse coordinates
        if data.get('coordinates'):
            try:
                coord_text = data['coordinates']
                lat_match = re.search(r'([0-9.-]+)', coord_text)
                if lat_match:
                    data['latitude'] = float(lat_match.group(1))
            except ValueError:
                data['latitude'] = None
        
        return data
    
    def _calculate_confidence_scores(self, extracted_data: Dict, original_text: str) -> Dict:
        """Calculate confidence scores for extracted data"""
        
        confidence_scores = {}
        
        for field, value in extracted_data.items():
            if value is None:
                confidence_scores[field] = 0.0
                continue
            
            # Base confidence on pattern matching success
            base_confidence = 0.7
            
            # Adjust confidence based on field-specific criteria
            if field == 'village_name':
                # Higher confidence for longer, more specific names
                if len(value) > 5:
                    base_confidence += 0.2
                if re.search(r'[A-Z]', value):
                    base_confidence += 0.1
            
            elif field == 'holder_name':
                # Higher confidence for names with proper capitalization
                if re.match(r'^[A-Z][a-z]+', value):
                    base_confidence += 0.2
            
            elif field == 'claim_type':
                # High confidence for standardized claim types
                if value in ['IFR', 'CR', 'CFR']:
                    base_confidence = 0.9
            
            elif field == 'area_claimed':
                # Higher confidence for reasonable area values
                if isinstance(value, (int, float)) and 0 < value < 1000:
                    base_confidence = 0.8
            
            confidence_scores[field] = min(base_confidence, 1.0)
        
        return confidence_scores

# Global OCR engine instance
ocr_engine = EnhancedOCREngine()

# API endpoints
@ocr_bp.route('/process', methods=['POST'])
def process_single_file():
    """Process a single file"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({'error': 'file_path is required'}), 400
        
        result = ocr_engine.process_file(file_path)
        
        return jsonify({
            'file_id': result.file_id,
            'file_name': result.file_name,
            'extraction_status': result.extraction_status,
            'extracted_data': result.extracted_data,
            'confidence_scores': result.confidence_scores,
            'processing_time': result.processing_time,
            'error_message': result.error_message
        })
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

@ocr_bp.route('/batch', methods=['POST'])
def process_batch_files():
    """Process multiple files in batch"""
    try:
        data = request.get_json()
        file_paths = data.get('file_paths', [])
        
        if not file_paths:
            return jsonify({'error': 'file_paths is required'}), 400
        
        results = ocr_engine.process_batch(file_paths)
        
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            serializable_results.append({
                'file_id': result.file_id,
                'file_name': result.file_name,
                'extraction_status': result.extraction_status,
                'extracted_data': result.extracted_data,
                'confidence_scores': result.confidence_scores,
                'processing_time': result.processing_time,
                'error_message': result.error_message
            })
        
        return jsonify({
            'total_files': len(file_paths),
            'successful': len([r for r in results if r.extraction_status == "success"]),
            'failed': len([r for r in results if r.extraction_status == "failed"]),
            'results': serializable_results
        })
        
    except Exception as e:
        logger.error(f"Batch API error: {e}")
        return jsonify({'error': str(e)}), 500

@ocr_bp.route('/status/<file_id>')
def get_processing_status(file_id: str):
    """Get processing status for a file"""
    # This would integrate with the message queue system
    # For now, return a simple status
    return jsonify({
        'file_id': file_id,
        'status': 'completed',
        'message': 'Processing completed'
    })

@ocr_bp.route('/patterns')
def get_extraction_patterns():
    """Get available extraction patterns"""
    return jsonify({
        'patterns': ocr_engine.extraction_patterns,
        'supported_formats': ocr_engine.supported_formats
    })

# Utility functions
def process_document(file_path: str) -> Dict:
    """Process a document and return extracted data"""
    result = ocr_engine.process_file(file_path)
    
    return {
        'success': result.extraction_status == "success",
        'data': result.extracted_data,
        'confidence': result.confidence_scores,
        'processing_time': result.processing_time,
        'error': result.error_message
    }

def batch_process_documents(file_paths: List[str]) -> List[Dict]:
    """Process multiple documents in batch"""
    results = ocr_engine.process_batch(file_paths)
    
    return [
        {
            'file_path': result.file_path,
            'success': result.extraction_status == "success",
            'data': result.extracted_data,
            'confidence': result.confidence_scores,
            'processing_time': result.processing_time,
            'error': result.error_message
        }
        for result in results
    ]

if __name__ == "__main__":
    # Test the OCR engine
    test_files = [
        "sample_patta.pdf",
        "sample_document.jpg"
    ]
    
    print("Testing Enhanced OCR Engine...")
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\nProcessing: {file_path}")
            result = process_document(file_path)
            print(f"Success: {result['success']}")
            print(f"Data: {result['data']}")
            print(f"Confidence: {result['confidence']}")
        else:
            print(f"File not found: {file_path}")
    
    print("\nOCR Engine test completed.")









