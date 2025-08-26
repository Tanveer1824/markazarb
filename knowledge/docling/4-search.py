import lancedb
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------
# Initialize Azure OpenAI client for embeddings
# --------------------------------------------------------------

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# --------------------------------------------------------------
# Custom embedding function for LanceDB
# --------------------------------------------------------------

def azure_openai_embedding(texts):
    """Custom embedding function using Azure OpenAI"""
    if isinstance(texts, str):
        texts = [texts]
    
    try:
        response = client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
            input=texts
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Azure OpenAI embedding error: {e}")
        raise

# --------------------------------------------------------------
# Connect to the database
# --------------------------------------------------------------

uri = "data/lancedb"
db = lancedb.connect(uri)

# --------------------------------------------------------------
# Load the table and register embedding function
# --------------------------------------------------------------

table = db.open_table("docling")

# Note: We'll use the embedding function directly in search calls

# --------------------------------------------------------------
# Search the table with real estate specific queries
# --------------------------------------------------------------

print("🔍 Searching KFH Real Estate Report 2025 Q1")
print("=" * 50)

# Example 1: Market overview
print("\n1. Market Overview Query:")
query_vector = azure_openai_embedding("market overview trends 2025")[0]
result1 = table.search(query=query_vector, query_type="vector").limit(3)
df1 = result1.to_pandas()
if not df1.empty:
    for idx, row in df1.iterrows():
        print(f"   - {row['text'][:150]}...")
        print(f"     Source: {row['metadata']['filename']} - Page: {row['metadata']['page_numbers']}")
        print()

# Example 2: Property prices
print("\n2. Property Prices Query:")
query_vector = azure_openai_embedding("property prices valuation market")[0]
result2 = table.search(query=query_vector, query_type="vector").limit(3)
df2 = result2.to_pandas()
if not df2.empty:
    for idx, row in df2.iterrows():
        print(f"   - {row['text'][:150]}...")
        print(f"     Source: {row['metadata']['filename']} - Page: {row['metadata']['page_numbers']}")
        print()

# Example 3: Investment opportunities
print("\n3. Investment Opportunities Query:")
query_vector = azure_openai_embedding("investment opportunities real estate")[0]
result3 = table.search(query=query_vector, query_type="vector").limit(3)
df3 = result3.to_pandas()
if not df3.empty:
    for idx, row in df3.iterrows():
        print(f"   - {row['text'][:150]}...")
        print(f"     Source: {row['metadata']['filename']} - Page: {row['metadata']['page_numbers']}")
        print()

print("=" * 50)
print(f"Total documents in database: {table.count_rows()}")
