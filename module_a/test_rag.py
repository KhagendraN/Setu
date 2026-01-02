"""
Test script for RAG Chain
Runs end-to-end tests with sample queries
"""

import os
import logging
from dotenv import load_dotenv

# Load env vars before importing modules that might use them
load_dotenv()

from module_a.rag_chain import LegalRAGChain
from module_a.config import LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def main():
    """Run RAG chain tests"""
    print("=" * 80)
    print("Testing Nepal Justice Weaver - RAG Chain")
    print("=" * 80)
    
    # Check API key
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("\n✗ Error: MISTRAL_API_KEY not found!")
        print("Please set it in .env file or environment variable.")
        print("Example: export MISTRAL_API_KEY='your_key_here'")
        return
    
    try:
        # Initialize chain
        print("\nInitializing RAG Chain...")
        rag = LegalRAGChain()
        
        # Test queries
        test_queries = [
            "I am a single mother, how to get citizenship for my child?",
            "Can daughters inherit property like sons?",
            "What are the fundamental rights regarding equality?"
        ]
        
        for query in test_queries:
            print(f"\n\n{'=' * 80}")
            print(f"QUERY: {query}")
            print(f"{'=' * 80}")
            
            result = rag.run(query)
            
            print(f"\nEXPLANATION:\n{result['explanation']}")
            
            print("\nSOURCES:")
            for source in result['sources']:
                print(f"- {source['section']} ({source['file']})")
                
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n✗ Test failed: {e}")


if __name__ == "__main__":
    main()
