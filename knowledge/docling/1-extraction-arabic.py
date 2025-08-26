#!/usr/bin/env python3
"""
Arabic PDF Extraction with Enhanced Language Support
Optimized for Arabic text processing and encoding
"""

from docling.document_converter import DocumentConverter
import os
import re

def clean_arabic_text(text):
    """Clean and normalize Arabic text"""
    # Remove common PDF artifacts
    text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}\"\']+', ' ', text)
    
    # Normalize Arabic text
    text = re.sub(r'[ـ]+', '', text)  # Remove tatweel (stretching)
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    return text

def extract_arabic_pdf(pdf_path):
    """Extract content from Arabic PDF with enhanced processing"""
    
    print(f"🔍 Processing Arabic PDF: {pdf_path}")
    print("=" * 60)
    
    # Initialize converter
    converter = DocumentConverter()
    
    try:
        # Convert PDF
        print("📄 Converting PDF to document object...")
        result = converter.convert(pdf_path)
        
        if not result.document:
            print("❌ Failed to extract document")
            return None
            
        print("✅ PDF conversion successful")
        
        # Export to different formats
        print("📝 Exporting content...")
        
        # Markdown export
        markdown_content = result.document.export_to_markdown()
        print(f"✅ Markdown export: {len(markdown_content)} characters")
        
        # Clean Arabic text
        cleaned_markdown = clean_arabic_text(markdown_content)
        print(f"✅ Text cleaning: {len(cleaned_markdown)} characters after cleaning")
        
        # Count Arabic characters
        arabic_chars = sum(1 for char in cleaned_markdown if '\u0600' <= char <= '\u06FF')
        print(f"📊 Arabic characters found: {arabic_chars}")
        
        # Save cleaned content
        output_file = "arabic_content_cleaned.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_markdown)
        print(f"💾 Cleaned content saved to: {output_file}")
        
        # Show sample of cleaned content
        print("\n📖 Sample of cleaned Arabic content:")
        print("-" * 40)
        sample = cleaned_markdown[:800]
        print(sample)
        print("-" * 40)
        
        return {
            'original': markdown_content,
            'cleaned': cleaned_markdown,
            'arabic_char_count': arabic_chars,
            'total_chars': len(cleaned_markdown)
        }
        
    except Exception as e:
        print(f"❌ Error processing Arabic PDF: {e}")
        return None

def analyze_arabic_content(content):
    """Analyze Arabic content structure"""
    
    print("\n🔍 Analyzing Arabic content structure...")
    print("=" * 40)
    
    # Split into lines
    lines = content.split('\n')
    print(f"📊 Total lines: {len(lines)}")
    
    # Count lines with Arabic content
    arabic_lines = 0
    for line in lines:
        if any('\u0600' <= char <= '\u06FF' for char in line):
            arabic_lines += 1
    
    print(f"📊 Lines with Arabic text: {arabic_lines}")
    
    # Find Arabic headers (lines starting with ##)
    headers = [line for line in lines if line.startswith('##') and any('\u0600' <= char <= '\u06FF' for char in line)]
    print(f"📊 Arabic headers found: {len(headers)}")
    
    if headers:
        print("📋 Sample headers:")
        for i, header in enumerate(headers[:5]):
            print(f"   {i+1}. {header}")
    
    return {
        'total_lines': len(lines),
        'arabic_lines': arabic_lines,
        'arabic_headers': len(headers)
    }

if __name__ == "__main__":
    # Process Arabic PDF
    pdf_file = "KFH_Real_Estate_Report_2025_Q1_arb.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        exit(1)
    
    # Extract content
    result = extract_arabic_pdf(pdf_file)
    
    if result:
        # Analyze content
        analysis = analyze_arabic_content(result['cleaned'])
        
        print("\n" + "=" * 60)
        print("📊 Arabic PDF Processing Summary")
        print("=" * 60)
        print(f"✅ PDF processed successfully")
        print(f"📄 Total characters: {result['total_chars']:,}")
        print(f"🔤 Arabic characters: {result['arabic_char_count']:,}")
        print(f"📊 Arabic content ratio: {(result['arabic_char_count']/result['total_chars']*100):.1f}%")
        print(f"📝 Lines with Arabic: {analysis['arabic_lines']}/{analysis['total_lines']}")
        print(f"📋 Arabic headers: {analysis['arabic_headers']}")
        print("=" * 60)
    else:
        print("❌ Failed to process Arabic PDF")
