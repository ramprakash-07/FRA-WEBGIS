"""
Simplified OCR/NER module without spacy dependency
"""
import pytesseract
from pdf2image import convert_from_path
import re
import os

# Set Tesseract path (adjust if different)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def pdf_to_text(pdf_path):
    """Extract text from PDF using OCR"""
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300)
        
        # Extract text from each image
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image, lang='eng') + "\n"
        
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_entities(text):
    """Extract entities from text using simple regex patterns"""
    try:
        # Simple regex patterns for common entities
        village_pattern = r'(?:village|ग्राम|गांव|கிராமம்)\s*[:\-]?\s*([A-Za-z\s]+)'
        holder_pattern = r'(?:name|नाम|பெயர்|holder|धारक)\s*[:\-]?\s*([A-Za-z\s]+)'
        lat_pattern = r'(?:latitude|अक्षांश|அட்சரேகை)\s*[:\-]?\s*([0-9\.]+)'
        lon_pattern = r'(?:longitude|देशांतर|தீர்க்கரேகை)\s*[:\-]?\s*([0-9\.]+)'
        
        village = re.search(village_pattern, text, re.IGNORECASE)
        holder = re.search(holder_pattern, text, re.IGNORECASE)
        lat = re.search(lat_pattern, text, re.IGNORECASE)
        lon = re.search(lon_pattern, text, re.IGNORECASE)
        
        return (
            village.group(1).strip() if village else None,
            holder.group(1).strip() if holder else None,
            lat.group(1).strip() if lat else None,
            lon.group(1).strip() if lon else None
        )
    except Exception as e:
        print(f"Error extracting entities: {e}")
        return None, None, None, None
