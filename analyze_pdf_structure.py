#!/usr/bin/env python3
"""
Detailed analysis of PDF content structure.
"""

import pdfplumber
from pathlib import Path

def analyze_pdf_structure(pdf_path, max_lines=50):
    """Analyze the structure of a PDF to understand data format."""
    print(f"\n=== Detailed Analysis: {pdf_path.name} ===")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Look at first few pages
            for page_num in range(min(3, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if text:
                    print(f"\n--- Page {page_num + 1} ---")
                    lines = text.split('\n')
                    
                    for i, line in enumerate(lines[:max_lines]):
                        if line.strip():
                            print(f"Line {i+1:2d}: {repr(line)}")
                    
                    if len(lines) > max_lines:
                        print(f"... and {len(lines) - max_lines} more lines")
                    
                    break  # Just first page for analysis
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Analyze one HR185 file
    hr185_file = Path("Data Hand-Over/HR185/1-HR185 - Transactions per Supplier - 202207 - 202306.pdf")
    if hr185_file.exists():
        analyze_pdf_structure(hr185_file, max_lines=30)
    
    # Analyze one HR990 file  
    hr990_file = Path("Data Hand-Over/HR990/1-HR990 - Expenditure Statistics - 202207 - 202306.pdf")
    if hr990_file.exists():
        analyze_pdf_structure(hr990_file, max_lines=30)
