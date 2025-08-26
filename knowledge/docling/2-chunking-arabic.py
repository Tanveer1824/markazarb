#!/usr/bin/env python3
"""
Arabic Text Chunking with Enhanced Language Support
Optimized for Arabic text processing and proper chunk sizing
"""

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from openai import AzureOpenAI
import os
import re

load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Optimized token limit for Arabic text (Arabic characters can be longer in tokens)
MAX_TOKENS = 4000  # Reduced from 8191 to avoid token length issues

def clean_arabic_text(text):
    """Clean and normalize Arabic text for better chunking"""
    # Remove common PDF artifacts
    text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}\"\']+', ' ', text)
    
    # Normalize Arabic text
    text = re.sub(r'[ـ]+', '', text)  # Remove tatweel (stretching)
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    return text

def create_arabic_optimized_chunks(document, max_tokens=MAX_TOKENS):
    """Create chunks optimized for Arabic text"""
    
    print(f"🔍 Creating Arabic-optimized chunks (max tokens: {max_tokens})")
    print("=" * 60)
    
    try:
        # Use hybrid chunking with optimized settings for Arabic
        chunker = HybridChunker(
            max_tokens=max_tokens,
            merge_peers=True,
            min_tokens=100,  # Minimum chunk size to avoid tiny fragments
        )
        
        print("✅ HybridChunker initialized with Arabic-optimized settings")
        
        # Create chunks
        chunk_iter = chunker.chunk(dl_doc=document)
        chunks = list(chunk_iter)
        
        print(f"✅ Chunking successful: {len(chunks)} chunks created")
        
        # Analyze chunks for Arabic content
        arabic_chunks = 0
        total_arabic_chars = 0
        
        for i, chunk in enumerate(chunks):
            if hasattr(chunk, 'text'):
                chunk_text = chunk.text
                arabic_char_count = sum(1 for char in chunk_text if '\u0600' <= char <= '\u06FF')
                
                if arabic_char_count > 0:
                    arabic_chunks += 1
                    total_arabic_chars += arabic_char_count
                
                # Show first few chunks as examples
                if i < 3:
                    print(f"\n📄 Chunk {i+1}:")
                    print(f"   Length: {len(chunk_text)} characters")
                    print(f"   Arabic chars: {arabic_char_count}")
                    print(f"   Preview: {chunk_text[:150]}...")
        
        print(f"\n📊 Chunk Analysis:")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Chunks with Arabic: {arabic_chunks}")
        print(f"   Total Arabic characters: {total_arabic_chars}")
        
        return chunks
        
    except Exception as e:
        print(f"❌ Chunking failed: {e}")
        print("🔄 Trying fallback chunking method...")
        
        # Fallback: manual chunking
        try:
            markdown_content = document.export_to_markdown()
            cleaned_content = clean_arabic_text(markdown_content)
            
            # Simple paragraph-based chunking
            paragraphs = [p.strip() for p in cleaned_content.split('\n\n') if p.strip()]
            
            # Create chunks from paragraphs
            chunks = []
            current_chunk = ""
            
            for paragraph in paragraphs:
                if len(current_chunk) + len(paragraph) < max_tokens * 4:  # Rough character estimate
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(type('Chunk', (), {'text': current_chunk.strip()})())
                    current_chunk = paragraph + "\n\n"
            
            if current_chunk:
                chunks.append(type('Chunk', (), {'text': current_chunk.strip()})())
            
            print(f"✅ Fallback chunking successful: {len(chunks)} chunks created")
            return chunks
            
        except Exception as fallback_error:
            print(f"❌ Fallback chunking also failed: {fallback_error}")
            return []

def validate_chunks_for_embedding(chunks):
    """Validate chunks to ensure they work with embedding model"""
    
    print("\n🔍 Validating chunks for embedding...")
    print("=" * 40)
    
    valid_chunks = []
    invalid_chunks = []
    
    for i, chunk in enumerate(chunks):
        if hasattr(chunk, 'text'):
            chunk_text = chunk.text
            
            # Check if chunk is too long for embedding
            if len(chunk_text) > 8000:  # Conservative limit for embedding
                print(f"⚠️  Chunk {i+1} too long: {len(chunk_text)} characters")
                invalid_chunks.append(i)
            else:
                valid_chunks.append(i)
    
    print(f"✅ Valid chunks: {len(valid_chunks)}")
    print(f"⚠️  Invalid chunks: {len(invalid_chunks)}")
    
    return valid_chunks, invalid_chunks

def save_chunks_to_file(chunks, filename="arabic_chunks.txt"):
    """Save chunks to a file for inspection"""
    
    print(f"\n💾 Saving chunks to {filename}...")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for i, chunk in enumerate(chunks):
                if hasattr(chunk, 'text'):
                    f.write(f"=== CHUNK {i+1} ===\n")
                    f.write(chunk.text)
                    f.write("\n\n" + "="*50 + "\n\n")
        
        print(f"✅ Chunks saved to {filename}")
        
    except Exception as e:
        print(f"❌ Failed to save chunks: {e}")

if __name__ == "__main__":
    # Process Arabic PDF
    pdf_file = "KFH_Real_Estate_Report_2025_Q1_arb.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        exit(1)
    
    # Extract document
    print("📄 Extracting Arabic PDF...")
    converter = DocumentConverter()
    result = converter.convert(pdf_file)
    
    if not result.document:
        print("❌ Failed to extract document")
        exit(1)
    
    print("✅ Document extracted successfully")
    
    # Create optimized chunks
    chunks = create_arabic_optimized_chunks(result.document)
    
    if chunks:
        # Validate chunks
        valid_indices, invalid_indices = validate_chunks_for_embedding(chunks)
        
        # Save chunks for inspection
        save_chunks_to_file(chunks)
        
        print("\n" + "=" * 60)
        print("📊 Arabic Chunking Summary")
        print("=" * 60)
        print(f"✅ Total chunks created: {len(chunks)}")
        print(f"✅ Valid chunks for embedding: {len(valid_indices)}")
        print(f"⚠️  Chunks needing adjustment: {len(invalid_indices)}")
        print(f"💾 Chunks saved to: arabic_chunks.txt")
        print("=" * 60)
        
        if invalid_indices:
            print("\n🔧 Recommendations:")
            print("   - Consider reducing MAX_TOKENS further")
            print("   - Implement chunk splitting for long chunks")
            print("   - Use more aggressive text cleaning")
    else:
        print("❌ Failed to create chunks")
