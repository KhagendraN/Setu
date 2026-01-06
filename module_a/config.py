"""
Configuration module for Module A
Contains all settings, paths, and parameters
"""

import os
from pathlib import Path
import re

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Load .env from project root (parent of module_a)
    _BASE_DIR = Path(__file__).parent.parent
    env_file = _BASE_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        # Also try loading from current directory
        load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "module-A"
LAW_DIR = DATA_DIR / "law"
CHUNKS_DIR = DATA_DIR / "chunks"
LOG_DIR = DATA_DIR / "logs"

# Ensure output directory exists
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Output file
CHUNKS_OUTPUT_FILE = CHUNKS_DIR / "processed_chunks.json"

# Chunking parameters
CHUNK_SIZE_MIN_WORDS = 300
CHUNK_SIZE_MAX_WORDS = 600
CHUNK_SIZE_TARGET_WORDS = 450
CHUNK_OVERLAP_WORDS = 50  # Overlap for context preservation

# Token estimation (rough: 1 word ≈ 1.3 tokens)
CHUNK_SIZE_MIN_TOKENS = int(CHUNK_SIZE_MIN_WORDS * 1.3)
CHUNK_SIZE_MAX_TOKENS = int(CHUNK_SIZE_MAX_WORDS * 1.3)

# Text cleaning patterns
CLEANING_PATTERNS = {
    # Page numbers (various formats)
    'page_numbers': [
        r'^\s*\d+\s*$',  # Standalone numbers
        r'Page\s+\d+',
        r'पृष्ठ\s+\d+',
    ],
    
    # Headers and footers
    'headers_footers': [
        r'www\..*?\.gov\.np',
        r'Constitution of Nepal.*?\d{4}',
        r'Nepal Gazette.*?Part.*?\d+',
        r'©.*?Government of Nepal',
    ],
    
    # Table of contents patterns
    'toc_patterns': [
        r'Table of Contents',
        r'CONTENTS',
        r'विषयसूची',
    ],
    
    # Excessive whitespace
    'whitespace': [
        r'\n\s*\n\s*\n+',  # Multiple blank lines
        r'[ \t]+',  # Multiple spaces/tabs
    ],
}

# Section/Article detection patterns
SECTION_PATTERNS = [
    # Numbered sections at start of line: "11. Right to citizenship:"
    r'^\s*(\d+[A-Za-z]?)\.\s+([A-Z][^:]+):',
    
    # Article patterns: "Article 11", "ARTICLE 11"
    r'^\s*(?:Article|ARTICLE)\s+(\d+[A-Za-z]?)',
    
    # Section patterns: "Section 8", "SECTION 8"  
    r'^\s*(?:Section|SECTION)\s+(\d+[A-Za-z]?)',
    
    # Part patterns: "Part 4", "PART 4"
    r'^\s*(?:Part|PART)\s+(\d+[A-Za-z]?)',
    
    # Chapter patterns: "Chapter 3", "CHAPTER 3"
    r'^\s*(?:Chapter|CHAPTER)\s+(\d+[A-Za-z]?)',
    
    # Nepali patterns (if needed later)
    r'^\s*धारा\s+(\d+[A-Za-z]?)',
    r'^\s*अनुच्छेद\s+(\d+[A-Za-z]?)',
]

# Compile regex patterns for efficiency
COMPILED_SECTION_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in SECTION_PATTERNS]

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOG_DIR / "pinecone.log"
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_FILE_BACKUP_COUNT = 5  # Keep 5 backup files

# PDF extraction settings
PDF_EXTRACTION_METHOD = "pdfplumber"  # Options: "pdfplumber", "pypdf2"
PDF_FALLBACK_METHOD = "pypdf2"  # Fallback if primary fails

# Vector database settings (Step 3)
VECTOR_DB_DIR = DATA_DIR / "vector_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # For all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE = 32

# Pinecone settings - Read from environment or set here
# Get your API key from: https://app.pinecone.io/
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "nepal-legal-docs")
PINECONE_TEXT_STORAGE_FILE = DATA_DIR / "pinecone_text_storage.json"


# Retrieval settings
DEFAULT_RETRIEVAL_K = 5  # Number of chunks to retrieve

# LLM settings (Step 4)
MISTRAL_MODEL = "mistral-tiny"  # Options: mistral-tiny, mistral-small, mistral-medium
MISTRAL_API_KEY_ENV_VAR = "MISTRAL_API_KEY"

