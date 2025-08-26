#!/usr/bin/env python3
"""
Arabic Text Embedding with Enhanced Language Support
Creates and stores embeddings for Arabic text chunks in LanceDB
"""

from typing import List
import lancedb
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from lancedb.pydantic import LanceModel, Vector
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

# Optimized token limit for Arabic text
MAX_TOKENS = 4000

def clean_arabic_text(text):
    """Clean and normalize Arabic text for better embedding"""
    # Remove common PDF artifacts
    text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}\"\']+', ' ', text)
    
    # Normalize Arabic text
    text = re.sub(r'[ـ]+', '', text)  # Remove tatweel (stretching)
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    return text

def create_arabic_optimized_chunks(document):
    """Create chunks optimized for Arabic text"""
    
    print(f"🔍 Creating Arabic-optimized chunks (max tokens: {MAX_TOKENS})")
    
    try:
        chunker = HybridChunker(
            max_tokens=MAX_TOKENS,
            merge_peers=True,
            min_tokens=100,
        )
        
        chunk_iter = chunker.chunk(dl_doc=document)
        chunks = list(chunk_iter)
        
        print(f"✅ Chunking successful: {len(chunks)} chunks created")
        return chunks
        
    except Exception as e:
        print(f"❌ Chunking failed: {e}")
        return []

def azure_openai_embedding(texts):
    """Custom embedding function using Azure OpenAI with Arabic text support"""
    if isinstance(texts, str):
        texts = [texts]
    
    try:
        # Clean Arabic text before embedding
        cleaned_texts = [clean_arabic_text(text) for text in texts]
        
        response = client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
            input=cleaned_texts
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Azure OpenAI embedding error: {e}")
        raise

# Define enhanced metadata schema for Arabic documents
class ArabicChunkMetadata(LanceModel):
    """Enhanced metadata for Arabic document chunks"""
    
    filename: str | None
    page_numbers: str | None
    title: str | None
    language: str = "Arabic"  # Default to Arabic
    arabic_char_count: int | None
    chunk_quality: str | None  # "high", "medium", "low"

# Define the main Schema for Arabic chunks
class ArabicChunks(LanceModel):
    text: str
    vector: Vector(3072)  # text-embedding-3-large has 3072 dimensions
    metadata: ArabicChunkMetadata

def process_arabic_pdf_for_embedding(pdf_path):
    """Process Arabic PDF and create embeddings"""
    
    print(f"🔍 Processing Arabic PDF: {pdf_path}")
    print("=" * 60)
    
    # Extract document
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    
    if not result.document:
        print("❌ Failed to extract document")
        return None
    
    print("✅ Document extracted successfully")
    
    # Create optimized chunks
    chunks = create_arabic_optimized_chunks(result.document)
    
    if not chunks:
        print("❌ Failed to create chunks")
        return None
    
    # Analyze chunks for Arabic content
    arabic_chunks = 0
    total_arabic_chars = 0
    
    for chunk in chunks:
        if hasattr(chunk, 'text'):
            chunk_text = chunk.text
            arabic_char_count = sum(1 for char in chunk_text if '\u0600' <= char <= '\u06FF')
            
            if arabic_char_count > 0:
                arabic_chunks += 1
                total_arabic_chars += arabic_char_count
    
    print(f"📊 Chunk Analysis:")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Chunks with Arabic: {arabic_chunks}")
    print(f"   Total Arabic characters: {total_arabic_chars}")
    
    return chunks

def create_arabic_database():
    """Create LanceDB database for Arabic content"""
    
    print("\n🗄️  Creating LanceDB database for Arabic content...")
    
    # Create database directory
    db_path = "data/arabic_lancedb"
    os.makedirs(db_path, exist_ok=True)
    
    # Connect to database
    db = lancedb.connect(db_path)
    
    # Force delete existing table and recreate with new schema
    try:
        db.drop_table("arabic_chunks")
        print("🗑️  Dropped existing table")
    except:
        pass
    
    # Create new table with Arabic-optimized schema
    table = db.create_table("arabic_chunks", schema=ArabicChunks, mode="overwrite")
    print("✅ Created new table with Arabic-optimized schema")
    
    return db, table

def store_arabic_chunks_with_embeddings(chunks, table):
    """Store Arabic chunks with embeddings in LanceDB"""
    
    print(f"\n💾 Storing {len(chunks)} Arabic chunks with embeddings...")
    print("=" * 50)
    
    processed_chunks = []
    successful_embeddings = 0
    failed_embeddings = 0
    
    for i, chunk in enumerate(chunks):
        if hasattr(chunk, 'text'):
            chunk_text = chunk.text
            
            # Skip empty chunks
            if not chunk_text.strip():
                continue
            
            try:
                # Generate embedding
                embedding = azure_openai_embedding([chunk_text])[0]
                
                # Count Arabic characters
                arabic_char_count = sum(1 for char in chunk_text if '\u0600' <= char <= '\u06FF')
                
                # Determine chunk quality
                if arabic_char_count > 100:
                    chunk_quality = "high"
                elif arabic_char_count > 50:
                    chunk_quality = "medium"
                else:
                    chunk_quality = "low"
                
                # Create chunk data
                chunk_data = {
                    "text": chunk_text,
                    "vector": embedding,
                    "metadata": {
                        "filename": "KFH_Real_Estate_Report_2025_Q1_arb.pdf",
                        "page_numbers": f"chunk_{i+1}",
                        "title": "KFH Real Estate Report 2025 Q1 (Arabic)",
                        "language": "Arabic",
                        "arabic_char_count": arabic_char_count,
                        "chunk_quality": chunk_quality
                    }
                }
                
                processed_chunks.append(chunk_data)
                successful_embeddings += 1
                
                if (i + 1) % 10 == 0:
                    print(f"   ✅ Processed {i + 1}/{len(chunks)} chunks")
                
            except Exception as e:
                print(f"❌ Failed to process chunk {i+1}: {e}")
                failed_embeddings += 1
    
    # Insert all chunks into the table
    if processed_chunks:
        try:
            table.add(processed_chunks)
            print(f"✅ Successfully stored {len(processed_chunks)} chunks in database")
        except Exception as e:
            print(f"❌ Failed to store chunks in database: {e}")
            return False
    
    print(f"\n📊 Embedding Summary:")
    print(f"   ✅ Successful embeddings: {successful_embeddings}")
    print(f"   ❌ Failed embeddings: {failed_embeddings}")
    print(f"   💾 Total stored: {len(processed_chunks)}")
    
    return True

def test_arabic_search(table):
    """Test Arabic text search functionality"""
    
    print("\n🔍 Testing Arabic text search...")
    print("=" * 40)
    
    try:
        # Test search with Arabic query
        test_query = "التقرير العقاري"
        print(f"🔍 Test query: {test_query}")
        
        # Generate embedding for test query
        query_embedding = azure_openai_embedding([test_query])[0]
        
        # Search database
        results = table.search(query=query_embedding, query_type="vector").limit(3).to_pandas()
        
        print(f"✅ Search successful: {len(results)} results found")
        
        # Show results
        for i, (_, row) in enumerate(results.iterrows()):
            print(f"\n📄 Result {i+1}:")
            print(f"   Text preview: {row['text'][:200]}...")
            print(f"   Arabic chars: {row['metadata']['arabic_char_count']}")
            print(f"   Quality: {row['metadata']['chunk_quality']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

if __name__ == "__main__":
    # Process Arabic PDF
    pdf_file = "KFH_Real_Estate_Report_2025_Q1_arb.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        exit(1)
    
    # Process PDF and create chunks
    chunks = process_arabic_pdf_for_embedding(pdf_file)
    
    if chunks:
        # Create database
        db, table = create_arabic_database()
        
        # Store chunks with embeddings
        success = store_arabic_chunks_with_embeddings(chunks, table)
        
        if success:
            # Test search functionality
            test_arabic_search(table)
            
            print("\n" + "=" * 60)
            print("🎉 Arabic PDF Processing Complete!")
            print("=" * 60)
            print(f"✅ PDF processed: {pdf_file}")
            print(f"✅ Chunks created: {len(chunks)}")
            print(f"✅ Database: data/arabic_lancedb")
            print(f"✅ Table: arabic_chunks")
            print("=" * 60)
        else:
            print("❌ Failed to store chunks in database")
    else:
        print("❌ Failed to process Arabic PDF")
