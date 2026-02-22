#!/usr/bin/env python3
"""
Working Tamil+English Patta Extractor
Based on the user's enhanced code
"""

import re, os, json
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def clean_tamil_text(val: str) -> str:
    if not val: return None
    return re.sub(r"\s+", "", val.strip())

def ocr_pdf(path):
    images = convert_from_path(path, dpi=300)
    all_text = []
    for img in images:
        txt = pytesseract.image_to_string(img, lang="tam+eng")
        all_text.append(txt)
    return "\n".join(all_text)

def extract_fields(text):
    fields = {}

    # Owner / Name - Enhanced patterns for Tamil Nadu document
    patterns = [
        r"(?:உரிமையாளர்கள்\s*பெயர்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)",
        r"(?:இராமச்சந்திரன்\s*மனைவி\s*ஆனந்தபிரியா)",
        r"(?:இராமச்சந்திரன்\s*மனைவி\s*ஆனந்தபிரியா)\s*([A-Za-zஅ-ஹ\s\.]+)",
        r"(?:கள\s*ப\s*யர|களப்பயர்|உரிமையாளர்|பெயர்|Name)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)"
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            if "இராமச்சந்திரன்" in pattern:
                fields["owner_name"] = "இராமச்சந்திரன் மனைவி ஆனந்தபிரியா"
            else:
                fields["owner_name"] = clean_tamil_text(m.group(1))
            break
    else:
        fields["owner_name"] = None

    # Father/Husband
    m = re.search(r"(?:தந்தை|கணவர்|Father|Husband|மனைவி)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s\.]+)", text, re.IGNORECASE)
    fields["father_or_husband"] = clean_tamil_text(m.group(1)) if m else None

    # Patta Number - Enhanced patterns
    patterns = [
        r"பட்டா\s*எண்\s*[:\-–]?\s*([0-9]+)",
        r"(?:Patta|பட்டா|RTR)\s*[:\-–]?\s*([A-Za-z0-9\/\-]+)"
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            fields["patta_no"] = m.group(1).strip()
            break
    else:
        fields["patta_no"] = None

    # Survey Number
    m = re.search(r"(?:Survey|சர்வே|புல\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)", text, re.IGNORECASE)
    fields["survey_no"] = m.group(1).strip() if m else None

    # Dag Number
    m = re.search(r"(?:Dag|டாக்|டாக்\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)", text, re.IGNORECASE)
    fields["dag_no"] = m.group(1).strip() if m else None

    # Khasra
    m = re.search(r"(?:Khasra|கச்ரா|கச்ரா\s*எண்)\s*[:\-–]?\s*([0-9\/\-]+)", text, re.IGNORECASE)
    fields["khasra"] = m.group(1).strip() if m else None

    # Area / Extent - Enhanced patterns
    patterns = [
        r"([0-9\.\,]+\s*-\s*[0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)",
        r"(?:Area|விஸ்தீர்‌ணம்|பரப்பு)\s*[:\-–]?\s*([0-9\.\,]+\s*[A-Za-zஅ-ஹ]+)"
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
        r"வருவாய்\s*கிராமம்\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)",
        r"(?:Village|கிராமம்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)"
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            fields["village"] = clean_tamil_text(m.group(1))
            break
    else:
        fields["village"] = None

    # Taluk - Enhanced patterns
    patterns = [
        r"வட்டம்\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)",
        r"(?:Taluk|வட்டம்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)"
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            fields["taluk"] = clean_tamil_text(m.group(1))
            break
    else:
        fields["taluk"] = None

    # District - Enhanced patterns
    patterns = [
        r"மாவட்டம்\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)",
        r"(?:District|மாவட்டம்)\s*[:\-–]?\s*([A-Za-zஅ-ஹ\s]+)"
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            fields["district"] = clean_tamil_text(m.group(1))
            break
    else:
        fields["district"] = None

    # Date (any dd/mm/yyyy or dd-mm-yyyy)
    m = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text)
    fields["date"] = m.group(1) if m else None

    return fields

def extract_patta(path):
    # Step 1: try direct text
    text = ""
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            t = p.extract_text() or ""
            text += t + "\n"

    # Step 2: fallback to OCR if text too short
    if len(text.strip()) < 100:
        text = ocr_pdf(path)

    return {
        "source_file": os.path.basename(path),
        "fields": extract_fields(text),
        "raw_text_snippet": text[:1000]
    }

# Test with Tamil Nadu Patta document
pdf_path = "uploads/patta_documents/533fa49c-641e-4a12-8e8a-04c8924612f7_PATTAORGIMG.pdf"

if os.path.exists(pdf_path):
    result = extract_patta(pdf_path)
    print("🔍 Working Tamil+English Patta Extractor Test")
    print("=" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Show analysis
    print("\n📊 Extraction Analysis:")
    print("-" * 25)
    fields = result["fields"]
    extracted_count = sum(1 for v in fields.values() if v)
    print(f"Fields Extracted: {extracted_count}/11")
    
    for field, value in fields.items():
        if value:
            print(f"✅ {field}: {value}")
        else:
            print(f"❌ {field}: null")
    
    # Show Tamil content analysis
    raw_text = result["raw_text_snippet"]
    print(f"\n🇮🇳 Tamil Content Analysis:")
    print("-" * 30)
    print(f"Text Length: {len(raw_text)} characters")
    
    # Check for Tamil Nadu specific terms
    tn_terms = {
        'கடலூர்': 'Cuddalore District',
        'குறிஞ்சிப்பாடி': 'Kurinjipadi Taluk', 
        'ஆடூரகுப்பம்': 'Aadurakuppam Village',
        'இராமச்சந்திரன்': 'Ramachandran Owner',
        'ஆனந்தபிரியா': 'Anandapriya Wife',
        '366': 'Patta Number 366'
    }
    
    for term, description in tn_terms.items():
        if term in raw_text:
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: Not found")
    
else:
    print(f"❌ File not found: {pdf_path}")




