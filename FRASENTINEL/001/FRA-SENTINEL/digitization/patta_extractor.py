"""
Patta Document Extraction System
Extracts structured data from uploaded Patta Document PDFs
"""

import os
import re
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

class PattaExtractor:
    """
    Main class for extracting structured data from Patta documents
    """
    
    def __init__(self):
        self.extracted_data = {}
        self.raw_text = ""
        self.confidence_scores = {}
        
        # Enhanced field patterns for Tamil+English Patta documents
        self.field_patterns = {
            'name': [
                # English patterns
                r'(?:name|owner|holder|patta holder)[\s:]*([^\n\r]+)',
                r'(?:name of|owner name|patta holder name)[\s:]*([^\n\r]+)',
                r'(?:Name|Owner|Holder|Patta Holder)[\s:]*([^\n\r]+)',
                # Tamil patterns (with OCR spacing tolerance)
                r'(?:ப\s*ய\s*ர\s*|உ\s*ர\s*ம\s*ய\s*ள\s*ர\s*|ப\s*ட\s*ட\s*ா\s*உ\s*ர\s*ம\s*ய\s*ள\s*ர\s*)[\s:]*([^\n\r]+)',
                r'(?:ப\s*ய\s*ர\s*|ப\s*ட\s*ட\s*ா\s*த\s*ர\s*ர\s*)[\s:]*([^\n\r]+)',
                # Tamil patterns (normal)
                r'(?:பெயர்|உரிமையாளர்|பட்டா\s*உரிமையாளர்)[\s:]*([^\n\r]+)',
                r'(?:பெயர்|பட்டா\s*தாரர்)[\s:]*([^\n\r]+)',
                # OCR tolerance patterns
                r'(?:Paita|Pata|Patta)[\s:]*([^\n\r]+)',
                r'(?:பைட்டா|பட்டா)[\s:]*([^\n\r]+)'
            ],
            'father_or_husband': [
                # English patterns
                r'(?:father|husband|father\'s name|husband\'s name)[\s:]*([^\n\r]+)',
                r'(?:father name|husband name)[\s:]*([^\n\r]+)',
                r'(?:Father|Husband|Father\'s Name|Husband\'s Name)[\s:]*([^\n\r]+)',
                # Tamil patterns
                r'(?:தந்தை|கணவர்|தந்தை பெயர்|கணவர் பெயர்)[\s:]*([^\n\r]+)',
                r'(?:தந்தை\s*பெயர்|கணவர்\s*பெயர்)[\s:]*([^\n\r]+)',
                # OCR tolerance patterns
                r'(?:Fathar|Fathor|Husbend)[\s:]*([^\n\r]+)',
                r'(?:தந்தை|கணவர்)[\s:]*([^\n\r]+)'
            ],
            'patta_no': [
                # English patterns
                r'(?:patta number|patta no|patta)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:Patta Number|Patta No|Patta)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                # Tamil patterns (with OCR spacing tolerance)
                r'(?:ப\s*ட\s*ட\s*ா\s*எ\s*ண\s*|ப\s*ட\s*ட\s*ா\s*)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:ப\s*ட\s*ட\s*ா\s*எ\s*ண\s*|ப\s*ட\s*ட\s*ா\s*ந\s*ம\s*ப\s*ர\s*)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                # Tamil patterns (normal)
                r'(?:பட்டா எண்|பட்டா\s*எண்|பட்டா)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:பட்டா\s*எண்|பட்டா\s*நம்பர்)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                # OCR tolerance patterns
                r'(?:Paita|Pata|Patta)\s*(?:Number|No|Num)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:பைட்டா|பட்டா)\s*(?:எண்|நம்பர்)[\s:]*([^\n\r\d]*\d+[^\n\r]*)'
            ],
            'survey_no': [
                # English patterns
                r'(?:survey number|survey no|survey)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:Survey Number|Survey No|Survey)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                # Tamil patterns
                r'(?:சர்வே எண்|சர்வே\s*எண்|சர்வே)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:சர்வே\s*எண்|சர்வே\s*நம்பர்)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                # OCR tolerance patterns
                r'(?:Survay|Survai|Survey)\s*(?:Number|No|Num)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:சர்வே|சர்வை)\s*(?:எண்|நம்பர்)[\s:]*([^\n\r\d]*\d+[^\n\r]*)'
            ],
            'dag_no': [
                r'(?:dag number|dag no|dag)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:डाग नंबर|डाग संख्या|डाग)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:டாக் எண்|டாக்)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:డాగ్ నంబర్|డాగ్)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:ಡಾಗ್ ಸಂಖ್ಯೆ|ಡಾಗ್)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:ഡാഗ് നമ്പർ|ഡാഗ്)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:ডাগ নম্বর|ডাগ)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:ଡାଗ୍ ନମ୍ବର|ଡାଗ୍)[\s:]*([^\n\r\d]*\d+[^\n\r]*)'
            ],
            'khasra': [
                r'(?:khasra number|khasra no|khasra)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:खसरा नंबर|खसरा संख्या|खसरा)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:கஸ்ரா எண்|கஸ்ரா)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:ఖస్రా నంబర్|ఖస్రా)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:ಖಸ್ರಾ ಸಂಖ್ಯೆ|ಖಸ್ರಾ)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:ഖസ്രാ നമ്പർ|ഖസ്രാ)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:খসরা নম্বর|খসরা)[\s:]*([^\n\r\d]*\d+[^\n\r]*)',
                r'(?:ଖସ୍ରା ନମ୍ବର|ଖସ୍ରା)[\s:]*([^\n\r\d]*\d+[^\n\r]*)'
            ],
            'area': [
                r'(?:area|extent|land area)[\s:]*([^\n\r\d]*\d+[^\n\r]*(?:acres?|hectares?|sq\.?\s*ft|sq\.?\s*m|गज|एकड़|हेक्टेयर|ஏக்கர்|హెక్టార్|ಎಕರೆ|ഏക്കർ|একর|ଏକର))',
                r'(?:क्षेत्रफल|जमीन का क्षेत्रफल|क्षेत्र)[\s:]*([^\n\r\d]*\d+[^\n\r]*(?:गज|एकड़|हेक्टेयर|वर्ग फुट|वर्ग मीटर))',
                r'(?:பரப்பளவு|நில பரப்பளவு|பரப்பு)[\s:]*([^\n\r\d]*\d+[^\n\r]*(?:ஏக்கர்|ஹெக்டேர்|சதுர அடி|சதுர மீட்டர்))',
                r'(?:వైశాల్యం|భూమి వైశాల్యం|వైశాల్య)[\s:]*([^\n\r\d]*\d+[^\n\r]*(?:హెక్టార్|ఎకరం|చదరపు అడుగులు|చదరపు మీటర్లు))',
                r'(?:ವಿಸ್ತೀರ್ಣ|ಭೂಮಿ ವಿಸ್ತೀರ್ಣ|ವಿಸ್ತೀರ್ಣ)[\s:]*([^\n\r\d]*\d+[^\n\r]*(?:ಎಕರೆ|ಹೆಕ್ಟೇರ್|ಚದರ ಅಡಿ|ಚದರ ಮೀಟರ್))',
                r'(?:വിസ്തീർണ്ണം|ഭൂമി വിസ്തീർണ്ണം|വിസ്തീർണ്ണം)[\s:]*([^\n\r\d]*\d+[^\n\r]*(?:ഏക്കർ|ഹെക്ടർ|ചതുര അടി|ചതുര മീറ്റർ))',
                r'(?:ক্ষেত্রফল|জমির ক্ষেত্রফল|ক্ষেত্র)[\s:]*([^\n\r\d]*\d+[^\n\r]*(?:একর|হেক্টর|বর্গ ফুট|বর্গ মিটার))',
                r'(?:କ୍ଷେତ୍ରଫଳ|ଜମିର କ୍ଷେତ୍ରଫଳ|କ୍ଷେତ୍ର)[\s:]*([^\n\r\d]*\d+[^\n\r]*(?:ଏକର|ହେକ୍ଟର|ବର୍ଗ ଫୁଟ|ବର୍ଗ ମିଟର))'
            ],
            'village': [
                r'(?:village|gram|gaon)[\s:]*([^\n\r]+)',
                r'(?:गांव|ग्राम|विलेज)[\s:]*([^\n\r]+)',
                r'(?:கிராமம்|ஊர்|வில்லேஜ்)[\s:]*([^\n\r]+)',
                r'(?:గ్రామం|ఊరు|విలేజ్)[\s:]*([^\n\r]+)',
                r'(?:ಗ್ರಾಮ|ಊರು|ವಿಲೇಜ್)[\s:]*([^\n\r]+)',
                r'(?:ഗ്രാമം|ഊര്|വില്ലേജ്)[\s:]*([^\n\r]+)',
                r'(?:গ্রাম|উর|ভিলেজ)[\s:]*([^\n\r]+)',
                r'(?:ଗ୍ରାମ|ଊର|ଭିଲେଜ୍)[\s:]*([^\n\r]+)'
            ],
            'taluk': [
                r'(?:taluk|taluka|tehsil|mandal)[\s:]*([^\n\r]+)',
                r'(?:तालुका|तहसील|मंडल)[\s:]*([^\n\r]+)',
                r'(?:தாலுகா|தெஹ்சில்|மண்டலம்)[\s:]*([^\n\r]+)',
                r'(?:తాలూకా|తహసీల్|మండలం)[\s:]*([^\n\r]+)',
                r'(?:ತಾಲೂಕು|ತಹಸೀಲು|ಮಂಡಲ)[\s:]*([^\n\r]+)',
                r'(?:താലൂക്ക്|തഹസീൽ|മണ്ഡലം)[\s:]*([^\n\r]+)',
                r'(?:তালুক|তহশিল|মণ্ডল)[\s:]*([^\n\r]+)',
                r'(?:ତାଲୁକ|ତହସିଲ|ମଣ୍ଡଳ)[\s:]*([^\n\r]+)'
            ],
            'district': [
                r'(?:district|zila|jila)[\s:]*([^\n\r]+)',
                r'(?:जिला|डिस्ट्रिक्ट)[\s:]*([^\n\r]+)',
                # Tamil patterns (with OCR spacing tolerance)
                r'(?:ம\s*வ\s*ட\s*ட\s*ம\s*|ட\s*ட\s*ர\s*க\s*ட\s*)[\s:]*([^\n\r]+)',
                # Tamil patterns (normal)
                r'(?:மாவட்டம்|டிஸ்ட்ரிக்ட்)[\s:]*([^\n\r]+)',
                # Specific Tamil Nadu pattern
                r'மாவட்டம்\s*:\s*([^\n\r]+)',
                r'ம\s*வ\s*ட\s*ட\s*ம\s*:\s*([^\n\r]+)',
                r'(?:జిల్లా|డిస్ట్రిక్ట్)[\s:]*([^\n\r]+)',
                r'(?:ಜಿಲ್ಲೆ|ಡಿಸ್ಟ್ರಿಕ್ಟ್)[\s:]*([^\n\r]+)',
                r'(?:ജില്ല|ഡിസ്ട്രിക്റ്റ്)[\s:]*([^\n\r]+)',
                r'(?:জেলা|ডিস্ট্রিক্ট)[\s:]*([^\n\r]+)',
                r'(?:ଜିଲ୍ଲା|ଡିଷ୍ଟ୍ରିକ୍ଟ୍)[\s:]*([^\n\r]+)'
            ],
            'date': [
                r'(?:date|issued on|date of issue)[\s:]*([^\n\r\d]*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}[^\n\r]*)',
                r'(?:तारीख|जारी की तारीख|दिनांक)[\s:]*([^\n\r\d]*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}[^\n\r]*)',
                r'(?:தேதி|வெளியிடப்பட்ட தேதி|திகதி)[\s:]*([^\n\r\d]*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}[^\n\r]*)',
                r'(?:తేదీ|విడుదల తేదీ|దినాంకం)[\s:]*([^\n\r\d]*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}[^\n\r]*)',
                r'(?:ದಿನಾಂಕ|ವಿಡುಗಡೆ ದಿನಾಂಕ|ತಾರೀಖು)[\s:]*([^\n\r\d]*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}[^\n\r]*)',
                r'(?:തീയതി|വിഡുദല തീയതി|ദിനാംകം)[\s:]*([^\n\r\d]*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}[^\n\r]*)',
                r'(?:তারিখ|প্রকাশের তারিখ|দিনাংক)[\s:]*([^\n\r\d]*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}[^\n\r]*)',
                r'(?:ତାରିଖ|ପ୍ରକାଶ ତାରିଖ|ଦିନାଙ୍କ)[\s:]*([^\n\r\d]*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}[^\n\r]*)'
            ]
        }
    
    def extract_from_pdf(self, pdf_path: str) -> Dict:
        """
        Main method to extract data from PDF
        """
        try:
            logger.info(f"Starting extraction from PDF: {pdf_path}")
            
            # Step 1: Try to extract text directly from PDF
            text_extracted = self._extract_text_from_pdf(pdf_path)
            
            if not text_extracted:
                # Step 2: If no text, use OCR
                logger.info("No searchable text found, using OCR...")
                text_extracted = self._extract_text_with_ocr(pdf_path)
            
            if text_extracted:
                # Step 3: Parse the extracted text
                self.extracted_data = self._parse_text(text_extracted)
                logger.info("Data extraction completed successfully")
                return self.extracted_data
            else:
                logger.error("Failed to extract text from PDF")
                return {"error": "Failed to extract text from PDF"}
                
        except Exception as e:
            logger.error(f"Error during extraction: {str(e)}")
            return {"error": f"Extraction failed: {str(e)}"}
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using pdfplumber
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        logger.info(f"Extracted text from page {page_num + 1}")
            
            self.raw_text = text
            return text if len(text.strip()) > 50 else ""  # Minimum text threshold
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _extract_text_with_ocr(self, pdf_path: str) -> str:
        """
        Extract text using OCR after converting PDF to images
        """
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            text = ""
            
            for i, image in enumerate(images):
                # Convert PIL image to bytes
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # Perform OCR with Tamil+English focus
                page_text = pytesseract.image_to_string(
                    Image.open(img_bytes),
                    lang='tam+eng',  # Tamil + English for Patta documents
                    config='--psm 6'  # Assume uniform block of text
                )
                
                if page_text:
                    text += page_text + "\n"
                    logger.info(f"OCR completed for page {i + 1}")
            
            self.raw_text = text
            return text if len(text.strip()) > 50 else ""
            
        except Exception as e:
            logger.error(f"Error during OCR: {str(e)}")
            return ""
    
    def _parse_text(self, text: str) -> Dict:
        """
        Parse extracted text to find structured data
        """
        result = {
            "name": "",
            "father_or_husband": "",
            "patta_no": "",
            "survey_no": "",
            "dag_no": "",
            "khasra": "",
            "area": "",
            "village": "",
            "taluk": "",
            "district": "",
            "date": ""
        }
        
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Extract each field
        for field, patterns in self.field_patterns.items():
            extracted_value = self._extract_field_value(text, patterns)
            if extracted_value:
                result[field] = extracted_value
                self.confidence_scores[field] = self._calculate_confidence(extracted_value, text)
        
        # Post-process and validate
        result = self._post_process_data(result)
        
        # Add raw text snippet for debugging
        result['raw_text_snippet'] = text[:1000] if text else ""
        
        # Add needs_review flag for low confidence fields
        result['needs_review'] = {}
        for field, value in result.items():
            if field in ['raw_text_snippet', 'needs_review']:
                continue
            confidence = self.confidence_scores.get(field, 0)
            if confidence < 0.6:
                result['needs_review'][field] = True
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for better pattern matching
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s:/\-\.]', ' ', text)
        
        # Normalize case for English text
        text = re.sub(r'\b(name|owner|father|husband|patta|survey|dag|khasra|area|village|taluk|district|date)\b', 
                     lambda m: m.group(1).lower(), text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _extract_field_value(self, text: str, patterns: List[str]) -> str:
        """
        Extract field value using multiple patterns
        """
        for pattern in patterns:
            try:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Take the first match and clean it
                    value = matches[0].strip()
                    if value and len(value) > 2:  # Minimum length threshold
                        return self._clean_field_value(value)
            except Exception as e:
                logger.warning(f"Pattern matching error: {str(e)}")
                continue
        
        return ""
    
    def _clean_field_value(self, value: str) -> str:
        """
        Clean extracted field value
        """
        # Remove common prefixes/suffixes
        value = re.sub(r'^(name|owner|father|husband|patta|survey|dag|khasra|area|village|taluk|district|date)[\s:]*', 
                      '', value, flags=re.IGNORECASE)
        
        # Remove extra punctuation
        value = re.sub(r'[^\w\s/\-\.]', '', value)
        
        # Remove extra whitespace
        value = re.sub(r'\s+', ' ', value).strip()
        
        return value
    
    def _calculate_confidence(self, value: str, full_text: str) -> float:
        """
        Calculate confidence score for extracted value
        """
        if not value:
            return 0.0
        
        # Simple confidence based on value length and context
        confidence = min(len(value) / 50.0, 1.0)  # Longer values are more confident
        
        # Check if value appears in multiple contexts
        occurrences = full_text.lower().count(value.lower())
        if occurrences > 1:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _post_process_data(self, data: Dict) -> Dict:
        """
        Post-process and validate extracted data for Tamil+English Patta documents
        """
        # Validate and clean each field
        for field, value in data.items():
            if value and field not in ['raw_text_snippet', 'needs_review']:
                # Remove any remaining unwanted characters but preserve Tamil characters
                data[field] = re.sub(r'[^\w\s/\-\.\u0B80-\u0BFF]', '', value).strip()
                
                # Special processing for specific fields
                if field == 'date':
                    data[field] = self._normalize_date(value)
                elif field in ['patta_no', 'survey_no', 'dag_no', 'khasra']:
                    data[field] = self._extract_numbers(value)
                elif field == 'area':
                    data[field] = self._normalize_area(value)
                elif field in ['name', 'father_or_husband']:
                    # Uppercase names for consistency
                    data[field] = value.title()
                elif field in ['village', 'taluk', 'district']:
                    # Clean location names
                    data[field] = re.sub(r'\s+', ' ', value).strip()
        
        # Replace empty strings with null as requested
        for field in ['name', 'father_or_husband', 'patta_no', 'survey_no', 'dag_no', 'khasra', 'area', 'village', 'taluk', 'district', 'date']:
            if not data.get(field):
                data[field] = None
        
        return data
    
    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize date format to DD-MM-YYYY for Tamil+English Patta documents
        """
        try:
            # Try to parse common date formats
            date_patterns = [
                r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})',
                r'(\d{1,2})\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{2,4})',
                r'(\d{1,2})\s+(?:தேதி|திகதி)\s+(\d{1,2})[\/\-\.](\d{2,4})',
                r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    if len(groups) >= 3:
                        day, month, year = groups[0], groups[1], groups[2]
                        # Ensure 4-digit year
                        if len(year) == 2:
                            year = '20' + year if int(year) < 50 else '19' + year
                        # Format as DD-MM-YYYY
                        return f"{day.zfill(2)}-{month.zfill(2)}-{year}"
                    else:
                        return match.group(0)
            
            return date_str
        except:
            return date_str
    
    def _extract_numbers(self, text: str) -> str:
        """
        Extract numbers from text
        """
        numbers = re.findall(r'\d+', text)
        return '/'.join(numbers) if numbers else text
    
    def _normalize_area(self, area_str: str) -> str:
        """
        Normalize area measurements
        """
        # Extract number and unit
        match = re.search(r'(\d+(?:\.\d+)?)\s*(acres?|hectares?|sq\.?\s*ft|sq\.?\s*m|गज|एकड़|हेक्टेयर|ஏக்கர்|హెక్టార్|ಎಕರೆ|ഏക്കർ|একর|ଏକର)', 
                        area_str, re.IGNORECASE)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        
        return area_str
    
    def get_extraction_summary(self) -> Dict:
        """
        Get summary of extraction process
        """
        total_fields = len(self.field_patterns)
        extracted_fields = sum(1 for value in self.extracted_data.values() if value)
        
        return {
            "total_fields": total_fields,
            "extracted_fields": extracted_fields,
            "extraction_rate": round((extracted_fields / total_fields) * 100, 2),
            "confidence_scores": self.confidence_scores,
            "average_confidence": round(sum(self.confidence_scores.values()) / len(self.confidence_scores), 2) if self.confidence_scores else 0,
            "text_length": len(self.raw_text),
            "extraction_timestamp": datetime.now().isoformat()
        }


def extract_patta_data(pdf_path: str) -> Dict:
    """
    Convenience function to extract data from Patta PDF
    """
    extractor = PattaExtractor()
    result = extractor.extract_from_pdf(pdf_path)
    
    # Add extraction summary
    if "error" not in result:
        result["extraction_summary"] = extractor.get_extraction_summary()
    
    return result


if __name__ == "__main__":
    # Test the extractor
    test_pdf = "sample_patta.pdf"
    if os.path.exists(test_pdf):
        result = extract_patta_data(test_pdf)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Test PDF not found. Please provide a sample Patta document.")




