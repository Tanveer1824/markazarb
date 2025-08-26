import streamlit as st
import lancedb
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Azure OpenAI client
def init_azure_client():
    """Initialize Azure OpenAI client with error handling"""
    try:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not api_key or not endpoint:
            st.error("❌ Azure OpenAI credentials not found!")
            st.info("Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in your .env file")
            return None
            
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize Azure OpenAI client: {e}")
        return None

# Initialize the client
client = init_azure_client()

def azure_openai_embedding(texts):
    """Custom embedding function using Azure OpenAI"""
    if client is None:
        st.error("❌ Azure OpenAI client not initialized")
        return None
        
    if isinstance(texts, str):
        texts = [texts]
    
    try:
        response = client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
            input=texts
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        st.error(f"Azure OpenAI embedding error: {e}")
        return None

# Initialize LanceDB connection
@st.cache_resource
def init_db():
    """Initialize database connection.

    Returns:
        LanceDB table object or None if connection fails
    """
    try:
        # Check if we're running in Streamlit Cloud or local
        import os
        current_dir = os.getcwd()
        st.info(f"Current working directory: {current_dir}")
        
        # Try multiple possible database paths
        possible_paths = [
            "data/lancedb",
            "knowledge/docling/data/lancedb",
            "/mount/src/markazarb/knowledge/docling/data/lancedb"
        ]
        
        db = None
        for db_path in possible_paths:
            try:
                if os.path.exists(db_path):
                    st.success(f"Found database at: {db_path}")
                    db = lancedb.connect(db_path)
                    # Check if the table exists
                    tables = db.table_names()
                    if "docling" in tables:
                        st.success(f"Found table 'docling' in database")
                        return db.open_table("docling")
                    else:
                        st.warning(f"Table 'docling' not found. Available tables: {tables}")
                        db.close()
                else:
                    st.info(f"Database path not found: {db_path}")
            except Exception as e:
                st.warning(f"Failed to connect to {db_path}: {e}")
                continue
        
        # If no database found, show error and return None
        st.error("❌ No valid database found. Please ensure the database is properly set up.")
        st.info("For local development, run the extraction and embedding scripts first.")
        st.info("For cloud deployment, ensure the database files are included in the repository.")
        return None
        
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None


def get_context(query: str, table, num_results: int = 5) -> str:
    """Search the database for relevant context.

    Args:
        query: User's question
        table: LanceDB table object
        num_results: Number of results to return

    Returns:
        str: Concatenated context from relevant chunks with source information
    """
    # Convert query to vector using Azure OpenAI
    query_vector = azure_openai_embedding(query)
    if query_vector is None:
        return "❌ Failed to generate embeddings. Please check your Azure OpenAI configuration."
    
    # Search using vector similarity
    try:
        results = table.search(query=query_vector[0], query_type="vector").limit(num_results).to_pandas()
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
                source_parts.append(f"p. {', '.join(str(p) for p in page_numbers)}")

            source = f"\nSource: {' - '.join(source_parts)}"
            if title:
                source += f"\nTitle: {title}"

            contexts.append(f"{row['text']}{source}")

        return "\n\n".join(contexts)
    except Exception as e:
        st.error(f"Database search error: {e}")
        return f"❌ Error searching database: {e}"


def get_chat_response(messages, context: str) -> str:
    """Get streaming response from Azure OpenAI API.

    Args:
        messages: Chat history
        context: Retrieved context from database

    Returns:
        str: Model's response
    """
    if client is None:
        return "❌ Azure OpenAI client not initialized. Please check your configuration."
    
    system_prompt = f"""You are a helpful real estate analyst assistant that answers questions based on the KFH Real Estate Report 2025 Q1.
    Use only the information from the provided context to answer questions. If you're unsure or the context
    doesn't contain the relevant information, say so.
    
    Context from KFH Real Estate Report 2025 Q1:
    {context}
    
    Always provide accurate, data-driven insights based on the report content.
    """

    messages_with_context = [{"role": "system", "content": system_prompt}, *messages]

    try:
        # Create the streaming response
        stream = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=messages_with_context,
            temperature=0.7,
            stream=True,
        )

        # Use Streamlit's built-in streaming capability
        response = st.write_stream(stream)
        return response
    except Exception as e:
        st.error(f"Chat completion error: {e}")
        return f"❌ Error generating response: {e}"


# Initialize Streamlit app
st.title("🏠 KFH Real Estate Report 2025 Q1 - Q&A Assistant")
st.markdown("Ask questions about the KFH Real Estate Report and get AI-powered insights!")

# Check environment configuration
def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        st.error("❌ Missing required environment variables:")
        for var in missing_vars:
            st.code(f"{var} = your_value_here")
        st.info("Please set these variables in your .env file or Streamlit Cloud secrets")
        return False
    
    st.success("✅ All required environment variables are set")
    return True

# Check environment before proceeding
if not check_environment():
    st.stop()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize database connection
table = init_db()

# Check if database connection was successful
if table is None:
    st.error("🚫 Database Connection Failed")
    st.markdown("""
    ### Setup Required
    
    This application requires a LanceDB database with processed document chunks. 
    
    **For Local Development:**
    1. Run `1-extraction.py` to extract text from PDFs
    2. Run `2-chunking.py` to create document chunks  
    3. Run `3-embedding.py` to generate embeddings
    4. Restart this application
    
    **For Cloud Deployment:**
    - Ensure the `data/lancedb` directory is included in your repository
    - Or set up a cloud database connection
    
    **Alternative:**
    You can still explore the interface, but chat functionality will be limited.
    """)
    
    # Show a demo mode
    st.info("🔄 Demo Mode: You can explore the interface, but chat is disabled")
    
    # Initialize empty chat history for demo
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    if st.session_state.messages:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Disable chat input in demo mode
    st.chat_input("Chat disabled - Database not available", disabled=True)
    
    # Show sidebar with demo info
    with st.sidebar:
        st.header("📊 Report Overview")
        st.info("This is a demo mode. Database connection required for full functionality.")
        st.markdown("""
        - Market trends and analysis
        - Property valuations
        - Investment opportunities
        - Regional market insights
        - Economic indicators
        - Future projections
        """)
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    st.stop()

# Display chat messages
if st.session_state.messages:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the real estate report..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get relevant context
    with st.status("🔍 Searching real estate report...", expanded=False) as status:
        context = get_context(prompt, table)
        st.markdown(
            """
            <style>
            .search-result {
                margin: 10px 0;
                padding: 10px;
                border-radius: 4px;
                background-color: #f0f2f6;
            }
            .search-result summary {
                cursor: pointer;
                color: #0f52ba;
                font-weight: 500;
            }
            .search-result summary:hover {
                color: #1e90ff;
            }
            .metadata {
                font-size: 0.9em;
                color: #666;
                font-style: italic;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        st.write("📄 Found relevant sections from the report:")
        for chunk in context.split("\n\n"):
            # Split into text and metadata parts
            parts = chunk.split("\n")
            text = parts[0]
            metadata = {
                line.split(": ")[0]: line.split(": ")[1]
                for line in parts[1:]
                if ": " in line
            }

            source = metadata.get("Source", "Unknown source")
            title = metadata.get("Title", "KFH Real Estate Report 2025 Q1")

            st.markdown(
                f"""
                <div class="search-result">
                    <details>
                        <summary>{source}</summary>
                        <div class="metadata">Section: {title}</div>
                        <div style="margin-top: 8px;">{text}</div>
                    </details>
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Display assistant response first
    with st.chat_message("assistant"):
        # Get model response with streaming
        response = get_chat_response(st.session_state.messages, context)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with helpful information
with st.sidebar:
    st.header("📊 Report Overview")
    st.info("This assistant can help you with questions about:")
    st.markdown("""
    - Market trends and analysis
    - Property valuations
    - Investment opportunities
    - Regional market insights
    - Economic indicators
    - Future projections
    """)
    
    st.header("💡 Sample Questions")
    st.markdown("""
    - "What are the key market trends for 2025?"
    - "How are property prices performing?"
    - "What investment opportunities are highlighted?"
    - "What's the outlook for residential vs commercial?"
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
