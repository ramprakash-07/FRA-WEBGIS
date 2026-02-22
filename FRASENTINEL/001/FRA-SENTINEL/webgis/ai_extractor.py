import openai
import json
from typing import Dict, Optional
import os

class AIExtractor:
    """AI-powered field extraction using OpenAI GPT"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI extractor with OpenAI API key"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        else:
            print("⚠️ OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
    
    def extract_with_ai(self, ocr_text: str) -> Dict[str, Optional[str]]:
        """Extract structured data from OCR text using AI"""
        
        if not self.api_key:
            return {"error": "OpenAI API key not configured"}
        
        try:
            prompt = self._create_extraction_prompt(ocr_text)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from Tamil land documents (Patta). Extract the requested fields accurately."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response)
            
        except Exception as e:
            return {"error": f"AI extraction failed: {str(e)}"}
    
    def _create_extraction_prompt(self, ocr_text: str) -> str:
        """Create a detailed prompt for AI extraction"""
        
        prompt = f"""
Extract the following fields from this Tamil Patta (land ownership) document OCR text:

OCR Text:
{ocr_text}

Please extract these specific fields and return ONLY a JSON object:

{{
    "district": "District name in Tamil/English",
    "taluk": "Taluk/Circle name in Tamil/English", 
    "village": "Revenue village name in Tamil/English",
    "patta_number": "Patta number (numeric only)",
    "owner_name": "Primary owner name in Tamil/English",
    "relationship": "Relationship if mentioned (e.g., 'Wife of [Name]')",
    "survey_number": "Survey number (numeric only)",
    "sub_division": "Sub-division number (numeric only)",
    "dry_land_area": "Dry land area measurement",
    "tax_amount": "Tax amount (numeric only)",
    "signed_by": "Name of person who signed",
    "signed_on": "Date and time of signature",
    "reference_number": "Reference number if any",
    "verification_url": "Verification URL if any"
}}

Important:
- Return ONLY the JSON object, no other text
- Use null for missing fields
- For Tamil text, preserve the original Tamil characters
- Extract numeric values without units
- Be precise with dates and times
"""
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict[str, Optional[str]]:
        """Parse AI response and extract JSON data"""
        try:
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # Parse JSON
            data = json.loads(response)
            return data
            
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            return {"error": "Failed to parse AI response as JSON"}
    
    def is_available(self) -> bool:
        """Check if AI extraction is available"""
        return self.api_key is not None

class HybridExtractor:
    """Combines regex and AI extraction for best results"""
    
    def __init__(self, use_ai: bool = True):
        self.regex_extractor = None  # Will be set by OCR service
        self.ai_extractor = AIExtractor()
        self.use_ai = use_ai and self.ai_extractor.is_available()
    
    def extract_fields(self, ocr_text: str, regex_data: Dict) -> Dict[str, Optional[str]]:
        """Extract fields using both regex and AI, then merge results"""
        
        # Start with regex results
        final_data = regex_data.copy()
        
        # If AI is available, enhance with AI extraction
        if self.use_ai:
            ai_data = self.ai_extractor.extract_with_ai(ocr_text)
            
            if "error" not in ai_data:
                # Merge AI results, preferring AI for missing regex fields
                for key, value in ai_data.items():
                    if value and (not final_data.get(key) or final_data.get(key) == ""):
                        final_data[key] = value
        
        return final_data

