#!/usr/bin/env python3
"""
Enhanced Arabic Chat Interface
Supports both Arabic and English queries with proper Arabic text handling
"""

import streamlit as st
import lancedb
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def clean_arabic_text(text):
    """Clean and normalize Arabic text"""
    # Remove common PDF artifacts
    text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}\"\']+', ' ', text)
    
    # Normalize Arabic text
    text = re.sub(r'[ـ]+', '', text)  # Remove tatweel (stretching)
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    return text

def detect_language(text):
    """Detect if text contains Arabic characters"""
    arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
    return "Arabic" if arabic_chars > 0 else "English"

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

# Initialize LanceDB connection for Arabic content
@st.cache_resource
def init_arabic_db():
    """Initialize Arabic database connection"""
    try:
        db = lancedb.connect("data/arabic_lancedb")
        return db.open_table("arabic_chunks")
    except Exception as e:
        st.error(f"Failed to connect to Arabic database: {e}")
        return None

def get_arabic_context(query: str, table, num_results: int = 5) -> str:
    """Search the Arabic database for relevant context"""
    
    if not table:
        return "Database connection failed"
    
    try:
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
            language = row["metadata"]["language"]
            arabic_char_count = row["metadata"]["arabic_char_count"]
            chunk_quality = row["metadata"]["chunk_quality"]

            # Build source citation
            source_parts = []
            if filename:
                source_parts.append(filename)
            if page_numbers:
                source_parts.append(f"p. {page_numbers}")
            if language:
                source_parts.append(f"Lang: {language}")
            if chunk_quality:
                source_parts.append(f"Quality: {chunk_quality}")

            source = f"\nSource: {' - '.join(source_parts)}"
            if title:
                source += f"\nTitle: {title}"

            contexts.append(f"{row['text']}{source}")

        return "\n\n".join(contexts)
        
    except Exception as e:
        st.error(f"Search failed: {e}")
        return ""

def get_arabic_chat_response(messages, context: str, query_language: str) -> str:
    """Get streaming response from Azure OpenAI API with Arabic support"""
    
    # Create language-appropriate system prompt
    if query_language == "Arabic":
        system_prompt = f"""أنت مساعد ذكي متخصص في تحليل التقارير العقارية. أجب على الأسئلة بناءً على المعلومات المقدمة في السياق.
        استخدم فقط المعلومات من السياق المقدم للإجابة على الأسئلة. إذا لم تكن متأكداً أو لم يحتوي السياق على المعلومات ذات الصلة، قل ذلك.
        
        السياق من تقرير KFH العقاري 2025 Q1:
        {context}
        
        تذكر أن تجيب باللغة العربية إذا كان السؤال بالعربية."""
    else:
        system_prompt = f"""You are a helpful real estate analyst assistant that answers questions based on the KFH Real Estate Report 2025 Q1.
        Use only the information from the provided context to answer questions. If you're unsure or the context
        doesn't contain the relevant information, say so.
        
        Context from KFH Real Estate Report 2025 Q1:
        {context}
        
        Remember to respond in the same language as the user's query."""
    
    try:
        # Check if chat model is configured
        chat_model = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        if not chat_model:
            return "Chat model not configured. Please set AZURE_OPENAI_CHAT_DEPLOYMENT_NAME in your environment."
        
        response = client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ],
            temperature=0.7,
            max_tokens=1000,
            stream=False
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error getting response: {e}"

def main():
    st.set_page_config(
        page_title="Arabic Real Estate Chat",
        page_icon="🏠",
        layout="wide"
    )
    
    st.title("🏠 Arabic Real Estate Chat Assistant")
    st.markdown("**Chat with KFH Real Estate Report 2025 Q1 (Arabic Version)**")
    
    # Initialize database
    table = init_arabic_db()
    
    if not table:
        st.error("❌ Failed to connect to Arabic database. Please run the embedding script first.")
        st.info("Run: `python 3-embedding-arabic.py` to create the database.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Language selection
        language = st.selectbox(
            "🌐 Interface Language",
            ["English", "Arabic"],
            index=0
        )
        
        # Number of search results
        num_results = st.slider(
            "🔍 Number of search results",
            min_value=1,
            max_value=10,
            value=5
        )
        
        # Database info
        st.header("📊 Database Info")
        try:
            # Get table info
            table_info = table.to_pandas()
            st.write(f"**Total chunks:** {len(table_info)}")
            
            # Count Arabic chunks
            arabic_chunks = sum(1 for _, row in table_info.iterrows() 
                              if row['metadata']['language'] == 'Arabic')
            st.write(f"**Arabic chunks:** {arabic_chunks}")
            
            # Show quality distribution
            quality_counts = table_info['metadata'].apply(lambda x: x['chunk_quality']).value_counts()
            st.write("**Chunk quality:**")
            for quality, count in quality_counts.items():
                st.write(f"  - {quality}: {count}")
                
        except Exception as e:
            st.write(f"Database info unavailable: {e}")
    
    # Main chat interface
    st.header("💬 Chat with the Report")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about the real estate report..."):
        # Detect query language
        query_language = detect_language(prompt)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Show language detection
        lang_emoji = "🇸🇦" if query_language == "Arabic" else "🇺🇸"
        st.info(f"{lang_emoji} Detected language: {query_language}")
        
        # Get context from database
        with st.spinner("🔍 Searching database..."):
            context = get_arabic_context(prompt, table, num_results)
        
        if context:
            # Display context
            with st.expander("📚 Retrieved Context", expanded=False):
                st.markdown(context)
        
        # Get AI response
        with st.spinner("🤖 Generating response..."):
            response = get_arabic_chat_response(st.session_state.messages, context, query_language)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("**Powered by Azure OpenAI + Docling + LanceDB**")
    
    # Show database path
    st.caption(f"Database: `data/arabic_lancedb/arabic_chunks`")

if __name__ == "__main__":
    main()
