#!/usr/bin/env python3
"""
Test Arabic PDF Processing Capabilities
Tests the system's ability to handle Arabic PDF documents
"""

import os
import sys
from pathlib import Path

def test_arabic_pdf_processing():
    """Test Arabic PDF processing capabilities"""
    
    print("🧪 Testing Arabic PDF Processing Capabilities")
    print("=" * 60)
    
    # Test 1: Check Arabic PDF exists
    arabic_pdf = "KFH_Real_Estate_Report_2025_Q1_arb.pdf"
    if not os.path.exists(arabic_pdf):
        print(f"❌ Arabic PDF not found: {arabic_pdf}")
        return False
    else:
        print(f"✅ Arabic PDF found: {arabic_pdf}")
        print(f"   File size: {os.path.getsize(arabic_pdf) / (1024*1024):.2f} MB")
    
    # Test 2: Test basic extraction
    try:
        from docling.document_converter import DocumentConverter
        print("✅ Docling imported successfully")
        
        converter = DocumentConverter()
        print("✅ DocumentConverter initialized")
        
        # Extract Arabic PDF
        print(f"🔍 Extracting content from Arabic PDF...")
        result = converter.convert(arabic_pdf)
        
        if result.document:
            print("✅ Arabic PDF extraction successful")
            
            # Test markdown export
            try:
                markdown_content = result.document.export_to_markdown()
                print(f"✅ Markdown export successful")
                print(f"   Content length: {len(markdown_content)} characters")
                
                # Check for Arabic text
                arabic_chars = sum(1 for char in markdown_content if '\u0600' <= char <= '\u06FF')
                print(f"   Arabic characters found: {arabic_chars}")
                
                # Show sample content
                sample = markdown_content[:500]
                print(f"   Sample content: {sample}...")
                
            except Exception as e:
                print(f"❌ Markdown export failed: {e}")
                
        else:
            print("❌ Arabic PDF extraction failed")
            return False
            
    except Exception as e:
        print(f"❌ Arabic PDF processing failed: {e}")
        return False
    
    # Test 3: Test chunking
    try:
        from docling.chunking import HybridChunker
        print("✅ HybridChunker imported successfully")
        
        # Create chunks
        chunker = HybridChunker(max_tokens=1000, merge_peers=True)
        chunk_iter = chunker.chunk(dl_doc=result.document)
        chunks = list(chunk_iter)
        
        print(f"✅ Chunking successful: {len(chunks)} chunks created")
        
        # Check first chunk for Arabic content
        if chunks:
            first_chunk = chunks[0]
            if hasattr(first_chunk, 'text'):
                chunk_text = first_chunk.text
                arabic_chars_in_chunk = sum(1 for char in chunk_text if '\u0600' <= char <= '\u06FF')
                print(f"   First chunk Arabic characters: {arabic_chars_in_chunk}")
                print(f"   First chunk preview: {chunk_text[:200]}...")
        
    except Exception as e:
        print(f"❌ Chunking failed: {e}")
    
    # Test 4: Test embedding generation
    try:
        from openai import AzureOpenAI
        from dotenv import load_dotenv
        
        load_dotenv()
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        print("✅ Azure OpenAI client initialized")
        
        # Test embedding with Arabic text
        if chunks:
            sample_text = chunks[0].text[:100]  # First 100 chars
            print(f"🔍 Testing embedding with Arabic text: {sample_text[:50]}...")
            
            response = client.embeddings.create(
                model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
                input=[sample_text]
            )
            
            embedding = response.data[0].embedding
            print(f"✅ Arabic text embedding successful")
            print(f"   Embedding dimensions: {len(embedding)}")
            
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Arabic PDF Processing Test Complete")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_arabic_pdf_processing()
