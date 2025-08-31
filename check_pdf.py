#!/usr/bin/env python3
"""
Check PDF content to see if we can extract data.
"""

import pdfplumber
import pandas as pd
from pathlib import Path

def check_pdf_content(pdf_path):
    """Check what's in a PDF file."""
    print(f"\n=== Checking: {pdf_path} ===")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Pages: {len(pdf.pages)}")
            
            # Check first page
            if len(pdf.pages) > 0:
                page = pdf.pages[0]
                
                # Extract text
                text = page.extract_text()
                if text:
                    print(f"Text found (first 300 chars):")
                    print(text[:300])
                    print("...")
                else:
                    print("No text found - likely scanned image")
                
                # Check for tables
                tables = page.extract_tables()
                print(f"Tables found: {len(tables)}")
                
                if tables:
                    print("First table preview:")
                    for i, row in enumerate(tables[0][:3]):  # First 3 rows
                        print(f"Row {i}: {row}")
                
                # Check if it might be an image-based PDF
                if not text and not tables:
                    print("⚠️  This appears to be a scanned image PDF")
                    print("💡 Would need OCR (pytesseract/easyocr) to extract data")
                
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    # Check HR185 PDFs
    hr185_folder = Path("Data Hand-Over/HR185")
    for pdf_file in hr185_folder.glob("*.pdf"):
        check_pdf_content(pdf_file)
    
    # Check HR990 PDFs  
    hr990_folder = Path("Data Hand-Over/HR990")
    for pdf_file in hr990_folder.glob("*.pdf"):
        check_pdf_content(pdf_file)
