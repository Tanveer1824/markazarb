# Environment Setup for Docling

## Required Environment Variables

Create a `.env` file in this directory with the following variables:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Model Deployment Names
# For chat completions (GPT-4, GPT-3.5-turbo, etc.)
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your-chat-deployment-name
# For embeddings (text-embedding-3-large, text-embedding-ada-002, etc.)
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your-embedding-deployment-name
```

## Important Notes

1. **You need TWO separate deployment names:**
   - `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`: For chat completions (GPT models)
   - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`: For embeddings (embedding models)

2. **Model Compatibility:**
   - Chat models (GPT-4, GPT-3.5-turbo) can only do chat completions
   - Embedding models (text-embedding-3-large) can only do embeddings
   - Never use an embedding model for chat completions or vice versa

3. **Common Models:**
   - **Chat Models:** gpt-4, gpt-4-turbo, gpt-3.5-turbo
   - **Embedding Models:** text-embedding-3-large, text-embedding-ada-002

## Testing

Run the test file to verify your configuration:

```bash
python test_azure_connection.py
```

This will test both chat completions and embeddings if both models are configured.
