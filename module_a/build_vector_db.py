"""
Build vector database from processed chunks
Main pipeline for Step 3
"""

import json
import logging
import time
from pathlib import Path

from .config import CHUNKS_OUTPUT_FILE, LOG_LEVEL, LOG_FORMAT, PINECONE_API_KEY
from .embeddings import EmbeddingGenerator
from .vector_db import LegalVectorDB

# Try to import Pinecone, use it if API key is set
try:
    from .pinecone_vector_db import PineconeLegalVectorDB
    USE_PINECONE = bool(PINECONE_API_KEY)
except ImportError:
    USE_PINECONE = False
    PineconeLegalVectorDB = None 


logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def load_chunks(chunks_file: Path):
    """Load processed chunks from JSON"""
    logger.info(f"Loading chunks from {chunks_file}")
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chunks = data['chunks']
    logger.info(f"Loaded {len(chunks)} chunks")
    
    return chunks


def main():
    """Main pipeline to build vector database"""
    print("=" * 80)
    print("Building Vector Database for Nepal Legal Documents")
    print("=" * 80)
    
    logger.info("=" * 80)
    logger.info("Starting Vector Database Build Pipeline")
    logger.info("=" * 80)
    
    start_time = time.time()
    
    try:
        # Step 1: Load chunks
        print("\nStep 1: Loading processed chunks...")
        chunks = load_chunks(CHUNKS_OUTPUT_FILE)
        print(f"✓ Loaded {len(chunks)} chunks")
        
        # Step 2: Initialize embedding generator
        print("\nStep 2: Initializing embedding model...")
        logger.info("Initializing embedding model (this may take a moment on first run)...")
        embedder = EmbeddingGenerator()
        print(f"✓ Model loaded: {embedder.model_name}")
        print(f"✓ Embedding dimension: {embedder.embedding_dim}")
        
        # Step 3: Generate embeddings
        print("\nStep 3: Generating embeddings for all chunks...")
        print("(This will take a minute or two...)")
        texts = [chunk['text'] for chunk in chunks]
        embeddings = embedder.generate_embeddings_batch(texts, show_progress=True)
        
        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"✓ Embedding shape: {embeddings.shape}")
        
        # Step 4: Initialize vector database
        print("\nStep 4: Initializing vector database...")
        if USE_PINECONE:
            print("Using Pinecone cloud vector database...")
            vector_db = PineconeLegalVectorDB()
            print(f"✓ Connected to Pinecone index: {vector_db.index_name}")
        else:
            print("Using local ChromaDB vector database...")
            vector_db = LegalVectorDB()
            print(f"✓ Database initialized at: {vector_db.persist_directory}")
        
        # Step 5: Add chunks to database
        print("\nStep 5: Adding chunks to vector database...")
        vector_db.add_chunks(chunks, embeddings.tolist())
        
        final_count = vector_db.get_count()
        print(f"✓ Successfully indexed {final_count} chunks")
        
        # Calculate stats
        elapsed_time = time.time() - start_time
        
        # Print summary
        print("\n" + "=" * 80)
        print("VECTOR DATABASE BUILD COMPLETE!")
        print("=" * 80)
        print(f"Total chunks indexed: {final_count}")
        print(f"Embedding dimension: {embedder.embedding_dim}")
        print(f"Embedding model: {embedder.model_name}")
        print(f"Build time: {elapsed_time:.2f} seconds")
        if USE_PINECONE:
            print(f"Database: Pinecone cloud index '{vector_db.index_name}'")
        else:
            print(f"Database location: {vector_db.persist_directory}")
        print("=" * 80)
        
        logger.info("=" * 80)
        logger.info("Vector Database Build Complete!")
        logger.info(f"Total chunks indexed: {final_count}")
        logger.info(f"Build time: {elapsed_time:.2f} seconds")
        logger.info("=" * 80)
        
        print(f"\n✓ Vector database built successfully!")
        print(f"✓ Ready for retrieval testing")
        print(f"\nNext step: Run 'python -m module_a.test_retrieval' to test queries")
        
        return 0
        
    except Exception as e:
        logger.error(f"Build failed: {e}", exc_info=True)
        print(f"\n✗ Build failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
