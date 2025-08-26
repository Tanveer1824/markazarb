# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites

1. **GitHub Repository**: Your code must be in a public GitHub repository
2. **Azure OpenAI Account**: Active Azure OpenAI service with API keys
3. **Streamlit Cloud Account**: Free account at [share.streamlit.io](https://share.streamlit.io)

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository structure looks like this:
```
markazarb/
├── knowledge/
│   └── docling/
│       ├── 5-chat.py          # Main Streamlit app
│       ├── requirements.txt    # Python dependencies
│       ├── .streamlit/        # Streamlit configuration
│       │   └── config.toml
│       └── data/              # Database files (optional for cloud)
│           └── lancedb/
└── README.md
```

### 2. Set Environment Variables in Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. In the app settings, add these secrets:

```toml
AZURE_OPENAI_API_KEY = "your_actual_api_key"
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_OPENAI_DEPLOYMENT_NAME = "your-chat-model-name"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = "your-embedding-model-name"
```

### 3. Configure App Settings

- **Main file path**: `knowledge/docling/5-chat.py`
- **Python version**: 3.9 or higher
- **Requirements file**: `knowledge/docling/requirements.txt`

### 4. Deploy

Click "Deploy" and wait for the build to complete.

## Troubleshooting

### Common Issues

1. **Database Not Found Error**
   - The app will show a helpful error message
   - For cloud deployment, you need to either:
     - Include the database files in your repository, or
     - Set up a cloud database connection

2. **Environment Variables Missing**
   - Check that all required variables are set in Streamlit Cloud secrets
   - Ensure variable names match exactly (case-sensitive)

3. **Dependencies Installation Failed**
   - Check your `requirements.txt` file
   - Some packages may not be available on Streamlit Cloud

### Database Options for Cloud

1. **Include in Repository** (Recommended for small databases):
   - Add your `data/lancedb` folder to Git
   - Commit and push to GitHub
   - The app will automatically find it

2. **Cloud Database** (For larger datasets):
   - Use Azure Blob Storage
   - Or set up a cloud LanceDB instance
   - Update the connection code accordingly

## Local vs Cloud Differences

| Feature | Local | Streamlit Cloud |
|---------|-------|-----------------|
| Database Path | `data/lancedb` | Multiple paths checked |
| Environment | `.env` file | Streamlit secrets |
| File Access | Direct | Repository-based |
| Performance | Full | Limited by cloud resources |

## Security Notes

- Never commit API keys to your repository
- Use Streamlit Cloud secrets for sensitive data
- The app includes error handling to prevent crashes
- Database connection failures are handled gracefully

## Support

If you encounter issues:
1. Check the Streamlit Cloud logs
2. Verify your environment variables
3. Ensure your database files are accessible
4. Check the app's error messages for guidance
