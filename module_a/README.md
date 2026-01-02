# Module A: Law Explanation (RAG Pipeline)

## Overview

Module A implements the Law Explanation feature for the **Nepal Justice Weaver** platform using Retrieval-Augmented Generation (RAG). This module processes legal documents from Nepal and prepares them for intelligent question-answering.

## Current Status: Step 2 Complete ✓

**Step 2: Extract and Chunk Text** has been implemented with a modular architecture.

## Architecture

```
module_a/
├── __init__.py           # Package initialization
├── config.py             # Central configuration
├── models.py             # Data models (DocumentChunk, ChunkMetadata)
├── extractors.py         # PDF text extraction
├── cleaners.py           # Text cleaning and normalization
├── chunkers.py           # Intelligent text chunking
├── storage.py            # Data persistence
├── process_documents.py  # Main pipeline orchestration
└── requirements.txt      # Python dependencies
```

## Installation

```bash
cd module_a
pip install -r requirements.txt
```

## Usage

### Process All Documents

```bash
python -m module_a.process_documents
```

This will:
1. Extract text from all PDFs in `data/module-A/law/`
2. Clean and normalize the text
3. Split into intelligent chunks (300-600 words)
4. Save to `data/module-A/chunks/processed_chunks.json`

### Output Files

- `data/module-A/chunks/processed_chunks.json` - All chunks with metadata
- `data/module-A/chunks/chunks_summary.txt` - Human-readable summary

## Features

### PDF Extraction
- Supports multiple extraction methods (pdfplumber, PyPDF2)
- Automatic fallback if primary method fails
- Page-level extraction with metadata

### Text Cleaning
- Removes headers, footers, page numbers
- Fixes line breaks and formatting issues
- Normalizes unicode characters
- Removes table of contents patterns

### Intelligent Chunking
- **Section/Article Detection**: Automatically detects "Article 11", "Section 8", etc.
- **Context-Aware Splitting**: Breaks at sentence boundaries
- **Metadata Preservation**: Tracks source file, article/section, word count
- **Configurable Size**: 300-600 words per chunk (configurable)
- **Overlap Support**: Maintains context between chunks

## Module Components

### `config.py`
Central configuration for paths, chunking parameters, and cleaning patterns.

### `models.py`
Data structures:
- `DocumentChunk`: Represents a text chunk with metadata
- `ChunkMetadata`: Source file, article/section, page numbers, word count
- `ProcessingStats`: Processing statistics

### `extractors.py`
`PDFExtractor` class for extracting text from PDFs with multiple methods and fallback support.

### `cleaners.py`
`TextCleaner` class for comprehensive text cleaning and normalization.

### `chunkers.py`
`LegalDocumentChunker` class for intelligent, section-aware chunking.

### `storage.py`
`ChunkStorage` class for saving/loading chunks with validation.

### `process_documents.py`
`DocumentProcessor` class that orchestrates the entire pipeline.

## Next Steps (Step 3)

The chunks are now ready for:
1. Embedding generation using sentence-transformers
2. Vector database creation (ChromaDB)
3. Retrieval testing

## Example Output

```json
{
  "metadata": {
    "total_chunks": 127,
    "version": "1.0"
  },
  "chunks": [
    {
      "chunk_id": "Constitution-of-Nepal_2072_Eng_chunk_0001",
      "text": "Article 11: Citizenship...",
      "metadata": {
        "source_file": "Constitution-of-Nepal_2072_Eng.pdf",
        "article_section": "Article 11",
        "word_count": 456,
        "char_count": 2834
      }
    }
  ]
}
```

## Configuration

Edit `config.py` to customize:
- Chunk size (min/max/target words)
- Overlap between chunks
- Cleaning patterns
- PDF extraction method

## Troubleshooting

**No text extracted**: Some PDFs may be scanned images. Use OCR preprocessing if needed.

**Chunks too large/small**: Adjust `CHUNK_SIZE_*` parameters in `config.py`.

**Missing sections**: Check `SECTION_PATTERNS` in `config.py` for your document format.

## License

Part of Nepal Justice Weaver - Hackathon Project
