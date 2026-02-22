#!/usr/bin/env python3
"""
Create proper PDF files for OCR testing
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf(filename, content):
    """Create a PDF file with the given content"""
    
    # Create PDF
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Set font and size
    c.setFont("Helvetica", 12)
    
    # Split content into lines
    lines = content.strip().split('\n')
    
    # Draw each line
    y_position = height - 50
    for line in lines:
        if line.strip():
            c.drawString(50, y_position, line.strip())
            y_position -= 20
    
    # Save PDF
    c.save()
    print(f"Created PDF: {filename}")

def create_sample_pdfs():
    """Create sample PDF files for OCR testing"""
    
    # Ensure sample_data directory exists
    os.makedirs('sample_data', exist_ok=True)
    
    # Sample patta document 1
    content1 = """
FOREST RIGHTS ACT - INDIVIDUAL FOREST RIGHTS

Village: Khargone
Name: Ram Singh
Father: Suresh Singh
Tribal Group: Bhil
Claim Type: IFR
Area: 2.5 hectares
Survey No: 123/45
Dag No: 67/89
Khasra No: 1234
Patta No: 56789
Latitude: 21.8225
Longitude: 75.6102
Status: Granted
"""
    
    # Sample patta document 2
    content2 = """
FOREST RIGHTS ACT - COMMUNITY RIGHTS

Village: Jhabua
Name: Lakshmi Devi
Husband: Mohan Lal
Tribal Group: Gond
Claim Type: CR
Area: 1.8 hectares
Survey No: 234/56
Dag No: 78/90
Khasra No: 2345
Patta No: 67890
Latitude: 22.5000
Longitude: 74.5000
Status: Under Verification
"""
    
    # Sample patta document 3
    content3 = """
FOREST RIGHTS ACT - COMMUNITY FOREST RIGHTS

Village: Koraput
Name: Rajesh Kumar
Father: Vikram Singh
Tribal Group: Santal
Claim Type: CFR
Area: 3.2 hectares
Survey No: 345/67
Dag No: 89/01
Khasra No: 3456
Patta No: 78901
Latitude: 18.8000
Longitude: 82.7000
Status: Filed
"""
    
    # Create PDF files
    create_test_pdf('sample_data/sample_patta_1.pdf', content1)
    create_test_pdf('sample_data/sample_patta_2.pdf', content2)
    create_test_pdf('sample_data/sample_patta_3.pdf', content3)
    
    print("\n✅ Sample PDF files created successfully!")

if __name__ == "__main__":
    create_sample_pdfs()









