from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
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

# Check document structure safely
print(f"Document extracted successfully")
print(f"Document object type: {type(result.document)}")

# Try to get document info safely
if hasattr(result.document, 'pages'):
    print(f"Number of pages: {len(result.document.pages)}")
else:
    print("Document doesn't have pages attribute")

# Try to export to see what's available
try:
    markdown_content = result.document.export_to_markdown()
    print(f"Document content length: {len(markdown_content)} characters")
    print(f"Content preview: {markdown_content[:200]}...")
except Exception as e:
    print(f"Could not export to markdown: {e}")
    print(f"Available attributes: {[attr for attr in dir(result.document) if not attr.startswith('_')]}")

# --------------------------------------------------------------
# Apply hybrid chunking with default tokenizer
# --------------------------------------------------------------

try:
    # Use the default tokenizer that comes with docling
    chunker = HybridChunker(
        max_tokens=MAX_TOKENS,
        merge_peers=True,
    )
    
    chunk_iter = chunker.chunk(dl_doc=result.document)
    chunks = list(chunk_iter)
    
    print(f"Created {len(chunks)} chunks from the real estate report")
    if chunks:
        # Check what attributes the chunks have
        first_chunk = chunks[0]
        print(f"First chunk type: {type(first_chunk)}")
        print(f"First chunk attributes: {[attr for attr in dir(first_chunk) if not attr.startswith('_')]}")
        
        # Try to access text content safely
        if hasattr(first_chunk, 'text'):
            print(f"First chunk preview: {first_chunk.text[:200]}...")
        elif hasattr(first_chunk, 'content'):
            print(f"First chunk preview: {first_chunk.content[:200]}...")
        else:
            print("Chunk created but no text/content attribute found")
    else:
        print("No chunks created")
        
except Exception as e:
    print(f"Chunking failed: {e}")
    print("Trying alternative chunking approach...")
    
    # Fallback: try simple text splitting
    try:
        markdown_content = result.document.export_to_markdown()
        # Simple chunking by paragraphs
        paragraphs = markdown_content.split('\n\n')
        print(f"Simple chunking created {len(paragraphs)} paragraph chunks")
        print(f"First paragraph: {paragraphs[0][:200]}...")
    except Exception as fallback_error:
        print(f"Fallback chunking also failed: {fallback_error}")
