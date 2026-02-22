import pytesseract
import spacy
import re
from pdf2image import convert_from_path
from PIL import Image
import os

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Regex for Indian phone numbers and emails
phone_pattern = re.compile(r'\b(?:\+91[-\s]?|0)?[6-9]\d{9}\b')
email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

# Indian address keywords (basic)
address_keywords = ['Village', 'Taluka', 'District', 'State', 'Pin', 'Pincode']

def extract_address(text):
    lines = text.splitlines()
    address_lines = [line for line in lines if any(kw.lower() in line.lower() for kw in address_keywords)]
    return ', '.join(address_lines) if address_lines else 'Unknown'

def process_patta_document(filepath):
    text = ""

    # PDF to images
    if filepath.lower().endswith(".pdf"):
        images = convert_from_path(filepath, dpi=300, poppler_path=r"C:\Program Files\poppler-24.02.0\Library\bin")
        for img in images:
            text += pytesseract.image_to_string(img)
    else:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)

    # NLP entity detection
    doc = nlp(text)
    extracted = {
        "patta_holder": "Unknown",
        "village": "Unknown",
        "phone": "Unknown",
        "email": "Unknown",
        "address": "Unknown"
    }

    for ent in doc.ents:
        if ent.label_ == "PERSON" and extracted["patta_holder"] == "Unknown":
            extracted["patta_holder"] = ent.text
        if ent.label_ in ["GPE", "LOC"] and extracted["village"] == "Unknown":
            extracted["village"] = ent.text

    # Regex extraction
    phone_match = phone_pattern.search(text)
    if phone_match:
        extracted["phone"] = phone_match.group()
    
    email_match = email_pattern.search(text)
    if email_match:
        extracted["email"] = email_match.group()

    extracted["address"] = extract_address(text)

    return extracted
