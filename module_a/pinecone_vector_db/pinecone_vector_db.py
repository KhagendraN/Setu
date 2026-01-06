"""
Production-ready Pinecone Vector Database with critical fixes
Fixes all showstopper bugs that would prevent usage
"""

import logging
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

from module_a.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_TEXT_STORAGE_FILE,
    DEFAULT_RETRIEVAL_K,
    EMBEDDING_DIMENSION,
)
from module_a.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

# Set up file logging for Pinecone operations
def _setup_pinecone_logging():
    """Ensure Pinecone logs are written to file"""
    try:
        from ..logging_setup import get_pinecone_logger
        pinecone_logger = get_pinecone_logger()
        # Also update the module logger
        logger.handlers = pinecone_logger.handlers
        logger.setLevel(pinecone_logger.level)
    except Exception:
        pass  # Fallback to default logging if setup fails

_setup_pinecone_logging()


class PineconeLegalVectorDB:
    """Production-ready Pinecone vector database for legal documents"""

    def __init__(self, text_storage: Optional[Dict[str, str]] = None, text_storage_file: Optional[Path] = None):
        """
        Initialize Pinecone with proper error handling
        
        Args:
            text_storage: Optional external dict to store full text (avoids metadata limits)
            text_storage_file: Optional path to JSON file for persistent text storage
        """
        if not PINECONE_AVAILABLE:
            raise ImportError(
                "pinecone-client not installed. "
                "Install with: pip install -U pinecone-client"
            )

        if not PINECONE_API_KEY:
            raise ValueError(
                "PINECONE_API_KEY must be set in config.py or environment. "
                "Get your API key from: https://app.pinecone.io/"
            )

        logger.info("=" * 60)
        logger.info("🚀 STARTING PINECONE INITIALIZATION")
        logger.info("=" * 60)
        logger.info(f"Index Name: {PINECONE_INDEX_NAME}")
        logger.info(f"API Key: {'*' * 20}...{PINECONE_API_KEY[-4:] if len(PINECONE_API_KEY) > 4 else '***'}")
        
        try:
            # Initialize Pinecone client
            logger.info("Connecting to Pinecone API...")
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            self.index_name = PINECONE_INDEX_NAME
            logger.info("✓ Pinecone client initialized")
            
            self.embedder = EmbeddingGenerator()
            logger.info("✓ Embedding generator ready")
            
            # Set up persistent text storage
            self.text_storage_file = Path(text_storage_file) if text_storage_file else PINECONE_TEXT_STORAGE_FILE
            if text_storage is not None:
                self.text_storage = text_storage
            else:
                self.text_storage = self._load_text_storage()
            
            # Check/create index
            self._initialize_index()
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            
            # Verify connection
            self._verify_connection()
            
            logger.info("=" * 60)
            logger.info("✅ PINECONE INITIALIZATION COMPLETE")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise RuntimeError(
                f"Pinecone initialization failed: {e}. "
                "Check your API key and network connection."
            )
    
    def _load_text_storage(self) -> Dict[str, str]:
        """Load text storage from JSON file"""
        if self.text_storage_file.exists():
            try:
                with open(self.text_storage_file, 'r', encoding='utf-8') as f:
                    storage = json.load(f)
                logger.info(f"Loaded {len(storage)} texts from storage file")
                return storage
            except Exception as e:
                logger.warning(f"Failed to load text storage: {e}. Starting with empty storage.")
                return {}
        else:
            logger.info("Text storage file not found. Starting with empty storage.")
            return {}
    
    def _save_text_storage(self) -> None:
        """Save text storage to JSON file"""
        try:
            # Ensure parent directory exists
            self.text_storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.text_storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.text_storage, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved {len(self.text_storage)} texts to storage file")
        except Exception as e:
            logger.warning(f"Failed to save text storage: {e}")

    def _initialize_index(self):
        """Create index if it doesn't exist, with proper waiting"""
        try:
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        except Exception as e:
            raise RuntimeError(f"Failed to list Pinecone indexes: {e}")
        
        if self.index_name not in existing_indexes:
            logger.info(f"Creating new Pinecone index: {self.index_name}")
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=EMBEDDING_DIMENSION,
                    metric="cosine",  # Returns similarity 0-1, higher = better
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'  # Change to your preferred region
                    )
                )
                
                # CRITICAL: Wait for index to be ready with timeout
                logger.info("Waiting for index to be ready...")
                max_wait = 120  # 2 minutes max
                waited = 0
                
                while waited < max_wait:
                    try:
                        desc = self.pc.describe_index(self.index_name)
                        # Check if ready (API may return dict or object)
                        if isinstance(desc, dict):
                            # New API format
                            ready = desc.get('status', {}).get('ready', False) if isinstance(desc.get('status'), dict) else False
                        else:
                            # Object format
                            status = getattr(desc, 'status', None)
                            if status:
                                ready = getattr(status, 'ready', False) if hasattr(status, 'ready') else False
                            else:
                                ready = False
                        
                        if ready:
                            logger.info(f"Index ready after {waited}s")
                            break
                    except Exception as e:
                        logger.debug(f"Waiting for index... ({e})")
                    
                    time.sleep(5)
                    waited += 5
                
                if waited >= max_wait:
                    raise TimeoutError(
                        f"Index creation timed out after {max_wait}s. "
                        "Check Pinecone console: https://app.pinecone.io/"
                    )
                    
            except Exception as e:
                logger.error(f"Failed to create index: {e}")
                raise RuntimeError(
                    f"Index creation failed: {e}. "
                    "This may be due to: (1) Invalid API key, (2) Region not available, "
                    "(3) Quota exceeded. Check your Pinecone dashboard."
                )
        else:
            logger.info(f"Using existing Pinecone index: {self.index_name}")

    def _verify_connection(self):
        """Verify we can connect to and query the index"""
        try:
            logger.info("Verifying connection to Pinecone index...")
            stats = self.index.describe_index_stats()
            current_count = stats.get('total_vector_count', 0)
            logger.info("=" * 60)
            logger.info(f"✅ CONNECTED TO PINECONE INDEX: '{self.index_name}'")
            logger.info(f"📊 Total Vectors: {current_count:,}")
            logger.info("=" * 60)
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to index: {e}. "
                "Index may not be ready yet. Wait a few minutes and retry."
            )

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> None:
        """
        Add chunks with embeddings to the database
        
        Args:
            chunks: List of chunk dicts with 'chunk_id', 'text', and 'metadata'
            embeddings: List of embedding vectors
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunk count ({len(chunks)}) must match embedding count ({len(embeddings)})"
            )

        if not chunks:
            logger.warning("No chunks to add")
            return

        vectors_to_upsert = []
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = chunk.get('chunk_id')
            if not chunk_id:
                raise ValueError("Each chunk must have a 'chunk_id' field")
            
            text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})
            
            # CRITICAL FIX: Store full text externally to avoid 40KB metadata limit
            # Only store a preview in metadata
            self.text_storage[chunk_id] = text  # Store full text
            
            # Save to persistent storage periodically (every 100 chunks)
            if len(vectors_to_upsert) % 100 == 0:
                self._save_text_storage()
            
            # Prepare metadata with text preview
            cleaned_metadata = self._clean_metadata(metadata)
            cleaned_metadata['text_preview'] = text[:500] + ('...' if len(text) > 500 else '')
            cleaned_metadata['text_length'] = len(text)
            
            # Validate metadata size (Pinecone limit: ~40KB)
            metadata_size = len(json.dumps(cleaned_metadata))
            if metadata_size > 35000:  # Leave some buffer
                logger.warning(
                    f"Chunk {chunk_id} metadata too large ({metadata_size} bytes), "
                    "reducing preview..."
                )
                cleaned_metadata['text_preview'] = text[:200] + '...'
            
            vectors_to_upsert.append({
                "id": chunk_id,
                "values": embedding,
                "metadata": cleaned_metadata,
            })

        logger.info(f"Upserting {len(chunks)} chunks to Pinecone...")
        
        # Upsert in batches with error handling
        batch_size = 100
        total_batches = (len(vectors_to_upsert) + batch_size - 1) // batch_size
        
        try:
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i+batch_size]
                batch_num = i // batch_size + 1
                
                try:
                    # Use namespace parameter only if needed (some Pinecone versions don't require it)
                    self.index.upsert(vectors=batch)
                    logger.info(f"✓ Batch {batch_num}/{total_batches} upserted")
                except Exception as e:
                    logger.error(f"✗ Batch {batch_num} failed: {e}")
                    raise
            
            # Wait for consistency
            time.sleep(2)
            
            # Verify upload
            stats = self.index.describe_index_stats()
            total_count = stats.get('total_vector_count', 0)
            logger.info(f"✓ Upload complete. Total vectors in DB: {total_count}")
            
            # Save text storage after all chunks are added
            self._save_text_storage()
            
        except Exception as e:
            logger.error(f"Failed to add chunks: {e}")
            raise RuntimeError(
                f"Chunk upload failed: {e}. "
                "This may be due to: (1) Network issues, (2) Malformed vectors, "
                "(3) Quota limits. Check Pinecone console for details."
            )

    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean metadata to be Pinecone-compatible
        Pinecone supports: strings, numbers, booleans, lists of strings
        """
        cleaned = {}
        for key, value in metadata.items():
            if value is None:
                continue
            
            # Pinecone metadata keys can't contain dots
            safe_key = key.replace('.', '_')
            
            if isinstance(value, (str, int, float, bool)):
                cleaned[safe_key] = value
            elif isinstance(value, list):
                # Convert list items to compatible types
                cleaned[safe_key] = [
                    str(item) if not isinstance(item, (str, int, float, bool)) 
                    else item 
                    for item in value
                ]
            else:
                cleaned[safe_key] = str(value)
                
        return cleaned

    def query_with_embedding(
        self,
        query_embedding: List[float],
        n_results: int = DEFAULT_RETRIEVAL_K,
        where: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Query with pre-computed embedding
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter (Pinecone filter syntax)
            
        Returns:
            Dict with 'ids', 'documents', 'metadatas', 'distances' (actually scores!)
        """
        logger.info(f"🔍 QUERYING PINECONE - Index: {self.index_name}, Top K: {n_results}")

        try:
            # Build query parameters
            query_params = {
                "vector": query_embedding,
                "top_k": n_results,
                "include_metadata": True
            }
            if where:
                query_params["filter"] = where
            
            results = self.index.query(**query_params)

            matches = results.get("matches", [])
            
            if not matches:
                logger.warning("No matches found")
                return {
                    "ids": [[]],
                    "documents": [[]],
                    "metadatas": [[]],
                    "distances": [[]]  # Actually similarity scores!
                }
            
            # CRITICAL FIX: Retrieve full text from storage, not metadata
            formatted_results = {
                "ids": [[match["id"] for match in matches]],
                "documents": [[
                    self.text_storage.get(match["id"], match["metadata"].get("text_preview", ""))
                    for match in matches
                ]],
                "metadatas": [[
                    {k: v for k, v in match["metadata"].items() 
                     if k not in ('text_preview', 'text_length')}
                    for match in matches
                ]],
                # CRITICAL: These are SIMILARITY SCORES (0-1, higher=better), not distances!
                "distances": [[match["score"] for match in matches]],
            }

            logger.info(
                f"✅ PINECONE QUERY SUCCESS - Retrieved {len(matches)} results, "
                f"Top score: {matches[0]['score']:.3f}"
            )
            return formatted_results
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise RuntimeError(
                f"Pinecone query failed: {e}. "
                "Check your network connection and Pinecone console."
            )

    def get_count(self) -> int:
        """Get the number of vectors in the database"""
        try:
            stats = self.index.describe_index_stats()
            return stats.get('total_vector_count', 0)
        except Exception as e:
            logger.error(f"Failed to get count: {e}")
            return 0
    
    def delete_all(self) -> None:
        """Delete all vectors from the index (use with caution!)"""
        try:
            self.index.delete(delete_all=True)
            self.text_storage.clear()
            self._save_text_storage()
            logger.info("✓ Deleted all vectors from index")
        except Exception as e:
            logger.error(f"Failed to delete all: {e}")
            raise
    
    def delete_by_ids(self, ids: List[str]) -> None:
        """Delete specific vectors by ID"""
        try:
            self.index.delete(ids=ids)
            for id in ids:
                self.text_storage.pop(id, None)
            self._save_text_storage()
            logger.info(f"✓ Deleted {len(ids)} vectors")
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            raise