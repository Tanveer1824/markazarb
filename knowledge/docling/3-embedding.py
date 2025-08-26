from typing import List

import lancedb
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from openai import AzureOpenAI
import os

load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

MAX_TOKENS = 8191  # text-embedding-3-large's maximum context length


# --------------------------------------------------------------
# Extract the data from local PDF
# --------------------------------------------------------------

converter = DocumentConverter()
result = converter.convert("KFH_Real_Estate_Report_2025_Q1.pdf")

print(f"Processing KFH Real Estate Report 2025 Q1")
print(f"Document extracted successfully")

# --------------------------------------------------------------
# Apply hybrid chunking with default tokenizer
# --------------------------------------------------------------

chunker = HybridChunker(
    max_tokens=MAX_TOKENS,
    merge_peers=True,
)

chunk_iter = chunker.chunk(dl_doc=result.document)
chunks = list(chunk_iter)

print(f"Created {len(chunks)} chunks from the real estate report")

# --------------------------------------------------------------
# Create a LanceDB database and table
# --------------------------------------------------------------

# Create a LanceDB database
db = lancedb.connect("data/lancedb")

# Create a custom embedding function using Azure OpenAI
def azure_openai_embedding(texts):
    """Custom embedding function using Azure OpenAI"""
    try:
        response = client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
            input=texts
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Azure OpenAI embedding error: {e}")
        raise

# Define a simplified metadata schema
class ChunkMetadata(LanceModel):
    """
    You must order the fields in alphabetical order.
    This is a requirement of the Pydantic implementation.
    """

    filename: str | None
    page_numbers: str | None  # Changed from List[int] to str for flexibility
    title: str | None

# Define the main Schema
class Chunks(LanceModel):
    text: str
    vector: Vector(3072)  # text-embedding-3-large has 3072 dimensions
    metadata: ChunkMetadata

# Force delete existing table and recreate with new schema
try:
    db.drop_table("docling")
    print("Dropped existing table")
except:
    pass

table = db.create_table("docling", schema=Chunks, mode="overwrite")
print("Created new table with updated schema")

# --------------------------------------------------------------
# Prepare the chunks for the table
# --------------------------------------------------------------

# Create table with processed chunks
processed_chunks = []
for chunk in chunks:
    # Extract page numbers more safely
    page_numbers = []
    try:
        for item in chunk.meta.doc_items:
            for prov in item.prov:
                if hasattr(prov, 'page_no') and prov.page_no is not None:
                    page_numbers.append(prov.page_no)
        # Remove duplicates and sort
        page_numbers = sorted(set(page_numbers)) if page_numbers else []
    except Exception as e:
        print(f"Warning: Could not extract page numbers for chunk: {e}")
        page_numbers = []
    
    processed_chunks.append({
        "text": chunk.text,
        "metadata": {
            "filename": "KFH_Real_Estate_Report_2025_Q1.pdf",
            "page_numbers": ", ".join(map(str, page_numbers)) if page_numbers else None,
            "title": "KFH Real Estate Report 2025 Q1",
        },
    })

# --------------------------------------------------------------
# Generate embeddings and add to the table
# --------------------------------------------------------------

print(f"Generating embeddings for {len(processed_chunks)} chunks using Azure OpenAI...")

# Process chunks in batches to avoid rate limits
batch_size = 10
all_embeddings = []

for i in range(0, len(processed_chunks), batch_size):
    batch = processed_chunks[i:i + batch_size]
    batch_texts = [chunk["text"] for chunk in batch]
    
    print(f"Processing batch {i//batch_size + 1}/{(len(processed_chunks) + batch_size - 1)//batch_size}")
    
    try:
        batch_embeddings = azure_openai_embedding(batch_texts)
        all_embeddings.extend(batch_embeddings)
        print(f"  ✅ Generated {len(batch_embeddings)} embeddings")
    except Exception as e:
        print(f"  ❌ Failed to generate embeddings for batch: {e}")
        # Add zero vectors as fallback
        all_embeddings.extend([[0.0] * 3072] * len(batch))

# Add embeddings to the chunks
for i, chunk in enumerate(processed_chunks):
    chunk["vector"] = all_embeddings[i]

print(f"Adding {len(processed_chunks)} chunks to LanceDB...")
table.add(processed_chunks)

# --------------------------------------------------------------
# Load the table and show results
# --------------------------------------------------------------

df = table.to_pandas()
print(f"Database created successfully!")
print(f"Total rows: {table.count_rows()}")
print(f"Sample data:")
print(df.head(3)[['text', 'metadata']])
