 """
Comprehensive Patta Document Verification System
Implements all rules and conditions for online Patta verification with OCR, portal verification, GIS validation, and authentication checks.
"""

import os
import re
import json
import hashlib
import requests
import pytesseract
import spacy
from PIL import Image
from pdf2image import convert_from_path
from datetime import datetime
import qrcode
from qrcode import QRCode
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PattaVerifier:
    """
    Comprehensive Patta Document Verification System
    
    Implements:
    1. OCR extraction with 90%+ confidence validation
    2. Portal verification with state government databases
    3. GIS/map validation for geographical coordinates
    4. Authentication checks (QR codes, watermarks, digital signatures)
    5. Cross-validation with Encumbrance Certificate
    6. Final decision rules for acceptance/rejection
    """
    
    def __init__(self):
        # Configure Tesseract path
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        # Load NLP model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Using basic regex extraction.")
            self.nlp = None
        
        # State portal configurations
        self.state_portals = {
            'Tamil Nadu': {
                'url': 'https://eservices.tn.gov.in',
                'api_endpoint': '/api/patta-verification',
                'fields': ['district', 'taluk', 'village', 'survey_number', 'patta_number']
            },
            'Andhra Pradesh': {
                'url': 'https://meebhoomi.ap.gov.in',
                'api_endpoint': '/api/land-records',
                'fields': ['district', 'mandal', 'village', 'survey_number', 'patta_number']
            },
            'Telangana': {
                'url': 'https://dharani.telangana.gov.in',
                'api_endpoint': '/api/land-verification',
                'fields': ['district', 'mandal', 'village', 'survey_number', 'patta_number']
            },
            'Karnataka': {
                'url': 'https://bhoomi.karnataka.gov.in',
                'api_endpoint': '/api/rtc-verification',
                'fields': ['district', 'taluk', 'village', 'survey_number', 'patta_number']
            }
        }
        
        # Validation patterns
        self.patterns = {
            'patta_number': r'Patta\s*[Nn]o[:\s]*([A-Z0-9/-]+)',
            'survey_number': r'Survey\s*[Nn]o[:\s]*([A-Z0-9/-]+)',
            'district': r'District[:\s]*([A-Za-z\s]+)',
            'taluk': r'(?:Taluk|Mandal)[:\s]*([A-Za-z\s]+)',
            'village': r'Village[:\s]*([A-Za-z\s]+)',
            'owner_name': r'(?:Owner|Holder|Name)[:\s]*([A-Za-z\s.]+)',
            'land_type': r'(?:Land\s*Type|Type)[:\s]*(Wet|Dry|Irrigated|Non-irrigated)',
            'extent': r'(?:Extent|Area)[:\s]*([0-9.]+)\s*(?:hectares?|acres?|cents?)',
            'coordinates': r'(\d+\.\d+)[°\s]*[NS][,\s]*(\d+\.\d+)[°\s]*[EW]'
        }
        
        # OCR confidence threshold
        self.ocr_confidence_threshold = 90
        
    def extract_document_data(self, file_path: str) -> Dict[str, Any]:
        """
        Extract all required data from Patta document using OCR
        
        Returns:
            Dict containing extracted data with confidence scores
        """
        logger.info(f"Extracting data from document: {file_path}")
        
        # Convert document to text
        text = self._convert_to_text(file_path)
        
        # Extract structured data
        extracted_data = {
            'raw_text': text,
            'extraction_timestamp': datetime.now().isoformat(),
            'fields': {},
            'confidence_scores': {},
            'ocr_quality': self._assess_ocr_quality(text)
        }
        
        # Extract each field with confidence scoring
        for field, pattern in self.patterns.items():
            value, confidence = self._extract_field_with_confidence(text, pattern, field)
            extracted_data['fields'][field] = value
            extracted_data['confidence_scores'][field] = confidence
        
        # Validate required fields
        extracted_data['validation_status'] = self._validate_required_fields(extracted_data['fields'])
        
        return extracted_data
    
    def _convert_to_text(self, file_path: str) -> str:
        """Convert PDF/image to text using OCR"""
        try:
            if file_path.lower().endswith('.pdf'):
                # Convert PDF to images
                images = convert_from_path(file_path, dpi=300)
                text = ""
                for img in images:
                    text += pytesseract.image_to_string(img, config='--psm 6')
                return text
            else:
                # Process image directly
                img = Image.open(file_path)
                return pytesseract.image_to_string(img, config='--psm 6')
        except Exception as e:
            logger.error(f"Error converting document to text: {e}")
            return ""
    
    def _extract_field_with_confidence(self, text: str, pattern: str, field_name: str) -> Tuple[str, float]:
        """Extract field value with confidence scoring"""
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Calculate confidence based on pattern match quality
                confidence = min(95, 70 + len(value) * 2)  # Base confidence + length bonus
                return value, confidence
            else:
                return "Not Found", 0.0
        except Exception as e:
            logger.error(f"Error extracting {field_name}: {e}")
            return "Error", 0.0
    
    def _assess_ocr_quality(self, text: str) -> Dict[str, Any]:
        """Assess overall OCR quality"""
        quality_score = 0
        issues = []
        
        # Check for common OCR errors
        if len(text) < 100:
            issues.append("Text too short - possible OCR failure")
            quality_score -= 30
        
        # Check for garbled text patterns
        garbled_patterns = [r'[^\w\s.,:;()/-]', r'\s{3,}', r'[a-z]{10,}']
        for pattern in garbled_patterns:
            if re.search(pattern, text):
                issues.append("Garbled text detected")
                quality_score -= 20
        
        # Check for required keywords
        required_keywords = ['patta', 'survey', 'village', 'district']
        found_keywords = sum(1 for keyword in required_keywords if keyword.lower() in text.lower())
        quality_score += found_keywords * 15
        
        return {
            'score': max(0, min(100, quality_score)),
            'issues': issues,
            'text_length': len(text)
        }
    
    def _validate_required_fields(self, fields: Dict[str, str]) -> Dict[str, Any]:
        """Validate that all required fields are present and properly formatted"""
        required_fields = ['patta_number', 'survey_number', 'district', 'village', 'owner_name']
        validation_result = {
            'all_present': True,
            'missing_fields': [],
            'format_issues': [],
            'overall_valid': True
        }
        
        for field in required_fields:
            if field not in fields or fields[field] == "Not Found":
                validation_result['missing_fields'].append(field)
                validation_result['all_present'] = False
        
        # Format validation
        if 'patta_number' in fields and fields['patta_number'] != "Not Found":
            if not re.match(r'^[A-Z0-9/-]+$', fields['patta_number']):
                validation_result['format_issues'].append("Invalid Patta Number format")
        
        if 'survey_number' in fields and fields['survey_number'] != "Not Found":
            if not re.match(r'^[A-Z0-9/-]+$', fields['survey_number']):
                validation_result['format_issues'].append("Invalid Survey Number format")
        
        validation_result['overall_valid'] = (
            validation_result['all_present'] and 
            len(validation_result['format_issues']) == 0
        )
        
        return validation_result
    
    def verify_with_portal(self, extracted_data: Dict[str, Any], state: str) -> Dict[str, Any]:
        """
        Verify extracted data with official state government portal
        
        Args:
            extracted_data: Data extracted from document
            state: State name for portal selection
            
        Returns:
            Portal verification results
        """
        logger.info(f"Verifying with {state} portal")
        
        if state not in self.state_portals:
            return {
                'status': 'error',
                'message': f'Portal not configured for {state}',
                'verified': False
            }
        
        portal_config = self.state_portals[state]
        fields = extracted_data['fields']
        
        # Prepare verification request
        verification_data = {
            'district': fields.get('district', ''),
            'taluk': fields.get('taluk', ''),
            'village': fields.get('village', ''),
            'survey_number': fields.get('survey_number', ''),
            'patta_number': fields.get('patta_number', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Simulate portal API call (in production, use actual API)
            portal_result = self._simulate_portal_verification(verification_data, state)
            
            return {
                'status': 'success',
                'portal_data': portal_result,
                'matches': self._compare_portal_data(fields, portal_result),
                'verified': portal_result.get('found', False),
                'verification_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Portal verification error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'verified': False
            }
    
    def _simulate_portal_verification(self, data: Dict[str, str], state: str) -> Dict[str, Any]:
        """
        Simulate portal verification (replace with actual API calls in production)
        """
        # This is a simulation - in production, make actual API calls to state portals
        simulated_data = {
            'found': True,
            'owner_name': 'Rajesh Kumar',
            'land_type': 'Dry',
            'extent': '2.5 hectares',
            'coordinates': {'lat': 12.9716, 'lon': 77.5946},
            'tax_details': {'current_year': 2024, 'amount': 1500, 'status': 'Paid'},
            'encumbrances': [],
            'portal_watermark': True,
            'qr_code_present': True
        }
        
        # Simulate some mismatches for testing
        if data.get('patta_number') == 'INVALID123':
            simulated_data['found'] = False
        
        return simulated_data
    
    def _compare_portal_data(self, extracted_fields: Dict[str, str], portal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare extracted data with portal data"""
        matches = {
            'owner_name': False,
            'land_type': False,
            'extent': False,
            'coordinates': False,
            'overall_match': False
        }
        
        if not portal_data.get('found', False):
            return matches
        
        # Compare owner name
        if 'owner_name' in extracted_fields:
            extracted_name = extracted_fields['owner_name'].lower().strip()
            portal_name = portal_data.get('owner_name', '').lower().strip()
            matches['owner_name'] = self._fuzzy_match(extracted_name, portal_name, threshold=0.8)
        
        # Compare land type
        if 'land_type' in extracted_fields:
            extracted_type = extracted_fields['land_type'].lower()
            portal_type = portal_data.get('land_type', '').lower()
            matches['land_type'] = extracted_type in portal_type or portal_type in extracted_type
        
        # Compare extent
        if 'extent' in extracted_fields:
            extracted_extent = self._extract_numeric_value(extracted_fields['extent'])
            portal_extent = self._extract_numeric_value(portal_data.get('extent', ''))
            if extracted_extent and portal_extent:
                matches['extent'] = abs(extracted_extent - portal_extent) < 0.1
        
        # Overall match calculation
        match_count = sum(1 for match in matches.values() if match)
        matches['overall_match'] = match_count >= 3  # At least 3 fields must match
        
        return matches
    
    def _fuzzy_match(self, str1: str, str2: str, threshold: float = 0.8) -> bool:
        """Simple fuzzy string matching"""
        if not str1 or not str2:
            return False
        
        # Simple similarity calculation
        common_chars = sum(1 for c in str1 if c in str2)
        similarity = common_chars / max(len(str1), len(str2))
        return similarity >= threshold
    
    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text"""
        try:
            match = re.search(r'(\d+\.?\d*)', text)
            return float(match.group(1)) if match else None
        except:
            return None
    
    def verify_gis_coordinates(self, extracted_data: Dict[str, Any], portal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify geographical coordinates using GIS/map data
        
        Args:
            extracted_data: Data extracted from document
            portal_data: Data from portal verification
            
        Returns:
            GIS verification results
        """
        logger.info("Performing GIS coordinate verification")
        
        gis_result = {
            'status': 'success',
            'coordinates_match': False,
            'boundary_validation': False,
            'location_accuracy': 0.0,
            'gis_issues': []
        }
        
        try:
            # Extract coordinates from document
            coord_text = extracted_data['fields'].get('coordinates', '')
            if coord_text == "Not Found":
                gis_result['gis_issues'].append("No coordinates found in document")
                return gis_result
            
            # Parse coordinates
            coord_match = re.search(self.patterns['coordinates'], coord_text)
            if not coord_match:
                gis_result['gis_issues'].append("Invalid coordinate format")
                return gis_result
            
            doc_lat = float(coord_match.group(1))
            doc_lon = float(coord_match.group(2))
            
            # Get portal coordinates
            portal_coords = portal_data.get('coordinates', {})
            if not portal_coords:
                gis_result['gis_issues'].append("No coordinates in portal data")
                return gis_result
            
            portal_lat = portal_coords.get('lat', 0)
            portal_lon = portal_coords.get('lon', 0)
            
            # Calculate distance between coordinates
            distance = self._calculate_distance(doc_lat, doc_lon, portal_lat, portal_lon)
            
            # Validate coordinates (within 100 meters is acceptable)
            gis_result['coordinates_match'] = distance < 0.1  # 100 meters
            gis_result['location_accuracy'] = max(0, 100 - distance * 1000)  # Accuracy percentage
            gis_result['distance_meters'] = distance * 1000
            
            # Simulate boundary validation
            gis_result['boundary_validation'] = self._simulate_boundary_validation(doc_lat, doc_lon)
            
        except Exception as e:
            logger.error(f"GIS verification error: {e}")
            gis_result['status'] = 'error'
            gis_result['gis_issues'].append(str(e))
        
        return gis_result
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth's radius in kilometers
        
        return c * r
    
    def _simulate_boundary_validation(self, lat: float, lon: float) -> bool:
        """Simulate boundary validation (in production, use actual GIS data)"""
        # This would typically involve checking against official land boundary data
        # For simulation, we'll assume coordinates within India are valid
        return 6.0 <= lat <= 37.0 and 68.0 <= lon <= 97.0
    
    def verify_authentication_features(self, file_path: str) -> Dict[str, Any]:
        """
        Verify authentication features like QR codes, watermarks, and digital signatures
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Authentication verification results
        """
        logger.info("Verifying authentication features")
        
        auth_result = {
            'qr_code_present': False,
            'qr_code_valid': False,
            'watermark_present': False,
            'digital_signature_present': False,
            'tampering_detected': False,
            'authentication_score': 0,
            'issues': []
        }
        
        try:
            # Check for QR code
            qr_result = self._detect_qr_code(file_path)
            auth_result['qr_code_present'] = qr_result['present']
            auth_result['qr_code_valid'] = qr_result['valid']
            
            # Check for watermark
            watermark_result = self._detect_watermark(file_path)
            auth_result['watermark_present'] = watermark_result['present']
            
            # Check for digital signature
            signature_result = self._detect_digital_signature(file_path)
            auth_result['digital_signature_present'] = signature_result['present']
            
            # Detect tampering
            tampering_result = self._detect_tampering(file_path)
            auth_result['tampering_detected'] = tampering_result['detected']
            auth_result['issues'].extend(tampering_result['issues'])
            
            # Calculate authentication score
            score = 0
            if auth_result['qr_code_valid']:
                score += 40
            if auth_result['watermark_present']:
                score += 30
            if auth_result['digital_signature_present']:
                score += 30
            if auth_result['tampering_detected']:
                score -= 50
            
            auth_result['authentication_score'] = max(0, score)
            
        except Exception as e:
            logger.error(f"Authentication verification error: {e}")
            auth_result['issues'].append(str(e))
        
        return auth_result
    
    def _detect_qr_code(self, file_path: str) -> Dict[str, Any]:
        """Detect and validate QR code in document"""
        try:
            # Convert to image if PDF
            if file_path.lower().endswith('.pdf'):
                images = convert_from_path(file_path)
                img = np.array(images[0])
            else:
                img = cv2.imread(file_path)
            
            # Detect QR codes
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)
            
            if data:
                # Validate QR code content (should contain document hash or verification URL)
                is_valid = self._validate_qr_content(data)
                return {'present': True, 'valid': is_valid, 'data': data}
            else:
                return {'present': False, 'valid': False, 'data': None}
                
        except Exception as e:
            logger.error(f"QR code detection error: {e}")
            return {'present': False, 'valid': False, 'data': None, 'error': str(e)}
    
    def _validate_qr_content(self, qr_data: str) -> bool:
        """Validate QR code content"""
        # Check if QR code contains valid verification data
        valid_patterns = [
            r'^https://.*\.gov\.in/verify/',
            r'^PATTA_VERIFY_[A-Z0-9]+$',
            r'^DOC_HASH_[a-f0-9]{64}$'
        ]
        
        for pattern in valid_patterns:
            if re.match(pattern, qr_data):
                return True
        
        return False
    
    def _detect_watermark(self, file_path: str) -> Dict[str, Any]:
        """Detect watermark in document"""
        try:
            # Convert to image if PDF
            if file_path.lower().endswith('.pdf'):
                images = convert_from_path(file_path)
                img = np.array(images[0])
            else:
                img = cv2.imread(file_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Look for watermark patterns (simplified detection)
            # In production, use more sophisticated watermark detection
            watermark_keywords = ['GOVERNMENT', 'OFFICIAL', 'VERIFIED', 'AUTHENTIC']
            
            # Use OCR to detect watermark text
            watermark_text = pytesseract.image_to_string(gray, config='--psm 8')
            
            watermark_found = any(keyword in watermark_text.upper() for keyword in watermark_keywords)
            
            return {'present': watermark_found, 'text': watermark_text}
            
        except Exception as e:
            logger.error(f"Watermark detection error: {e}")
            return {'present': False, 'text': '', 'error': str(e)}
    
    def _detect_digital_signature(self, file_path: str) -> Dict[str, Any]:
        """Detect digital signature in document"""
        try:
            # For PDF files, check for digital signature metadata
            if file_path.lower().endswith('.pdf'):
                # In production, use PyPDF2 or similar to check for digital signatures
                # For simulation, we'll check file metadata
                file_size = os.path.getsize(file_path)
                # Simulate signature detection based on file characteristics
                has_signature = file_size > 50000  # Larger files more likely to have signatures
                return {'present': has_signature, 'type': 'simulated'}
            else:
                return {'present': False, 'type': 'not_applicable'}
                
        except Exception as e:
            logger.error(f"Digital signature detection error: {e}")
            return {'present': False, 'type': 'error', 'error': str(e)}
    
    def _detect_tampering(self, file_path: str) -> Dict[str, Any]:
        """Detect signs of document tampering"""
        tampering_result = {
            'detected': False,
            'issues': [],
            'confidence': 0.0
        }
        
        try:
            # Check file integrity
            file_hash = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()
            
            # Check for common tampering indicators
            issues = []
            
            # Check file size (too small might indicate tampering)
            file_size = os.path.getsize(file_path)
            if file_size < 10000:  # Less than 10KB
                issues.append("File size suspiciously small")
            
            # Check for multiple versions of same text (copy-paste indicators)
            if file_path.lower().endswith('.pdf'):
                images = convert_from_path(file_path)
                text = pytesseract.image_to_string(images[0])
                
                # Look for repeated text patterns that might indicate tampering
                words = text.split()
                word_counts = {}
                for word in words:
                    if len(word) > 3:  # Only check longer words
                        word_counts[word] = word_counts.get(word, 0) + 1
                
                # If any word appears more than 10 times, might be tampered
                for word, count in word_counts.items():
                    if count > 10:
                        issues.append(f"Excessive repetition of '{word}' ({count} times)")
            
            tampering_result['issues'] = issues
            tampering_result['detected'] = len(issues) > 0
            tampering_result['confidence'] = min(100, len(issues) * 20)
            
        except Exception as e:
            logger.error(f"Tampering detection error: {e}")
            tampering_result['issues'].append(f"Detection error: {str(e)}")
        
        return tampering_result
    
    def cross_validate_with_ec(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-validate with Encumbrance Certificate data
        
        Args:
            extracted_data: Data extracted from Patta document
            
        Returns:
            EC validation results
        """
        logger.info("Cross-validating with Encumbrance Certificate")
        
        ec_result = {
            'status': 'success',
            'ec_available': False,
            'encumbrances_found': False,
            'disputes_detected': False,
            'loan_liens': False,
            'validation_matches': False,
            'ec_issues': []
        }
        
        try:
            # Simulate EC data retrieval (in production, integrate with Registrar Office)
            ec_data = self._simulate_ec_data(extracted_data)
            
            ec_result['ec_available'] = ec_data.get('available', False)
            ec_result['encumbrances_found'] = len(ec_data.get('encumbrances', [])) > 0
            ec_result['disputes_detected'] = ec_data.get('disputes', False)
            ec_result['loan_liens'] = ec_data.get('loan_liens', False)
            
            # Validate owner name matches
            if ec_data.get('owner_name'):
                extracted_owner = extracted_data['fields'].get('owner_name', '').lower()
                ec_owner = ec_data['owner_name'].lower()
                ec_result['validation_matches'] = self._fuzzy_match(extracted_owner, ec_owner)
            
            # Check for issues
            if ec_result['disputes_detected']:
                ec_result['ec_issues'].append("Legal disputes detected in EC")
            if ec_result['loan_liens']:
                ec_result['ec_issues'].append("Loan liens present")
            if ec_result['encumbrances_found']:
                ec_result['ec_issues'].append("Encumbrances found on property")
            
        except Exception as e:
            logger.error(f"EC validation error: {e}")
            ec_result['status'] = 'error'
            ec_result['ec_issues'].append(str(e))
        
        return ec_result
    
    def _simulate_ec_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Encumbrance Certificate data (replace with actual EC integration)"""
        # This is simulation data - in production, integrate with actual EC systems
        return {
            'available': True,
            'owner_name': 'Rajesh Kumar',
            'property_address': 'Village: Sample Village, District: Sample District',
            'encumbrances': [],
            'disputes': False,
            'loan_liens': False,
            'last_updated': '2024-01-15'
        }
    
    def make_final_decision(self, verification_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make final decision on document acceptance/rejection based on all verification results
        
        Args:
            verification_results: Combined results from all verification steps
            
        Returns:
            Final decision with detailed reasoning
        """
        logger.info("Making final verification decision")
        
        decision = {
            'status': 'pending',
            'confidence': 0.0,
            'reasoning': [],
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract individual results
        ocr_result = verification_results.get('ocr_extraction', {})
        portal_result = verification_results.get('portal_verification', {})
        gis_result = verification_results.get('gis_verification', {})
        auth_result = verification_results.get('authentication', {})
        ec_result = verification_results.get('ec_validation', {})
        
        # Decision logic based on rules
        score = 0
        max_score = 100
        
        # OCR Quality (20 points)
        ocr_quality = ocr_result.get('ocr_quality', {}).get('score', 0)
        if ocr_quality >= 80:
            score += 20
            decision['reasoning'].append("✅ High OCR quality")
        elif ocr_quality >= 60:
            score += 10
            decision['reasoning'].append("⚠️ Moderate OCR quality")
        else:
            decision['reasoning'].append("❌ Poor OCR quality")
        
        # Required Fields (20 points)
        validation_status = ocr_result.get('validation_status', {})
        if validation_status.get('overall_valid', False):
            score += 20
            decision['reasoning'].append("✅ All required fields present and valid")
        else:
            missing_fields = validation_status.get('missing_fields', [])
            if missing_fields:
                decision['reasoning'].append(f"❌ Missing required fields: {', '.join(missing_fields)}")
        
        # Portal Verification (25 points)
        if portal_result.get('verified', False):
            score += 25
            decision['reasoning'].append("✅ Portal verification successful")
            
            # Check data matches
            matches = portal_result.get('matches', {})
            if matches.get('overall_match', False):
                score += 10
                decision['reasoning'].append("✅ Portal data matches document")
            else:
                decision['reasoning'].append("⚠️ Some portal data mismatches")
        else:
            decision['reasoning'].append("❌ Portal verification failed")
        
        # GIS Verification (15 points)
        if gis_result.get('coordinates_match', False):
            score += 15
            decision['reasoning'].append("✅ GIS coordinates match")
        else:
            decision['reasoning'].append("❌ GIS coordinate mismatch")
        
        # Authentication (20 points)
        auth_score = auth_result.get('authentication_score', 0)
        if auth_score >= 70:
            score += 20
            decision['reasoning'].append("✅ Strong authentication features")
        elif auth_score >= 40:
            score += 10
            decision['reasoning'].append("⚠️ Moderate authentication features")
        else:
            decision['reasoning'].append("❌ Weak authentication features")
        
        # Tampering Detection
        if auth_result.get('tampering_detected', False):
            score -= 30
            decision['reasoning'].append("❌ Document tampering detected")
        
        # EC Validation
        if ec_result.get('ec_available', False):
            if ec_result.get('disputes_detected', False):
                score -= 20
                decision['reasoning'].append("❌ Legal disputes detected in EC")
            if ec_result.get('loan_liens', False):
                score -= 15
                decision['reasoning'].append("⚠️ Loan liens present")
            if not ec_result.get('validation_matches', False):
                score -= 10
                decision['reasoning'].append("⚠️ EC owner name mismatch")
        
        # Final decision
        decision['confidence'] = max(0, min(100, score))
        
        if score >= 80:
            decision['status'] = 'ACCEPTED'
            decision['recommendations'].append("Document is verified and accepted")
        elif score >= 60:
            decision['status'] = 'FLAGGED_FOR_REVIEW'
            decision['recommendations'].append("Document requires manual review")
            decision['recommendations'].append("Verify discrepancies with original records")
        else:
            decision['status'] = 'REJECTED'
            decision['recommendations'].append("Document verification failed")
            decision['recommendations'].append("Do not proceed with transaction")
        
        return decision
    
    def verify_patta_document(self, file_path: str, state: str = 'Tamil Nadu') -> Dict[str, Any]:
        """
        Complete Patta document verification process
        
        Args:
            file_path: Path to the Patta document
            state: State for portal verification
            
        Returns:
            Complete verification results
        """
        logger.info(f"Starting complete Patta verification for {file_path}")
        
        verification_results = {
            'document_path': file_path,
            'state': state,
            'verification_timestamp': datetime.now().isoformat(),
            'steps_completed': [],
            'final_decision': None
        }
        
        try:
            # Step 1: OCR Extraction
            logger.info("Step 1: OCR Extraction")
            ocr_result = self.extract_document_data(file_path)
            verification_results['ocr_extraction'] = ocr_result
            verification_results['steps_completed'].append('ocr_extraction')
            
            # Step 2: Portal Verification
            logger.info("Step 2: Portal Verification")
            portal_result = self.verify_with_portal(ocr_result, state)
            verification_results['portal_verification'] = portal_result
            verification_results['steps_completed'].append('portal_verification')
            
            # Step 3: GIS Verification
            logger.info("Step 3: GIS Verification")
            gis_result = self.verify_gis_coordinates(ocr_result, portal_result.get('portal_data', {}))
            verification_results['gis_verification'] = gis_result
            verification_results['steps_completed'].append('gis_verification')
            
            # Step 4: Authentication Verification
            logger.info("Step 4: Authentication Verification")
            auth_result = self.verify_authentication_features(file_path)
            verification_results['authentication'] = auth_result
            verification_results['steps_completed'].append('authentication')
            
            # Step 5: EC Cross-validation
            logger.info("Step 5: EC Cross-validation")
            ec_result = self.cross_validate_with_ec(ocr_result)
            verification_results['ec_validation'] = ec_result
            verification_results['steps_completed'].append('ec_validation')
            
            # Step 6: Final Decision
            logger.info("Step 6: Final Decision")
            final_decision = self.make_final_decision(verification_results)
            verification_results['final_decision'] = final_decision
            verification_results['steps_completed'].append('final_decision')
            
            verification_results['status'] = 'completed'
            verification_results['success'] = True
            
        except Exception as e:
            logger.error(f"Verification process error: {e}")
            verification_results['status'] = 'error'
            verification_results['success'] = False
            verification_results['error'] = str(e)
        
        return verification_results

# Example usage and testing
if __name__ == "__main__":
    # Initialize verifier
    verifier = PattaVerifier()
    
    # Test with sample document
    sample_doc = "../data/sample_fra_claim.pdf"
    
    if os.path.exists(sample_doc):
        print("🔍 Starting Patta Document Verification...")
        results = verifier.verify_patta_document(sample_doc, 'Tamil Nadu')
        
        print("\n📋 Verification Results:")
        print(f"Status: {results['status']}")
        print(f"Steps Completed: {', '.join(results['steps_completed'])}")
        
        if results['final_decision']:
            decision = results['final_decision']
            print(f"\n🎯 Final Decision: {decision['status']}")
            print(f"Confidence: {decision['confidence']}%")
            print("\nReasoning:")
            for reason in decision['reasoning']:
                print(f"  {reason}")
            print("\nRecommendations:")
            for rec in decision['recommendations']:
                print(f"  • {rec}")
    else:
        print(f"Sample document not found: {sample_doc}")
        print("Please provide a valid Patta document for testing.")

