import lancedb
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

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

# Initialize LanceDB connection
def init_db():
    """Initialize database connection."""
    db = lancedb.connect("data/lancedb")
    return db.open_table("docling")

def get_context(query: str, table, num_results: int = 5) -> str:
    """Search the database for relevant context."""
    # Convert query to vector using Azure OpenAI
    query_vector = azure_openai_embedding(query)[0]
    
    # Search using vector similarity
    results = table.search(query=query_vector, query_type="vector").limit(num_results).to_pandas()
    contexts = []

    for _, row in results.iterrows():
        # Extract metadata
        filename = row["metadata"]["filename"]
        page_numbers = row["metadata"]["page_numbers"]
        title = row["metadata"]["title"]

        # Build source citation
        source_parts = []
        if filename:
            source_parts.append(filename)
        if page_numbers:
            source_parts.append(f"p. {page_numbers}")

        source = f"\nSource: {' - '.join(source_parts)}"
        if title:
            source += f"\nTitle: {title}"

        contexts.append(f"{row['text']}{source}")

    return "\n\n".join(contexts)

def get_chat_response(messages, context: str) -> str:
    """Get response from Azure OpenAI API."""
    system_prompt = f"""You are a helpful real estate analyst assistant that answers questions based on the KFH Real Estate Report 2025 Q1.
    Use only the information from the provided context to answer questions. If you're unsure or the context
    doesn't contain the relevant information, say so.
    
    Context from KFH Real Estate Report 2025 Q1:
    {context}
    
    Always provide accurate, data-driven insights based on the report content.
    """

    messages_with_context = [{"role": "system", "content": system_prompt}, *messages]

    # Create the response
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        messages=messages_with_context,
        temperature=0.7,
        max_tokens=1000,
    )

    return response.choices[0].message.content

def main():
    print("🏠 KFH Real Estate Report 2025 Q1 - Q&A Assistant")
    print("=" * 60)
    print("Ask questions about the KFH Real Estate Report and get AI-powered insights!")
    print("Type 'quit' to exit.")
    print()

    # Initialize database connection
    try:
        table = init_db()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # Chat loop
    messages = []
    
    while True:
        try:
            # Get user input
            user_input = input("\n🤔 Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Thank you for using the KFH Real Estate Assistant.")
                break
            
            if not user_input:
                continue

            print("\n🔍 Searching real estate report...")
            
            # Get relevant context
            context = get_context(user_input, table, num_results=3)
            
            print(f"📄 Found relevant sections from the report:")
            print("-" * 50)
            
            # Display context
            for i, chunk in enumerate(context.split("\n\n"), 1):
                print(f"\n{i}. {chunk[:200]}...")
            
            print("-" * 50)
            
            # Add user message to chat history
            messages.append({"role": "user", "content": user_input})
            
            print("\n🤖 Generating AI response...")
            
            # Get AI response
            response = get_chat_response(messages, context)
            
            print(f"\n💡 AI Response:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
            # Add AI response to chat history
            messages.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thank you for using the KFH Real Estate Assistant.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()
