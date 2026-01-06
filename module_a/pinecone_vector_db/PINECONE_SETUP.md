# Pinecone Vector Database Setup Guide

This guide will help you set up Pinecone cloud storage for your vector database.

## Prerequisites

1. A Pinecone account (sign up at https://app.pinecone.io/)
2. A Pinecone API key

## Setup Steps

### 1. Get Your Pinecone API Key

1. Go to https://app.pinecone.io/
2. Sign up or log in
3. Navigate to your API keys section
4. Copy your API key

### 2. Set the API Key

You have two options:

#### Option A: Environment Variable (Recommended)
Set the environment variable before running your code:

**Windows (PowerShell):**
```powershell
$env:PINECONE_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set PINECONE_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export PINECONE_API_KEY="your-api-key-here"
```

#### Option B: Direct Configuration
Edit `module_a/config.py` and set:
```python
PINECONE_API_KEY = "your-api-key-here"
```

**Note:** Option A is recommended for security reasons.

### 3. Install Dependencies

Make sure you have the Pinecone client installed:
```bash
pip install pinecone-client[grpc]>=3.0.0
```

Or install all requirements:
```bash
pip install -r module_a/requirements.txt
```

### 4. Build Your Vector Database

Run the build script:
```bash
python -m module_a.build_vector_db
```

The script will automatically detect if Pinecone is configured and use it instead of ChromaDB.

### 5. Verify Setup

The build script will:
- Create a Pinecone index if it doesn't exist
- Upload your document chunks to Pinecone
- Store full text in a local JSON file (to avoid Pinecone metadata limits)

## How It Works

### Text Storage
Pinecone has a 40KB limit on metadata per vector. To work around this:
- Full text is stored in a local JSON file (`data/module-A/pinecone_text_storage.json`)
- Only a text preview is stored in Pinecone metadata
- The system automatically loads and saves this storage file

### Index Configuration
- **Index Name:** `nepal-legal-docs` (configurable in `config.py`)
- **Dimension:** 384 (matches the embedding model)
- **Metric:** Cosine similarity
- **Cloud:** AWS
- **Region:** us-east-1 (configurable in `pinecone_vector_db.py`)

## Troubleshooting

### "PINECONE_API_KEY must be set"
- Make sure you've set the API key (see Step 2)
- Check that the environment variable is set in the same terminal session

### "Index creation failed"
- Check your Pinecone dashboard for quota limits
- Verify your API key is valid
- Try a different region if us-east-1 is unavailable

### "Failed to connect to index"
- Wait a few minutes after index creation (it takes time to initialize)
- Check your network connection
- Verify the index exists in your Pinecone dashboard

### Text not found in queries
- Make sure `pinecone_text_storage.json` exists and contains your data
- The file is automatically created when you build the database
- If you delete it, you'll need to rebuild the database

## Switching Between ChromaDB and Pinecone

The system automatically uses Pinecone if `PINECONE_API_KEY` is set, otherwise it falls back to ChromaDB.

**Important:** The application will automatically fall back to ChromaDB if:
- Pinecone API key is not set
- Pinecone initialization fails
- Pinecone client is not installed

This means your application will work even without Pinecone configured - it will just use the local ChromaDB instead.

To switch:
- **Use Pinecone:** Set `PINECONE_API_KEY` environment variable
- **Use ChromaDB:** Unset or remove `PINECONE_API_KEY`

The RAG chain (`LegalRAGChain`) automatically detects which vector database to use at initialization time.

## Cost Considerations

Pinecone offers a free tier with:
- 1 index
- 100K vectors
- 1M queries/month

Check https://www.pinecone.io/pricing/ for current pricing.

## Support

For Pinecone-specific issues, check:
- Pinecone Documentation: https://docs.pinecone.io/
- Pinecone Console: https://app.pinecone.io/
