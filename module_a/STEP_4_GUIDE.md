# Step 4: RAG Chain with Mistral API

## Overview

Step 4 implements the Retrieval-Augmented Generation (RAG) chain, combining the vector database from Step 3 with the Mistral AI API to generate simple, accurate legal explanations.

## Components Built

1. **Mistral Client** (`llm_client.py`): Handles API interaction with error handling.
2. **Prompt Templates** (`prompts.py`): Specialized prompts for legal simplification.
3. **RAG Chain** (`rag_chain.py`): Orchestrates retrieval and generation.
4. **Testing Script** (`test_rag.py`): End-to-end verification.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install mistralai python-dotenv
   ```

2. **Configure API Key**:
   Create a `.env` file in the project root:
   ```
   MISTRAL_API_KEY=your_mistral_api_key_here
   ```

## Usage

### Running Tests
```bash
python -m module_a.test_rag
```

### Using in Code
```python
from module_a.rag_chain import LegalRAGChain

# Initialize chain
rag = LegalRAGChain()

# Run query
result = rag.run("How to get citizenship for my child?")

# Access results
print(result['explanation'])
print(result['sources'])
```

## Configuration

Settings in `module_a/config.py`:
- `MISTRAL_MODEL`: "mistral-tiny" (default), "mistral-small", etc.
- `DEFAULT_RETRIEVAL_K`: Number of chunks to retrieve (default: 5)

## How It Works

1. **User Query** -> Embedding Generator
2. **Embedding** -> Vector Database (Find top 5 relevant chunks)
3. **Chunks + Query** -> Prompt Template (Context injection)
4. **Prompt** -> Mistral API
5. **Response** -> Simple Legal Explanation

## Troubleshooting

- **API Key Error**: Ensure `.env` exists and `MISTRAL_API_KEY` is set.
- **Import Error**: Ensure `mistralai` is installed.
- **Empty Response**: Check internet connection and API limits.
