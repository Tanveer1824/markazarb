from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Test Azure OpenAI connection
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

print("Testing Azure OpenAI connection...")
print(f"Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
print(f"Chat Model: {os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME', 'Not configured')}")
print(f"Embedding Model: {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME', 'Not configured')}")
print(f"API Version: {os.getenv('AZURE_OPENAI_API_VERSION')}")

try:
    # Test chat completion if chat model is configured
    chat_model = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
    if chat_model:
        response = client.chat.completions.create(
            model=chat_model,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print("✅ Chat completion test successful!")
        print(f"Response: {response.choices[0].message.content}")
    else:
        print("⚠️  Chat completion test skipped - no chat model configured")
    
    # Test embeddings if embedding model is configured
    embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
    if embedding_model:
        embedding_response = client.embeddings.create(
            model=embedding_model,
            input=["test text"]
        )
        print("✅ Embedding test successful!")
        print(f"Embedding dimensions: {len(embedding_response.data[0].embedding)}")
    else:
        print("⚠️  Embedding test skipped - no embedding model configured")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
