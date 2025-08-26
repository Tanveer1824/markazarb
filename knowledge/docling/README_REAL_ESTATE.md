# KFH Real Estate Report 2025 Q1 - AI Analysis Setup

This setup processes the KFH Real Estate Report 2025 Q1 PDF and creates an AI-powered Q&A system using Azure OpenAI and LanceDB.

## 🏠 What's Included

- **PDF Processing**: Extract and chunk the KFH Real Estate Report
- **Vector Database**: Store embeddings in LanceDB for semantic search
- **AI Chat Interface**: Streamlit-based Q&A system powered by Azure OpenAI
- **Real Estate Focus**: Specialized for real estate market analysis queries

## 📋 Prerequisites

1. **Azure OpenAI Setup**:
   - Azure OpenAI resource with deployed models
   - API key and endpoint URL
   - Model deployment name

2. **Environment Variables**:
   Create a `.env` file in the `knowledge/docling` directory:
   ```bash
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
   ```

3. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Step 1: Extract and Process the PDF
```bash
cd knowledge/docling
python 1-extraction.py
```

### Step 2: Create Chunks
```bash
python 2-chunking.py
```

### Step 3: Generate Embeddings and Store in Database
```bash
python 3-embedding.py
```

### Step 4: Test Search Functionality
```bash
python 4-search.py
```

### Step 5: Launch Chat Interface
```bash
streamlit run 5-chat.py
```

## 📊 What Each Script Does

### `1-extraction.py`
- Extracts text content from `KFH_Real_Estate_Report_2025_Q1.pdf`
- Converts to markdown and JSON formats
- Shows preview of extracted content

### `2-chunking.py`
- Splits the document into manageable chunks
- Uses hybrid chunking strategy for optimal text segmentation
- Configures Azure OpenAI client for processing

### `3-embedding.py`
- Creates vector embeddings for each text chunk
- Stores data in LanceDB with metadata
- Includes filename, page numbers, and section titles

### `4-search.py`
- Demonstrates semantic search capabilities
- Shows example queries for real estate topics
- Displays search results with source information

### `5-chat.py`
- Interactive Streamlit chat interface
- Real-time Q&A about the real estate report
- Context-aware responses using retrieved information

## 🎯 Sample Queries

The system is optimized for real estate analysis questions:

- **Market Analysis**: "What are the key market trends for 2025?"
- **Property Values**: "How are property prices performing?"
- **Investment**: "What investment opportunities are highlighted?"
- **Regional Insights**: "What's the outlook for different regions?"
- **Economic Factors**: "How do economic indicators affect the market?"

## 🗄️ Database Schema

The LanceDB table stores:
- **text**: The actual content chunk
- **vector**: Embedding vector for semantic search
- **metadata**: 
  - filename: "KFH_Real_Estate_Report_2025_Q1.pdf"
  - page_numbers: List of source pages
  - title: Section heading or "KFH Real Estate Report 2025 Q1"

## 🔧 Configuration Options

### Chunking Parameters
- `MAX_TOKENS`: 8191 (for text-embedding-3-large)
- `merge_peers`: True (combines related chunks)
- `tokenizer`: OpenAI-compatible tokenizer

### Search Parameters
- `num_results`: 5 (default search results)
- `query_type`: "vector" (semantic search)

### Azure OpenAI Settings
- API version: 2024-02-15-preview
- Temperature: 0.7 (balanced creativity/accuracy)
- Streaming: Enabled for real-time responses

## 📁 File Structure

```
knowledge/docling/
├── KFH_Real_Estate_Report_2025_Q1.pdf    # Source PDF
├── 1-extraction.py                        # PDF extraction
├── 2-chunking.py                          # Text chunking
├── 3-embedding.py                         # Vector embeddings
├── 4-search.py                            # Search examples
├── 5-chat.py                              # Chat interface
├── requirements.txt                        # Dependencies
├── utils/                                  # Utility functions
└── data/lancedb/                          # Vector database
```

## 🚨 Troubleshooting

### Common Issues

1. **PDF Not Found**: Ensure `KFH_Real_Estate_Report_2025_Q1.pdf` is in the same directory
2. **Azure OpenAI Errors**: Check environment variables and API configuration
3. **Database Errors**: Ensure LanceDB can create/write to `data/lancedb` directory
4. **Memory Issues**: Large PDFs may require more RAM for processing

### Debug Tips

- Check console output for detailed error messages
- Verify PDF file is readable and not corrupted
- Test Azure OpenAI connection separately
- Monitor memory usage during processing

## 🔄 Updating the Report

To use a different real estate report:

1. Replace the PDF file
2. Update filename references in scripts
3. Re-run the extraction and embedding pipeline
4. Update the chat interface title and descriptions

## 📈 Performance Considerations

- **Processing Time**: Large PDFs may take several minutes
- **Storage**: Vector database size depends on document length
- **Search Speed**: LanceDB provides fast vector similarity search
- **Memory**: Keep chunk sizes reasonable for optimal performance

## 🎉 Next Steps

After setup, you can:
- Customize the chat interface for specific use cases
- Add more real estate reports to the knowledge base
- Integrate with external data sources
- Deploy the chat interface as a web service
- Add user authentication and usage tracking

## 📚 Additional Resources

- [LanceDB Documentation](https://lancedb.github.io/lancedb/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Docling Documentation](https://ds4sd.github.io/docling/)
