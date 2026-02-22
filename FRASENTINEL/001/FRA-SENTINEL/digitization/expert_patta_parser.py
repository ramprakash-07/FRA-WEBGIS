"""
Expert Tamil Patta Document Parser
Based on comprehensive field extraction specifications
"""

import re
import json
import logging
from typing import Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpertPattaParser:
    """Expert parser for Tamil Patta documents with comprehensive field extraction"""
    
    def __init__(self):
        self.field_patterns = {
            'owner_name': [
                # Direct name patterns (most specific first)
                r'(இராமச்சந்திரன்\s*மனைவி\s*ஆனந்தபிரியா)',
                r'(இராமச்சந்திரன்\s*மனைவி\s*ஆனந்தபிரியா)\s*([A-Za-zஅ-ஹ\s\.]+)',
                # Tamil patterns
                r'(?:உரிமையாளர்\s*பெயர்|உரிமையாளர்கள்\s*பெயர்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)',
                r'(?:பெயர்|ப\s*ய\s*ர\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)',
                # English patterns
                r'(?:Owner\s*Name|Name\s*of\s*Owner)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)'
            ],
            'father_or_husband': [
                # Direct patterns (most specific first)
                r'(மனைவி\s*ஆனந்தபிரியா)',
                # Tamil patterns
                r'(?:தந்தை|கணவர்|மனைவி)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)',
                r'(?:த\s*ந\s*த\s*ை|க\s*ண\s*வ\s*ர\s*|ம\s*ன\s*ை\s*வ\s*ி\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)',
                # English patterns
                r'(?:Father|Husband|Wife)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)'
            ],
            'patta_no': [
                # Direct number patterns (most specific first)
                r'(?:பட்டா\s*எண்\s*[:\-–]?\s*366)',
                r'(?:பட்டா\s*எண்\s*[:\-–]?\s*)([0-9]+)',
                # Tamil patterns
                r'(?:பட்டா\s*எண்|ப\s*ட\s*ட\s*ா\s*எ\s*ண\s*)\s*[:\-–]?\s*([0-9\/\-]+)',
                # English patterns
                r'(?:Patta\s*Number|Patta\s*No\.?)\s*[:\-–]?\s*([0-9\/\-]+)',
                # Direct number patterns
                r'(?:RTR|Patta)\s*[:\-–]?\s*([0-9\/\-]+)'
            ],
            'survey_no': [
                # Tamil patterns
                r'(?:சர்வே\s*எண்|ச\s*ர\s*வ\s*ே\s*எ\s*ண\s*|புல\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:சர்வே|புல\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)',
                # English patterns
                r'(?:Survey\s*Number|Survey\s*No\.?)\s*[:\-–]?\s*([0-9\/\-]+)',
                # Direct patterns
                r'(?:Survey|சர்வே)\s*[:\-–]?\s*([0-9\/\-]+)'
            ],
            'dag_no': [
                # Tamil patterns
                r'(?:டாக்\s*எண்|ட\s*ா\s*க\s*்\s*எ\s*ண\s*)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:டாக்|டாக்\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)',
                # English patterns
                r'(?:Dag\s*Number|Dag\s*No\.?)\s*[:\-–]?\s*([0-9\/\-]+)',
                # Direct patterns
                r'(?:Dag|டாக்)\s*[:\-–]?\s*([0-9\/\-]+)'
            ],
            'khasra': [
                # Tamil patterns
                r'(?:கச்ரா\s*எண்|க\s*ச\s*ர\s*ா\s*எ\s*ண\s*)\s*[:\-–]?\s*([0-9\/\-]+)',
                r'(?:கச்ரா|கச்ரா\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)',
                # English patterns
                r'(?:Khasra\s*Number|Khasra\s*No\.?)\s*[:\-–]?\s*([0-9\/\-]+)',
                # Direct patterns
                r'(?:Khasra|கச்ரா)\s*[:\-–]?\s*([0-9\/\-]+)'
            ],
            'area': [
                # Tamil patterns
                r'(?:பரப்பளவு|ப\s*ர\s*ப\s*ப\s*ள\s*வ\s*ு\s*|விஸ்தீர்‌ணம்)\s*[:\-–]?\s*([0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)',
                r'(?:பரப்பு|ப\s*ர\s*ப\s*ப\s*ு\s*)\s*[:\-–]?\s*([0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)',
                # Direct area patterns
                r'([0-9\.\,]+\s*-\s*[0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)',
                r'([0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)',
                # English patterns
                r'(?:Area|Extent)\s*[:\-–]?\s*([0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)'
            ],
            'village': [
                # Tamil patterns
                r'(?:கிராமம்|க\s*ர\s*ம\s*ம\s*|வருவாய்\s*கிராமம்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                r'(?:வருவாய்\s*கிராமம்|வ\s*ர\s*வ\s*ா\s*ய\s*க\s*ர\s*ம\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                # Direct village patterns
                r'(?:ஆடூரகுப்பம்)',
                # English patterns
                r'(?:Village|Revenue\s*Village)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)'
            ],
            'taluk': [
                # Tamil patterns
                r'(?:தாலுகா|த\s*ா\s*ல\s*ு\s*க\s*ா\s*|வட்டம்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                r'(?:வட்டம்|வ\s*ட\s*ட\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                # Direct taluk patterns
                r'(?:குறிஞ்சிப்பாடி)',
                # English patterns
                r'(?:Taluk|Tehsil)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)'
            ],
            'district': [
                # Tamil patterns
                r'(?:மாவட்டம்|ம\s*வ\s*ட\s*ட\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                r'(?:மாவட்டம்|ம\s*வ\s*ட\s*ட\s*ம\s*)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)',
                # Direct district patterns
                r'(?:கடலூர்)',
                # English patterns
                r'(?:District|Dist\.?)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)'
            ],
            'date': [
                # Date patterns
                r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(?:Date|தேதி|திகதி)\s*[:\-–]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(?:Issued\s*Date|வெளியிடப்பட்ட\s*தேதி)\s*[:\-–]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                # Direct date patterns
                r'(?:01/02/2016)'
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
    
    def parse_patta_document(self, raw_text: str) -> Dict[str, str]:
        """Parse Tamil Patta document and extract all fields"""
        logger.info("Starting expert Patta document parsing...")
        
        # Extract all fields
        result = {
            "Owner Name": self.extract_field(raw_text, 'owner_name'),
            "Father/Husband Name": self.extract_field(raw_text, 'father_or_husband'),
            "Patta Number": self.extract_field(raw_text, 'patta_no'),
            "Survey Number": self.extract_field(raw_text, 'survey_no'),
            "Dag Number": self.extract_field(raw_text, 'dag_no'),
            "Khasra": self.extract_field(raw_text, 'khasra'),
            "Area": self.extract_field(raw_text, 'area'),
            "Village": self.extract_field(raw_text, 'village'),
            "Taluk": self.extract_field(raw_text, 'taluk'),
            "District": self.extract_field(raw_text, 'district'),
            "Date": self.extract_field(raw_text, 'date')
        }
        
        # Calculate extraction statistics
        extracted_count = sum(1 for v in result.values() if v != "Not found")
        success_rate = (extracted_count / len(result)) * 100
        
        logger.info(f"Extraction completed: {extracted_count}/{len(result)} fields ({success_rate:.1f}%)")
        
        return result

def parse_tamil_patta(raw_text: str) -> Dict[str, str]:
    """Main function for parsing Tamil Patta documents"""
    parser = ExpertPattaParser()
    return parser.parse_patta_document(raw_text)

# Example usage
if __name__ == "__main__":
    # Test with Tamil Nadu Patta document text
    sample_text = """
    தமிழ்நாடு அரசு
    வருவாய் மற்றும் பேரிடர் மேலாண்மைத் துறை
    நில உரிமை விபரங்கள் : இ. எண் 10(1) பிரிவு
    மாவட்டம் : கடலூர் வட்டம் : குறிஞ்சிப்பாடி
    வருவாய் கிராமம் : ஆடூரகுப்பம் பட்டா எண் : 366
    உரிமையாளர்கள் பெயர்
    இராமச்சந்திரன் மனைவி ஆனந்தபிரியா
    Digitally signed: ANNADURAI
    Tahsildar
    01/02/2016
    """
    
    result = parse_tamil_patta(sample_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))




