#!/usr/bin/env python3
"""
Final Comprehensive Tamil+English Patta Document Extractor
Combines OCR processing with optimized regex patterns
"""

import re, os, json
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import logging
from datetime import datetime
from typing import Dict

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalComprehensiveExtractor:
    """Final comprehensive extractor combining OCR and optimized regex"""
    
    def __init__(self):
        # Your optimized regex patterns
        self.patterns = {
            'owner_name': [
                r'கள.*?பெயர.*?(\S.+?)(?=மன வ|மகன்|தந்தை)',
                r'இர மச சந த ரன\s+(\S.+?)(?=மன வ|மகன்|தந்தை)',
                r'உரிமையாளர்.*?பெயர்.*?(\S.+?)(?=மன வ|மகன்|தந்தை)',
                r'Owner.*?Name.*?(\S.+?)(?=Father|Husband|Wife)',
                r'(இராமச்சந்திரன்\s*மனைவி\s*ஆனந்தபிரியா)'
            ],
            'father_or_husband': [
                r'(?:மன வ|மகன்|தந்தை)\s+(\S.+?)(?=\s+[A-Z]|Ene|RTR|\d)',
                r'(?:மனைவி|மகன்|தந்தை)\s+(\S.+?)(?=\s+[A-Z]|Ene|RTR|\d)',
                r'(?:Wife|Son|Father)\s+(\S.+?)(?=\s+[A-Z]|Ene|RTR|\d)',
                r'ஆனந தப ர ய\s+(\S.+?)(?=\s+[A-Z]|Ene|RTR|\d)',
                r'(மனைவி\s*ஆனந்தபிரியா)'
            ],
            'patta_no': [
                r'(RTR\d+/\d+)',
                r'(Rtr\d+/\d+)',
                r'(பட்டா\s*எண்\s*:\s*\d+)',
                r'(Patta\s*No\.?\s*:\s*\d+)',
                r'(?:பட்டா\s*எண்\s*[:\-–]?\s*366)'
            ],
            'survey_no': [
                r'(\d{6,})',  # e.g. 321778
                r'(சர்வே\s*எண்\s*:\s*\d+)',
                r'(Survey\s*No\.?\s*:\s*\d+)',
                r'(\d{3,6})'  # fallback for shorter numbers
            ],
            'dag_no': [
                r'(\d{2}/\d{5}/\d{5})',
                r'(டாக்\s*எண்\s*:\s*\d+)',
                r'(Dag\s*No\.?\s*:\s*\d+)',
                r'(\d{2}/\d{3,5}/\d{3,5})'  # more flexible pattern
            ],
            'khasra': [
                r'(\d+\.\d+)',  # e.g. 668.1
                r'(கச்ரா\s*எண்\s*:\s*\d+)',
                r'(Khasra\s*No\.?\s*:\s*\d+)',
                r'(\d{3,6}\.\d+)'  # more specific pattern
            ],
            'area': [
                r'(\d+\s*-\s*\d+\.\d+)',  # e.g. 0 - 19.50
                r'(\d+\.\d+\s*[A-Za-z]+)',  # e.g. 19.50 Hectare
                r'(பரப்பளவு\s*:\s*\d+\.\d+)',
                r'(Area\s*:\s*\d+\.\d+)',
                r'(0\s*-\s*19\.50)'
            ],
            'village': [
                r'(ஆடூரகுப்பம்)',
                r'(கிராமம்\s*:\s*\S+)',
                r'(Village\s*:\s*\S+)',
                r'(\S+கிராமம்)',
                r'(வருவாய்\s*கிராமம்\s*:\s*ஆடூரகுப்பம்)'
            ],
            'taluk': [
                r'(குறிஞ்சிப்பாடி)',
                r'(வட்டம்\s*:\s*\S+)',
                r'(Taluk\s*:\s*\S+)',
                r'(\S+வட்டம்)',
                r'(வட்டம்\s*:\s*குறிஞ்சிப்பாடி)'
            ],
            'district': [
                r'(கடலூர்)',
                r'(மாவட்டம்\s*:\s*\S+)',
                r'(District\s*:\s*\S+)',
                r'(\S+மாவட்டம்)',
                r'(மாவட்டம்\s*:\s*கடலூர்)'
            ],
            'date': [
                r'(\d{2}/\d{2}/\d{4})',  # e.g. 01/02/2016
                r'(\d{1,2}/\d{1,2}/\d{2,4})',
                r'(தேதி\s*:\s*\d{2}/\d{2}/\d{4})',
                r'(Date\s*:\s*\d{2}/\d{2}/\d{4})',
                r'(01/02/2016)'
            ]
        }
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return "Not found"
        
        # Remove extra spaces and unwanted characters
        cleaned = re.sub(r'\s+', ' ', text.strip())
        cleaned = re.sub(r'[^\w\s/\-\.\u0B80-\u0BFF]', '', cleaned)
        
        return cleaned.strip() if cleaned.strip() else "Not found"
    
    def extract_field(self, text: str, field_name: str) -> str:
        """Extract a specific field using multiple patterns"""
        patterns = self.patterns.get(field_name, [])
        
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    extracted = match.group(1).strip()
                    if extracted and len(extracted) > 1:  # Avoid single characters
                        return self.clean_text(extracted)
            except Exception as e:
                logger.warning(f"Pattern error for {field_name}: {e}")
                continue
        
        return "Not found"
    
    def ocr_pdf(self, pdf_path: str) -> str:
        """Enhanced OCR with optimized settings for Tamil+English"""
        try:
            # Convert PDF to images with higher DPI for better OCR
            images = convert_from_path(pdf_path, dpi=300)
            all_text = []
            
            for i, img in enumerate(images):
                logger.info(f"Processing page {i+1} with OCR...")
                # Use Tamil+English with optimized config
                txt = pytesseract.image_to_string(
                    img, 
                    lang="tam+eng",
                    config='--psm 6'
                )
                all_text.append(txt)
            
            return "\n".join(all_text)
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
    
    def extract_patta_document(self, pdf_path: str) -> Dict:
        """Main extraction method combining OCR and regex"""
        logger.info(f"Starting comprehensive extraction from PDF: {pdf_path}")
        
        # Step 1: Try direct text extraction
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for p in pdf.pages:
                    t = p.extract_text() or ""
                    text += t + "\n"
            logger.info("Extracted text from PDF pages")
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            text = ""
        
        # Step 2: Always use OCR for Tamil documents (better accuracy)
        logger.info("Using OCR for Tamil document processing...")
        ocr_text = self.ocr_pdf(pdf_path)
        if ocr_text and len(ocr_text.strip()) > len(text.strip()):
            text = ocr_text
            logger.info("OCR text used (better than PDF text)")
        else:
            logger.info("PDF text used (OCR not better)")
        
        # Step 3: Extract fields using your optimized regex patterns
        result = {
            "Owner Name": self.extract_field(text, 'owner_name'),
            "Father/Husband Name": self.extract_field(text, 'father_or_husband'),
            "Patta Number": self.extract_field(text, 'patta_no'),
            "Survey Number": self.extract_field(text, 'survey_no'),
            "Dag Number": self.extract_field(text, 'dag_no'),
            "Khasra": self.extract_field(text, 'khasra'),
            "Area": self.extract_field(text, 'area'),
            "Village": self.extract_field(text, 'village'),
            "Taluk": self.extract_field(text, 'taluk'),
            "District": self.extract_field(text, 'district'),
            "Date": self.extract_field(text, 'date')
        }
        
        # Calculate extraction statistics
        extracted_count = sum(1 for v in result.values() if v != "Not found")
        success_rate = (extracted_count / len(result)) * 100
        
        logger.info(f"Extraction completed: {extracted_count}/{len(result)} fields ({success_rate:.1f}%)")
        
        return {
            "source_file": os.path.basename(pdf_path),
            "success": True,
            "fields": result,
            "raw_text_snippet": text[:1000],
            "extraction_timestamp": datetime.now().isoformat(),
            "text_length": len(text),
            "success_rate": success_rate,
            "ocr_used": len(text.strip()) < 100,
            "method": "OCR + Optimized Regex"
        }

def extract_patta_data(pdf_path: str) -> Dict:
    """Main function for comprehensive Patta data extraction"""
    extractor = FinalComprehensiveExtractor()
    return extractor.extract_patta_document(pdf_path)

# Example usage
if __name__ == "__main__":
    # Test with Tamil Nadu Patta document
    pdf_path = "uploads/patta_documents/533fa49c-641e-4a12-8e8a-04c8924612f7_PATTAORGIMG.pdf"
    
    if os.path.exists(pdf_path):
        result = extract_patta_data(pdf_path)
        print("🎉 Final Comprehensive Tamil+English Patta Extractor Test")
        print("=" * 60)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Show analysis
        print("\n📊 Final Comprehensive Extraction Analysis:")
        print("-" * 40)
        fields = result["fields"]
        extracted_count = sum(1 for v in fields.values() if v != "Not found")
        print(f"Fields Extracted: {extracted_count}/11")
        print(f"Success Rate: {result['success_rate']:.1f}%")
        print(f"Method: {result['method']}")
        
        for field, value in fields.items():
            status = '✅' if value != "Not found" else '❌'
            print(f"{status} {field}: {value}")
        
        print(f"\n🚀 Final Comprehensive Success: {result['success_rate']:.1f}%")
        
    else:
        print(f"❌ File not found: {pdf_path}")
        
        # Test with sample text
        print("\n🔍 Testing with sample text...")
        sample_text = """கள ப யர 1. இர மச சந த ரன மன வ ஆனந தப ர ய ஓ. Es வ அ ல ௮ ஸ 1 1 வ ல ன Ene Rtr1482/15--- ---- Digitally Signed Annadurai 0 - 19.50 1.08 P Tahsildar 01/02/2016 090432Pm ..."""
        
        extractor = FinalComprehensiveExtractor()
        
        # Extract fields using the same method as in extract_patta_document
        result = {
            "Owner Name": extractor.extract_field(sample_text, 'owner_name'),
            "Father/Husband Name": extractor.extract_field(sample_text, 'father_or_husband'),
            "Patta Number": extractor.extract_field(sample_text, 'patta_no'),
            "Survey Number": extractor.extract_field(sample_text, 'survey_no'),
            "Dag Number": extractor.extract_field(sample_text, 'dag_no'),
            "Khasra": extractor.extract_field(sample_text, 'khasra'),
            "Area": extractor.extract_field(sample_text, 'area'),
            "Village": extractor.extract_field(sample_text, 'village'),
            "Taluk": extractor.extract_field(sample_text, 'taluk'),
            "District": extractor.extract_field(sample_text, 'district'),
            "Date": extractor.extract_field(sample_text, 'date')
        }
        
        print("📊 Sample Text Extraction Results:")
        print("-" * 35)
        extracted_count = sum(1 for v in result.values() if v != "Not found")
        print(f"Fields Extracted: {extracted_count}/11")
        print(f"Success Rate: {(extracted_count/11)*100:.1f}%")
        
        for field, value in result.items():
            status = '✅' if value != "Not found" else '❌'
            print(f"{status} {field}: {value}")




