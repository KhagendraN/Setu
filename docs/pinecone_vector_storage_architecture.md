# Pinecone Vector Storage Architecture

## Overview

This document demonstrates the hybrid vector storage architecture used in Module A for legal document retrieval. The system combines **Pinecone's cloud-based vector database** with **local JSON storage** to overcome metadata limitations while maintaining fast semantic search capabilities.

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Legal Document Ingestion                          │
│                                                                       │
│  Input: Nepal Constitution, Legal Acts, Court Judgments              │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   PDF Processing     │
                   │   (PyMuPDF)          │
                   │                      │
                   │   • Extract text     │
                   │   • Clean content    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   Text Chunking      │
                   │                      │
                   │   • Split documents  │
                   │   • Create chunk IDs │
                   │   • Add metadata     │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────────────┐
                   │   Embedding Generation       │
                   │   sentence-transformers      │
                   │   all-MiniLM-L6-v2          │
                   │                              │
                   │   Input: Text chunks         │
                   │   Output: 384-dim vectors    │
                   └──────────┬───────────────────┘
                              │
              ┌───────────────┴────────────────┐
              │                                │
              ▼                                ▼
┌─────────────────────────────┐   ┌──────────────────────────────┐
│   PINECONE CLOUD STORAGE    │   │   LOCAL JSON STORAGE         │
│   (AWS us-east-1)           │   │   (pinecone_text_storage.json)│
├─────────────────────────────┤   ├──────────────────────────────┤
│                             │   │                              │
│  Index: nepal-legal-docs    │   │  Purpose: Full text storage  │
│  Dimension: 384             │   │  Size: ~1.1 MB               │
│  Metric: Cosine similarity  │   │                              │
│                             │   │  Structure:                  │
│  Per Vector:                │   │  {                           │
│  ├─ ID: chunk_id           │   │    "chunk_0000": "full text",│
│  ├─ Values: [384 floats]   │   │    "chunk_0001": "full text",│
│  └─ Metadata:              │   │    ...                       │
│     ├─ text_preview (500ch)│   │  }                           │
│     ├─ text_length         │   │                              │
│     ├─ source_file         │   │  Avoids Pinecone's 40KB      │
│     ├─ page_number         │   │  metadata limit per vector   │
│     └─ ...                 │   │                              │
│                             │   │                              │
│  Supports:                  │   │                              │
│  • Semantic similarity      │   │                              │
│  • Fast vector search       │   │                              │
│  • Metadata filtering       │   │                              │
│  • Scalable to millions     │   │                              │
└─────────────┬───────────────┘   └──────────┬───────────────────┘
              │                               │
              └───────────┬───────────────────┘
                          │
                          ▼
              ┌───────────────────────────┐
              │   Synchronized Storage    │
              │                           │
              │   Chunk IDs link both     │
              │   storage systems         │
              └───────────────────────────┘
```

---

## Query Flow Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Query                               │
│  "What are the fundamental rights in Nepal Constitution?"        │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  Query Embedding     │
                   │  Generation          │
                   │                      │
                   │  Model: all-MiniLM   │
                   │  Output: 384-dim     │
                   └──────────┬───────────┘
                              │
                              ▼
         ┌────────────────────────────────────────────┐
         │    STEP 1: PINECONE CLOUD SEARCH           │
         ├────────────────────────────────────────────┤
         │                                            │
         │  Operation: Vector Similarity Search       │
         │  • Compare query vector with all vectors   │
         │  • Cosine similarity metric                │
         │  • Return top K matches (default: 5)       │
         │                                            │
         │  Result:                                   │
         │  ┌──────────────────────────────────────┐  │
         │  │ Match 1:                             │  │
         │  │   ID: chunk_0042                     │  │
         │  │   Score: 0.87                        │  │
         │  │   Metadata: {preview, page, source}  │  │
         │  ├──────────────────────────────────────┤  │
         │  │ Match 2:                             │  │
         │  │   ID: chunk_0014                     │  │
         │  │   Score: 0.82                        │  │
         │  │   Metadata: {preview, page, source}  │  │
         │  └──────────────────────────────────────┘  │
         └────────────────┬───────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────────────┐
         │    STEP 2: LOCAL TEXT RETRIEVAL            │
         ├────────────────────────────────────────────┤
         │                                            │
         │  For each chunk ID from Pinecone:          │
         │  1. Look up in pinecone_text_storage.json  │
         │  2. Retrieve full text content             │
         │  3. Combine with metadata                  │
         │                                            │
         │  Example:                                  │
         │  chunk_0042 → "17. Right to freedom: (1)  │
         │                No person shall be deprived │
         │                of his or her personal      │
         │                liberty except in accordance│
         │                with law. (2) Every citizen │
         │                shall have the following    │
         │                freedoms: (a) freedom of    │
         │                opinion and expression..."  │
         │                                            │
         └────────────────┬───────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────────────┐
         │    STEP 3: FORMAT RESULTS                  │
         ├────────────────────────────────────────────┤
         │                                            │
         │  Combine into standard format:             │
         │  {                                         │
         │    "ids": [["chunk_0042", "chunk_0014"]], │
         │    "documents": [[full_text_1, full_text_2]],│
         │    "metadatas": [[{...}, {...}]],          │
         │    "distances": [[0.87, 0.82]]             │
         │  }                                         │
         │                                            │
         └────────────────┬───────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────────────┐
         │    STEP 4: RAG CHAIN PROCESSING            │
         ├────────────────────────────────────────────┤
         │                                            │
         │  1. Pass retrieved chunks to LLM           │
         │  2. LLM generates answer using context     │
         │  3. Return answer with source citations    │
         │                                            │
         └────────────────┬───────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Response to User                              │
│                                                                  │
│  "According to Article 17 of the Nepal Constitution, the        │
│   fundamental rights include:                                   │
│   1. Freedom of opinion and expression                          │
│   2. Freedom to assemble peaceably and without arms             │
│   3. Freedom to form political parties                          │
│   ..."                                                          │
│                                                                  │
│  Source: Constitution of Nepal, Part 3, Article 17              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Storage Comparison

### What's Stored Where

| Component | Pinecone Cloud | Local JSON | Why? |
|-----------|---------------|------------|------|
| **Vector Embeddings** | ✅ (384 floats) | ❌ | Fast semantic search requires cloud-scale vector operations |
| **Chunk IDs** | ✅ | ✅ (as keys) | Links both storage systems |
| **Full Text** | ❌ | ✅ | Exceeds 40KB metadata limit |
| **Text Preview** | ✅ (500 chars) | ❌ | Allows quick preview without local lookup |
| **Metadata** | ✅ | ❌ | Enables filtering (by source, page, date, etc.) |
| **Similarity Scores** | ✅ (computed) | ❌ | Result of vector search |

### Storage Sizes

```
Pinecone Cloud (per vector):
├─ Vector: 384 floats × 4 bytes = 1,536 bytes
├─ Metadata: ~2-5 KB (text preview + fields)
└─ Total per vector: ~3.5-6.5 KB

Local JSON:
├─ Full text per chunk: 500-5,000 chars
├─ Current file size: 1.1 MB
└─ Contains: ~300-500 document chunks
```

---

## Implementation Details

### 1. Initialization

**File**: [module_a/pinecone_vector_db/pinecone_vector_db.py](../module_a/pinecone_vector_db/pinecone_vector_db.py)

```python
class PineconeLegalVectorDB:
    def __init__(self):
        # Connect to Pinecone cloud
        self.pc = Pinecone(api_key=PINECONE_API_KEY)

        # Load local text storage
        self.text_storage_file = PINECONE_TEXT_STORAGE_FILE
        self.text_storage = self._load_text_storage()

        # Connect to index
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
```

**Configuration** ([module_a/config.py](../module_a/config.py)):
```python
# Pinecone Cloud Settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME = "nepal-legal-docs"

# Local Storage
PINECONE_TEXT_STORAGE_FILE = DATA_DIR / "pinecone_text_storage.json"

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
```

### 2. Adding Documents (Upsert)

**Process** (Lines 218-313):

```python
def add_chunks(self, chunks, embeddings):
    vectors_to_upsert = []

    for chunk, embedding in zip(chunks, embeddings):
        chunk_id = chunk['chunk_id']
        text = chunk['text']

        # CRITICAL: Store full text locally
        self.text_storage[chunk_id] = text

        # Save periodically (every 100 chunks)
        if len(vectors_to_upsert) % 100 == 0:
            self._save_text_storage()

        # Prepare for Pinecone (only preview)
        metadata = {
            'text_preview': text[:500],
            'text_length': len(text),
            'source_file': chunk.get('source'),
            'page_number': chunk.get('page')
        }

        # Add to Pinecone batch
        vectors_to_upsert.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": metadata
        })

    # Upload to Pinecone in batches of 100
    for i in range(0, len(vectors_to_upsert), 100):
        batch = vectors_to_upsert[i:i+100]
        self.index.upsert(vectors=batch)

    # Final save to local storage
    self._save_text_storage()
```

### 3. Querying Documents

**Process** (Lines 342-411):

```python
def query_with_embedding(self, query_embedding, n_results=5):
    # STEP 1: Query Pinecone cloud
    results = self.index.query(
        vector=query_embedding,
        top_k=n_results,
        include_metadata=True
    )

    matches = results.get("matches", [])

    # STEP 2: Retrieve full text from local storage
    formatted_results = {
        "ids": [[match["id"] for match in matches]],
        "documents": [[
            self.text_storage.get(match["id"], "")
            for match in matches
        ]],
        "metadatas": [[match["metadata"] for match in matches]],
        "distances": [[match["score"] for match in matches]]
    }

    return formatted_results
```

### 4. Local Storage Management

**Loading** (Lines 110-123):
```python
def _load_text_storage(self):
    if self.text_storage_file.exists():
        with open(self.text_storage_file, 'r', encoding='utf-8') as f:
            storage = json.load(f)
        logger.info(f"Loaded {len(storage)} texts from storage")
        return storage
    return {}
```

**Saving** (Lines 125-135):
```python
def _save_text_storage(self):
    self.text_storage_file.parent.mkdir(parents=True, exist_ok=True)
    with open(self.text_storage_file, 'w', encoding='utf-8') as f:
        json.dump(self.text_storage, f, ensure_ascii=False, indent=2)
```

---

## Configuration & Setup

### Environment Variables

```bash
# Required: Pinecone API key
# Get from: https://app.pinecone.io/
PINECONE_API_KEY=your-api-key-here

# Optional: Override default index name
PINECONE_INDEX_NAME=nepal-legal-docs
```

### File Structure

```
locus_setu/
├── module_a/
│   ├── config.py                    # Configuration settings
│   ├── embeddings.py                # Embedding generation
│   └── pinecone_vector_db/
│       └── pinecone_vector_db.py   # Main vector DB class
└── data/
    └── module-A/
        ├── pinecone_text_storage.json   # Local full text storage
        └── logs/
            └── pinecone.log             # Operation logs
```

### Dependencies

```txt
# Pinecone client
pinecone-client>=3.0.0

# Embeddings
sentence-transformers>=2.2.0
torch>=2.0.0

# Utilities
numpy>=1.24.0
```

---

## Performance Characteristics

### Speed

| Operation | Time | Notes |
|-----------|------|-------|
| Index initialization | 5-10s | One-time on startup |
| Upload 100 vectors | ~2-3s | Batched upsert |
| Query (top 5) | ~200-500ms | Depends on index size |
| Local text lookup | <1ms | In-memory dict access |

### Scalability

```
Current Setup:
├─ Vectors in Pinecone: ~500
├─ JSON file size: 1.1 MB
└─ Query latency: ~300ms

Projected at Scale:
├─ 100,000 vectors: Query ~500ms
├─ 1,000,000 vectors: Query ~800ms
└─ JSON file: 200-500 MB (still manageable)
```

### Cost Optimization

**Pinecone Cloud**:
- Free tier: 1 index, up to 100K vectors
- Serverless: Pay per read/write operation
- Cost-effective for moderate usage

**Local Storage**:
- Zero cloud storage cost
- Reduces metadata costs
- Faster retrieval for full text

---

## Advantages & Trade-offs

### ✅ Advantages

1. **Overcomes Metadata Limits**
   - Pinecone: 40KB limit per vector
   - Solution: Store unlimited text locally

2. **Fast Semantic Search**
   - Leverages Pinecone's optimized vector search
   - Cosine similarity at scale
   - Sub-second query times

3. **Cost-Effective**
   - Minimize expensive cloud metadata storage
   - Free local storage for text

4. **Complete Context**
   - Full document chunks available for RAG
   - No truncation or information loss

### ⚠️ Trade-offs

1. **Storage Synchronization**
   - Must keep JSON and Pinecone in sync
   - If JSON is lost, full text is gone

2. **Not Fully Cloud-Native**
   - Local file dependency
   - Challenges in distributed deployments

3. **Backup Complexity**
   - Two storage systems to backup
   - Chunk IDs must match

### 🔧 Mitigation Strategies

```python
# Auto-save on periodic intervals
if len(vectors_to_upsert) % 100 == 0:
    self._save_text_storage()

# Final save after operations
self._save_text_storage()

# Reload on startup
self.text_storage = self._load_text_storage()
```

---

## Example Usage

### Building the Vector Database

```python
from module_a.pinecone_vector_db import PineconeLegalVectorDB
from module_a.embeddings import EmbeddingGenerator

# Initialize
db = PineconeLegalVectorDB()
embedder = EmbeddingGenerator()

# Prepare chunks
chunks = [
    {
        'chunk_id': 'constitution_chunk_0000',
        'text': 'THE CONSTITUTION OF NEPAL...',
        'metadata': {
            'source_file': 'Constitution-of-Nepal_2072_Eng.pdf',
            'page_number': 1
        }
    }
]

# Generate embeddings
embeddings = embedder.generate_embeddings([c['text'] for c in chunks])

# Add to database (stores in both Pinecone + local JSON)
db.add_chunks(chunks, embeddings)

print(f"Total vectors: {db.get_count()}")
# Output: Total vectors: 500
```

### Querying the Database

```python
# Generate query embedding
query = "What are fundamental rights in Nepal?"
query_embedding = embedder.generate_embeddings([query])[0]

# Search (queries Pinecone, retrieves from local JSON)
results = db.query_with_embedding(
    query_embedding=query_embedding,
    n_results=5
)

# Display results
for i, (doc, metadata, score) in enumerate(zip(
    results['documents'][0],
    results['metadatas'][0],
    results['distances'][0]
)):
    print(f"\n--- Result {i+1} (Score: {score:.3f}) ---")
    print(f"Source: {metadata.get('source_file')}")
    print(f"Page: {metadata.get('page_number')}")
    print(f"Text: {doc[:200]}...")
```

**Output**:
```
--- Result 1 (Score: 0.872) ---
Source: Constitution-of-Nepal_2072_Eng.pdf
Page: 7
Text: 17. Right to freedom: (1) No person shall be deprived of
his or her personal liberty except in accordance with law. (2)
Every citizen shall have the following freedoms: (a) freedom...

--- Result 2 (Score: 0.845) ---
Source: Constitution-of-Nepal_2072_Eng.pdf
Page: 6
Text: 16. Right to live with dignity: (1) Every person shall
have the right to live with dignity. (2) No law shall be made...
```

---

## Monitoring & Debugging

### Logs

**Location**: `data/module-A/logs/pinecone.log`

**Sample Log Output**:
```
2026-01-06 10:15:23 - INFO - ============================================================
2026-01-06 10:15:23 - INFO - 🚀 STARTING PINECONE INITIALIZATION
2026-01-06 10:15:23 - INFO - ============================================================
2026-01-06 10:15:23 - INFO - Index Name: nepal-legal-docs
2026-01-06 10:15:24 - INFO - ✓ Pinecone client initialized
2026-01-06 10:15:24 - INFO - ✓ Embedding generator ready
2026-01-06 10:15:24 - INFO - Loaded 487 texts from storage file
2026-01-06 10:15:25 - INFO - Using existing Pinecone index: nepal-legal-docs
2026-01-06 10:15:26 - INFO - ============================================================
2026-01-06 10:15:26 - INFO - ✅ CONNECTED TO PINECONE INDEX: 'nepal-legal-docs'
2026-01-06 10:15:26 - INFO - 📊 Total Vectors: 487
2026-01-06 10:15:26 - INFO - ============================================================
```

### Health Checks

```python
# Check Pinecone connection
stats = db.index.describe_index_stats()
print(f"Vectors in cloud: {stats.get('total_vector_count')}")

# Check local storage
print(f"Texts in local storage: {len(db.text_storage)}")

# Verify sync
assert stats.get('total_vector_count') == len(db.text_storage)
print("✓ Storage systems in sync")
```

---

## Future Improvements

### Potential Enhancements

1. **Cloud-Native Text Storage**
   - Use S3/Cloud Storage instead of local JSON
   - Better for distributed deployments

2. **Backup & Recovery**
   - Automated backups of JSON file
   - Recovery mechanism if out of sync

3. **Compression**
   - Compress JSON file (gzip)
   - Reduce disk usage

4. **Caching Layer**
   - Cache frequently accessed texts
   - Redis for distributed caching

5. **Metadata Enrichment**
   - Store more searchable metadata in Pinecone
   - Enable advanced filtering

---

## References

- **Pinecone Documentation**: https://docs.pinecone.io/
- **Sentence Transformers**: https://www.sbert.net/
- **Implementation**: [module_a/pinecone_vector_db/](../module_a/pinecone_vector_db/)
- **Configuration**: [module_a/config.py](../module_a/config.py)

---

## Summary

This hybrid architecture provides an effective solution for storing and retrieving large legal documents:

- ✅ **Fast semantic search** via Pinecone cloud
- ✅ **Complete text storage** via local JSON
- ✅ **Cost-effective** hybrid approach
- ✅ **Scalable** to millions of vectors
- ✅ **Production-ready** with proper error handling

The system successfully powers the legal document RAG system in Module A, enabling users to find relevant legal information through natural language queries.
