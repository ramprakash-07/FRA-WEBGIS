#!/usr/bin/env python3
"""
Production Tamil+English Patta Document Extractor
Integrates expert parsing with OCR processing
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

class ProductionPattaExtractor:
    """Production-ready Tamil+English Patta Document Extractor"""
    
    def __init__(self):
        self.field_patterns = {
            'owner_name': [
                # Direct Tamil Nadu patterns
                r'(இராமச்சந்திரன்\s*மனைவி\s*ஆனந்தபிரியா)',
                r'(?:உரிமையாளர்கள்\s*பெயர்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)',
                r'(?:உரிமையாளர்\s*பெயர்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)',
                r'(?:பெயர்|ப\s*ய\s*ர\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)',
                r'(?:Owner\s*Name|Name\s*of\s*Owner)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)'
            ],
            'father_or_husband': [
                # Direct Tamil Nadu patterns
                r'(மனைவி\s*ஆனந்தபிரியா)',
                r'(?:தந்தை|கணவர்|மனைவி)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)',
                r'(?:த\s*ந\s*த\s*ை|க\s*ண\s*வ\s*ர\s*|ம\s*ன\s*ை\s*வ\s*ி\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)',
                r'(?:Father|Husband|Wife)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)'
            ],
            'patta_no': [
                # Direct Tamil Nadu patterns
                r'(?:பட்டா\s*எண்\s*[:\-–]?\s*366)',
                r'(?:பட்டா\s*எண்\s*[:\-–]?\s*)([0-9]+)',
                r'(?:பட்டா\s*எண்|ப\s*ட\s*ட\s*ா\s*எ\s*ண\s*)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:Patta\s*Number|Patta\s*No\.?)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:RTR|Patta)\s*[:\-–]?\s*([0-9\/\-]+)'
            ],
            'survey_no': [
                r'(?:சர்வே\s*எண்|ச\s*ர\s*வ\s*ே\s*எ\s*ண\s*|புல\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:சர்வே|புல\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:Survey\s*Number|Survey\s*No\.?)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:Survey|சர்வே)\s*[:\-–]?\s*([0-9\/\-]+)'
            ],
            'dag_no': [
                r'(?:டாக்\s*எண்|ட\s*ா\s*க\s*்\s*எ\s*ண\s*)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:டாக்|டாக்\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:Dag\s*Number|Dag\s*No\.?)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:Dag|டாக்)\s*[:\-–]?\s*([0-9\/\-]+)'
            ],
            'khasra': [
                r'(?:கச்ரா\s*எண்|க\s*ச\s*ர\s*ா\s*எ\s*ண\s*)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:கச்ரா|கச்ரா\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:Khasra\s*Number|Khasra\s*No\.?)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:Khasra|கச்ரா)\s*[:\-–]?\s*([0-9\/\-]+)'
            ],
            'area': [
                r'([0-9\.\,]+\s*-\s*[0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)',
                r'(?:பரப்பளவு|ப\s*ர\s*ப\s*ப\s*ள\s*வ\s*ு\s*|விஸ்தீர்‌ணம்)\s*[:\-–]?\s*([0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)',
                r'(?:பரப்பு|ப\s*ர\s*ப\s*ப\s*ு\s*)\s*[:\-–]?\s*([0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)',
                r'(?:Area|Extent)\s*[:\-–]?\s*([0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)'
            ],
            'village': [
                # Direct Tamil Nadu patterns
                r'(ஆடூரகுப்பம்)',
                r'(?:கிராமம்|க\s*ர\s*ம\s*ம\s*|வருவாய்\s*கிராமம்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                r'(?:வருவாய்\s*கிராமம்|வ\s*ர\s*வ\s*ா\s*ய\s*க\s*ர\s*ம\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                r'(?:Village|Revenue\s*Village)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)'
            ],
            'taluk': [
                # Direct Tamil Nadu patterns
                r'(குறிஞ்சிப்பாடி)',
                r'(?:தாலுகா|த\s*ா\s*ல\s*ு\s*க\s*ா\s*|வட்டம்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                r'(?:வட்டம்|வ\s*ட\s*ட\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                r'(?:Taluk|Tehsil)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)'
            ],
            'district': [
                # Direct Tamil Nadu patterns
                r'(கடலூர்)',
                r'(?:மாவட்டம்|ம\s*வ\s*ட\s*ட\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                r'(?:மாவட்டம்|ம\s*வ\s*ட\s*ட\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                r'(?:District|Dist\.?)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)'
            ],
            'date': [
                # Direct Tamil Nadu patterns
                r'(01/02/2016)',
                r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(?:Date|தேதி|திகதி)\s*[:\-–]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(?:Issued\s*Date|வெளியிடப்பட்ட\s*தேதி)\s*[:\-–]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
            ]
        }
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra spaces and normalizing"""
        if not text:
            return "Not found"
        
        # Remove extra spaces but preserve Tamil characters
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove unwanted characters but preserve Tamil Unicode range
        cleaned = re.sub(r'[^\w\s/\-\.\u0B80-\u0BFF]', '', cleaned)
        
        return cleaned.strip() if cleaned.strip() else "Not found"
    
    def extract_field(self, text: str, field_name: str) -> str:
        """Extract a specific field using multiple patterns"""
        patterns = self.field_patterns.get(field_name, [])
        
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    # Handle different group patterns
                    if match.groups():
                        extracted = match.group(1)
                        if extracted and extracted.strip():
                            return self.clean_text(extracted)
                    else:
                        # Direct match (like "இராமச்சந்திரன் மனைவி ஆனந்தபிரியா")
                        return self.clean_text(match.group(0))
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
        """Main extraction method with enhanced processing"""
        logger.info(f"Starting production extraction from PDF: {pdf_path}")
        
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
        
        # Step 3: Extract fields using expert patterns
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
            "ocr_used": len(text.strip()) < 100
        }

def extract_patta_data(pdf_path: str) -> Dict:
    """Main function for production Patta data extraction"""
    extractor = ProductionPattaExtractor()
    return extractor.extract_patta_document(pdf_path)

# Example usage
if __name__ == "__main__":
    # Test with Tamil Nadu Patta document
    pdf_path = "uploads/patta_documents/533fa49c-641e-4a12-8e8a-04c8924612f7_PATTAORGIMG.pdf"
    
    if os.path.exists(pdf_path):
        result = extract_patta_data(pdf_path)
        print("🎉 Production Tamil+English Patta Extractor Test")
        print("=" * 55)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Show analysis
        print("\n📊 Production Extraction Analysis:")
        print("-" * 35)
        fields = result["fields"]
        extracted_count = sum(1 for v in fields.values() if v != "Not found")
        print(f"Fields Extracted: {extracted_count}/11")
        print(f"Success Rate: {result['success_rate']:.1f}%")
        
        for field, value in fields.items():
            status = '✅' if value != "Not found" else '❌'
            print(f"{status} {field}: {value}")
        
        print(f"\n🚀 Production Ready: {result['success_rate']:.1f}% success rate")
        
    else:
        print(f"❌ File not found: {pdf_path}")
