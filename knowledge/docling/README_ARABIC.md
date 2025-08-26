# Arabic PDF Processing System 🏠🇸🇦

This system provides comprehensive Arabic PDF processing capabilities with enhanced language support, optimized chunking, and a bilingual chat interface.

## 🌟 Features

- **Arabic PDF Support**: Native support for Arabic text extraction and processing
- **Enhanced Text Cleaning**: Removes PDF artifacts and normalizes Arabic text
- **Optimized Chunking**: Arabic-aware text chunking with proper token limits
- **Bilingual Chat**: Support for both Arabic and English queries
- **Vector Database**: LanceDB storage with Arabic-optimized metadata
- **Quality Assessment**: Automatic chunk quality scoring based on Arabic content

## 📋 Prerequisites

### 1. Environment Variables
Create a `.env` file with the following variables:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Model Deployment Names
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your-chat-deployment-name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your-embedding-deployment-name
```

### 2. Dependencies
```bash
pip install -r requirements.txt
```

### 3. Arabic PDF
Place your Arabic PDF file in the directory (e.g., `KFH_Real_Estate_Report_2025_Q1_arb.pdf`)

## 🚀 Quick Start

### Option 1: Run Complete Pipeline (Recommended)
```bash
python test_arabic_pipeline.py
```

This will run all steps automatically and provide a comprehensive report.

### Option 2: Run Steps Manually

#### Step 1: Extract Arabic PDF
```bash
python 1-extraction-arabic.py
```
- Extracts text from Arabic PDF
- Cleans and normalizes Arabic text
- Saves cleaned content to `arabic_content_cleaned.md`
- Provides detailed analysis of Arabic content

#### Step 2: Create Optimized Chunks
```bash
python 2-chunking-arabic.py
```
- Creates Arabic-optimized text chunks
- Uses reduced token limits (4000) to avoid token length issues
- Saves chunks to `arabic_chunks.txt` for inspection
- Validates chunks for embedding compatibility

#### Step 3: Generate Embeddings & Store
```bash
python 3-embedding-arabic.py
```
- Generates embeddings for Arabic text chunks
- Stores in LanceDB with enhanced metadata
- Creates database at `data/arabic_lancedb`
- Tests search functionality

#### Step 4: Launch Chat Interface
```bash
streamlit run 5-chat-arabic.py
```
- Bilingual chat interface (Arabic/English)
- Automatic language detection
- Real-time search and response generation
- Database statistics and quality metrics

## 🔧 Technical Details

### Arabic Text Processing

#### Text Cleaning
- Removes PDF artifacts and encoding issues
- Normalizes Arabic text (removes tatweel, normalizes whitespace)
- Preserves Arabic Unicode ranges (U+0600-U+06FF, U+0750-U+077F, etc.)

#### Chunking Strategy
- **Hybrid Chunker**: Combines hierarchical and token-based chunking
- **Token Limits**: Reduced to 4000 tokens to avoid model limitations
- **Quality Control**: Minimum chunk size of 100 tokens
- **Fallback**: Manual paragraph-based chunking if automatic fails

#### Embedding Optimization
- Arabic text cleaning before embedding generation
- Enhanced metadata schema with language and quality information
- Chunk quality scoring (high/medium/low based on Arabic content)

### Database Schema

```python
class ArabicChunkMetadata(LanceModel):
    filename: str | None
    page_numbers: str | None
    title: str | None
    language: str = "Arabic"
    arabic_char_count: int | None
    chunk_quality: str | None

class ArabicChunks(LanceModel):
    text: str
    vector: Vector(3072)  # text-embedding-3-large
    metadata: ArabicChunkMetadata
```

### Language Detection

The system automatically detects query language:
- **Arabic**: Contains Arabic Unicode characters (U+0600-U+06FF)
- **English**: No Arabic characters detected

## 📊 Performance Metrics

### Chunk Analysis
- Total chunks created
- Chunks with Arabic content
- Total Arabic characters
- Chunk quality distribution

### Quality Scoring
- **High**: >100 Arabic characters
- **Medium**: 50-100 Arabic characters  
- **Low**: <50 Arabic characters

### Database Statistics
- Total chunks stored
- Arabic chunks count
- Quality distribution
- Search performance metrics

## 🧪 Testing

### Comprehensive Test
```bash
python test_arabic_pipeline.py
```

### Individual Component Tests
```bash
# Test Arabic PDF processing
python test_arabic_pdf.py

# Test Azure connection
python test_azure_connection.py
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Token Length Warnings
**Problem**: "Token indices sequence length is longer than the specified maximum sequence length"
**Solution**: The system automatically reduces token limits to 4000 for Arabic text

#### 2. Arabic Text Encoding Issues
**Problem**: Arabic text appears as characters
**Solution**: The enhanced text cleaning automatically handles encoding issues

#### 3. Database Connection Failed
**Problem**: "Failed to connect to Arabic database"
**Solution**: Run the embedding script first: `python 3-embedding-arabic.py`

#### 4. Chat Model Not Configured
**Problem**: "Chat model not configured"
**Solution**: Set `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` in your `.env` file

### Performance Optimization

#### For Large Arabic PDFs
- Increase chunk size limits in chunking scripts
- Use more aggressive text cleaning
- Implement parallel processing for embeddings

#### For Better Search Results
- Adjust `num_results` parameter in chat interface
- Fine-tune chunk quality thresholds
- Implement semantic search filters

## 📁 Output Files

After running the pipeline, you'll have:

- `arabic_content_cleaned.md` - Cleaned Arabic text content
- `arabic_chunks.txt` - Text chunks for inspection
- `data/arabic_lancedb/` - Vector database with embeddings
- `arabic_chunks.lance` - LanceDB table file

## 🌐 Language Support

### Arabic Features
- Right-to-left text support
- Arabic character normalization
- Arabic-specific chunking optimization
- Bilingual system prompts

### English Features
- Standard English text processing
- Cross-language search capability
- English interface options

## 🔮 Future Enhancements

- **OCR Enhancement**: Better Arabic text extraction from images
- **Dialect Support**: Regional Arabic dialect recognition
- **Advanced Search**: Semantic search with Arabic language models
- **Real-time Translation**: Arabic-English translation capabilities
- **Performance Monitoring**: Advanced metrics and analytics

## 📚 Resources

- [Docling Documentation](https://ds4sd.github.io/docling/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [LanceDB Documentation](https://lancedb.github.io/lancedb/)
- [Arabic Unicode Ranges](https://unicode.org/charts/PDF/U0600.pdf)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test output for specific error messages
3. Ensure all environment variables are properly set
4. Verify Azure OpenAI service availability

---

**Built with ❤️ for Arabic language processing**
