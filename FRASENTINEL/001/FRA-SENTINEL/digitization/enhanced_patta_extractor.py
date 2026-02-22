"""
Enhanced Tamil+English Patta Document Extraction System
Based on improved regex patterns and OCR optimization
"""

import re
import os
import json
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import io

# Configure Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPattaExtractor:
    """Enhanced Patta Document Extractor with optimized Tamil+English OCR"""
    
    def __init__(self):
        self.raw_text = ""
        self.confidence_scores = {}
        
    def clean_tamil_text(self, val: str) -> Optional[str]:
        """Clean Tamil text by removing extra spaces and normalizing"""
        if not val:
            return None
        # Remove extra spaces but preserve Tamil characters
        cleaned = re.sub(r"\s+", "", val.strip())
        return cleaned if cleaned else None
    
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
                    config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789அஆஇஈஉஊஎஏஐஒஓஔகஙசஜஞடணதநனபமயரலவழளறனஷஸஹ் '
                )
                all_text.append(txt)
            
            return "\n".join(all_text)
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
    
    def extract_fields(self, text: str) -> Dict[str, Optional[str]]:
        """Enhanced field extraction with improved regex patterns"""
        fields = {}
        
        # Owner / Name - Enhanced patterns
        patterns = [
            r"(?:கள\s*ப\s*யர|களப்பயர்|உரிமையாளர்|பெயர்|Name|Owner)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)",
            r"(?:உரிமையாளர்கள்\s*பெயர்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)",
            r"(?:ப\s*ய\s*ர\s*|உ\s*ர\s*ம\s*ய\s*ள\s*ர\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["owner_name"] = self.clean_tamil_text(m.group(1))
                break
        else:
            fields["owner_name"] = None
        
        # Father/Husband - Enhanced patterns
        patterns = [
            r"(?:தந்தை|கணவர்|Father|Husband|மனைவி)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)",
            r"(?:த\s*ந\s*த\s*ை|க\s*ண\s*வ\s*ர\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["father_or_husband"] = self.clean_tamil_text(m.group(1))
                break
        else:
            fields["father_or_husband"] = None
        
        # Patta Number - Enhanced patterns
        patterns = [
            r"(?:Patta|பட்டா|RTR)\s*[:\-–]?\s*([A-Za-z0-9\/\-]+)",
            r"(?:ப\s*ட\s*ட\s*ா\s*எ\s*ண\s*|ப\s*ட\s*ட\s*ா\s*)\s*[:\-–]?\s*([A-Za-z0-9\/\-]+)",
            r"பட்டா\s*எண்\s*:\s*([0-9]+)"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["patta_no"] = m.group(1).strip()
                break
        else:
            fields["patta_no"] = None
        
        # Survey Number - Enhanced patterns
        patterns = [
            r"(?:Survey|சர்வே|புல\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)",
            r"(?:ச\s*ர\s*வ\s*ே\s*எ\s*ண\s*|ச\s*ர\s*வ\s*ே\s*)\s*[:\-–]?\s*([0-9\/\-]+)",
            r"புல\s*எண்\s*:\s*([0-9]+)"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["survey_no"] = m.group(1).strip()
                break
        else:
            fields["survey_no"] = None
        
        # Dag Number - Enhanced patterns
        patterns = [
            r"(?:Dag|டாக்|டாக்\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)",
            r"(?:ட\s*ா\s*க\s*்\s*எ\s*ண\s*|ட\s*ா\s*க\s*்\s*)\s*[:\-–]?\s*([0-9\/\-]+)"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["dag_no"] = m.group(1).strip()
                break
        else:
            fields["dag_no"] = None
        
        # Khasra - Enhanced patterns
        patterns = [
            r"(?:Khasra|கச்ரா|கச்ரா\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)",
            r"(?:க\s*ச\s*ர\s*ா\s*எ\s*ண\s*|க\s*ச\s*ர\s*ா\s*)\s*[:\-–]?\s*([0-9\/\-]+)"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["khasra"] = m.group(1).strip()
                break
        else:
            fields["khasra"] = None
        
        # Area / Extent - Enhanced patterns
        patterns = [
            r"(?:Area|விஸ்தீர்‌ணம்|பரப்பு)\s*[:\-–]?\s*([0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)",
            r"(?:வ\s*ட\s*ட\s*ம\s*|வ\s*ட\s*ட\s*ம\s*)\s*[:\-–]?\s*([0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)",
            r"([0-9\.\,]+\s*-\s*[0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["area"] = m.group(1).strip()
                break
        else:
            fields["area"] = None
        
        # Village - Enhanced patterns
        patterns = [
            r"(?:Village|கிராமம்|வருவாய்\s*கிராமம்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)",
            r"(?:க\s*ர\s*ம\s*ம\s*|வ\s*ர\s*வ\s*ா\s*ய\s*க\s*ர\s*ம\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)",
            r"வருவாய்\s*கிராமம்\s*:\s*([A-Za-zஅ-ஹ\s]+)"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["village"] = self.clean_tamil_text(m.group(1))
                break
        else:
            fields["village"] = None
        
        # Taluk - Enhanced patterns
        patterns = [
            r"(?:Taluk|வட்டம்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)",
            r"(?:வ\s*ட\s*ட\s*ம\s*|வ\s*ட\s*ட\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)",
            r"வட்டம்\s*:\s*([A-Za-zஅ-ஹ\s]+)"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["taluk"] = self.clean_tamil_text(m.group(1))
                break
        else:
            fields["taluk"] = None
        
        # District - Enhanced patterns
        patterns = [
            r"(?:District|மாவட்டம்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)",
            r"(?:ம\s*வ\s*ட\s*ட\s*ம\s*|ம\s*வ\s*ட\s*ட\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)",
            r"மாவட்டம்\s*:\s*([A-Za-zஅ-ஹ\s]+)"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["district"] = self.clean_tamil_text(m.group(1))
                break
        else:
            fields["district"] = None
        
        # Date - Enhanced patterns
        patterns = [
            r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
            r"(?:Date|தேதி|திகதி)\s*[:\-–]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
            r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s*[:\-–]?\s*(?:AM|PM|am|pm)?"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                fields["date"] = m.group(1).strip()
                break
        else:
            fields["date"] = None
        
        return fields
    
    def extract_patta(self, pdf_path: str) -> Dict:
        """Main extraction method with enhanced processing"""
        logger.info(f"Starting enhanced extraction from PDF: {pdf_path}")
        
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
        
        # Step 3: Extract fields
        fields = self.extract_fields(text)
        
        # Step 4: Calculate confidence scores
        confidence_scores = {}
        for field, value in fields.items():
            if value:
                # Simple confidence based on field completeness
                confidence_scores[field] = 0.8 if len(str(value)) > 3 else 0.6
            else:
                confidence_scores[field] = 0.0
        
        # Step 5: Prepare result
        result = {
            "source_file": os.path.basename(pdf_path),
            "success": True,
            "fields": fields,
            "raw_text_snippet": text[:1000],
            "confidence_scores": confidence_scores,
            "extraction_timestamp": datetime.now().isoformat(),
            "text_length": len(text),
            "ocr_used": len(text.strip()) < 100
        }
        
        logger.info("Enhanced extraction completed successfully")
        return result

def extract_patta_data(pdf_path: str) -> Dict:
    """Main function for enhanced Patta data extraction"""
    extractor = EnhancedPattaExtractor()
    return extractor.extract_patta(pdf_path)

# Example usage
if __name__ == "__main__":
    # Test with Tamil Nadu Patta document
    pdf_path = "uploads/patta_documents/533fa49c-641e-4a12-8e8a-04c8924612f7_PATTAORGIMG.pdf"
    
    if os.path.exists(pdf_path):
        result = extract_patta_data(pdf_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"File not found: {pdf_path}")




