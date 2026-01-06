"""
RAG Chain Module
Orchestrates retrieval and generation for legal explanations
"""

import logging
from typing import Dict, Any, List, Optional

from .embeddings import EmbeddingGenerator
from .llm_client import MistralClient
from .prompts import format_rag_prompt, LEGAL_SYSTEM_PROMPT
from .config import DEFAULT_RETRIEVAL_K, PINECONE_API_KEY

# Import Pinecone - required for RAG chain
try:
    from .pinecone_vector_db import PineconeLegalVectorDB
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    PineconeLegalVectorDB = None

logger = logging.getLogger(__name__)

# Set up file logging
def _setup_rag_logging():
    """Ensure RAG chain logs are written to file"""
    try:
        from .logging_setup import setup_logging
        setup_logging("module_a.rag_chain")
    except Exception:
        pass  # Fallback to default logging if setup fails

_setup_rag_logging()


class LegalRAGChain:
    """
    Retrieval-Augmented Generation Chain for Legal Explanations
    Combines Vector DB retrieval with Mistral LLM generation
    
    NOTE: This RAG chain uses Pinecone only. ChromaDB integration has been removed.
    Make sure PINECONE_API_KEY is set before initializing.
    """
    
    def __init__(self):
        """Initialize the RAG chain components"""
        logger.info("Initializing Legal RAG Chain...")
        
        # Check if Pinecone is available
        if not PINECONE_AVAILABLE:
            raise ImportError(
                "Pinecone client not installed. "
                "Install with: pip install pinecone-client[grpc]>=3.0.0"
            )
        
        # Check if API key is configured
        if not PINECONE_API_KEY:
            raise ValueError(
                "PINECONE_API_KEY must be set to use the RAG chain. "
                "Set it as an environment variable or in a .env file. "
                "Get your API key from: https://app.pinecone.io/"
            )
        
        # Initialize components
        self.embedder = EmbeddingGenerator()
        
        # Initialize Pinecone vector database
        logger.info("Initializing Pinecone vector database...")
        try:
            self.vector_db = PineconeLegalVectorDB()
            logger.info("✓ Using Pinecone cloud vector database")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise RuntimeError(
                f"Pinecone initialization failed: {e}. "
                "Please check your API key and network connection. "
                "See module_a/PINECONE_SETUP.md for setup instructions."
            )
        
        self.llm = MistralClient()
        
        logger.info("RAG Chain initialized successfully with Pinecone")
    
    def get_vector_db_info(self) -> Dict[str, Any]:
        """
        Get information about the Pinecone vector database
        
        Returns:
            Dictionary with database type, name, and other info
        """
        info = {
            "type": "Pinecone",
            "class_name": type(self.vector_db).__name__,
            "is_pinecone": True,
            "index_name": getattr(self.vector_db, "index_name", "unknown"),
            "vector_count": self.vector_db.get_count()
        }
        
        return info
    
    def run(
        self, 
        query: str, 
        k: int = DEFAULT_RETRIEVAL_K
    ) -> Dict[str, Any]:
        """
        Run the full RAG pipeline
        
        Args:
            query: User's question
            k: Number of chunks to retrieve
            
        Returns:
            Dictionary with 'query', 'explanation', and 'sources'
        """
        logger.info(f"Processing query: {query}")
        
        # Step 1: Retrieve relevant chunks
        logger.info("Step 1: Retrieving relevant laws...")
        query_embedding = self.embedder.generate_embedding(query)
        retrieval_results = self.vector_db.query_with_embedding(
            query_embedding.tolist(), 
            n_results=k
        )
        
        # Process retrieval results into a clean list
        context_chunks = []
        if retrieval_results['documents'][0]:
            for doc, metadata, distance in zip(
                retrieval_results['documents'][0],
                retrieval_results['metadatas'][0],
                retrieval_results['distances'][0]
            ):
                context_chunks.append({
                    'text': doc,
                    'metadata': metadata,
                    'distance': distance
                })
        
        logger.info(f"Retrieved {len(context_chunks)} relevant chunks")
        
        # Step 2: Generate explanation
        logger.info("Step 2: Generating explanation...")
        
        # Format prompt
        prompt = format_rag_prompt(query, context_chunks)
        
        # Call LLM
        try:
            explanation = self.llm.generate_response(
                prompt=prompt,
                system_prompt=LEGAL_SYSTEM_PROMPT
            )
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            explanation = "I apologize, but I encountered an error while generating the explanation. Please try again later."
        
        # Step 3: Format output with improved source handling
        sources = []
        for i, chunk in enumerate(context_chunks):
            source_file = chunk['metadata'].get('source_file', 'Legal Document')
            article_section = chunk['metadata'].get('article_section')

            # If no specific section, try to extract from the text
            if not article_section and 'Article' in chunk['text'][:200]:
                # Try to extract article number from beginning of text
                import re
                match = re.search(r'Article\s+(\d+[A-Za-z]?)', chunk['text'][:200])
                if match:
                    article_section = f"Article {match.group(1)}"

            # Create source entry
            source_entry = {
                'file': source_file,
                'section': article_section or f"Section {i+1}",
                'relevance_score': 1.0 - chunk['distance']  # Approx score
            }
            sources.append(source_entry)

        result = {
            'query': query,
            'explanation': explanation,
            'sources': sources
        }

        logger.info(f"Returning {len(sources)} sources")

        return result
