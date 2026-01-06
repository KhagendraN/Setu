"""
Quick script to check which vector database is being used
Run this to verify if Pinecone or ChromaDB is active
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from module_a.rag_chain import LegalRAGChain
from module_a.config import PINECONE_API_KEY

# Configure logging to see the initialization messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 80)
    print("Vector Database Checker")
    print("=" * 80)
    print()
    
    # Check environment
    print("Environment Check:")
    print("-" * 80)
    api_key_set = bool(PINECONE_API_KEY)
    api_key_from_env = bool(os.getenv("PINECONE_API_KEY"))
    
    print(f"PINECONE_API_KEY in config: {'✓ Set' if api_key_set else '✗ Not set'}")
    print(f"PINECONE_API_KEY in environment: {'✓ Set' if api_key_from_env else '✗ Not set'}")
    
    if api_key_set:
        # Mask the API key for security
        masked_key = PINECONE_API_KEY[:8] + "..." + PINECONE_API_KEY[-4:] if len(PINECONE_API_KEY) > 12 else "***"
        print(f"API Key (masked): {masked_key}")
    else:
        print("\n⚠️  TROUBLESHOOTING:")
        print("-" * 80)
        print("The API key is not being detected. Here are possible reasons:")
        print()
        print("1. Environment variable not set in current session:")
        print("   PowerShell: $env:PINECONE_API_KEY='your-key'")
        print("   CMD:        set PINECONE_API_KEY=your-key")
        print()
        print("2. .env file not found or not loaded:")
        print("   Create a .env file in project root with:")
        print("   PINECONE_API_KEY=your-key")
        print()
        print("3. Environment variable set in different terminal:")
        print("   Set it in the SAME terminal where you run the application")
        print()
        print("4. Need to restart application after setting:")
        print("   After setting the variable, restart your server/application")
    print()
    
    # Initialize RAG chain (this will show which DB is used)
    print("Initializing RAG Chain...")
    print("-" * 80)
    try:
        rag_chain = LegalRAGChain()
        
        # Get database info
        db_info = rag_chain.get_vector_db_info()
        
        print()
        print("=" * 80)
        print("RESULT:")
        print("=" * 80)
        print(f"Database Type: {db_info['type']}")
        print(f"Class Name: {db_info['class_name']}")
        print(f"Is Pinecone: {db_info['is_pinecone']}")
        
        if db_info['is_pinecone']:
            print(f"Pinecone Index: {db_info.get('index_name', 'N/A')}")
            print(f"Vector Count: {db_info.get('vector_count', 0)}")
        else:
            print(f"ChromaDB Directory: {db_info.get('persist_directory', 'N/A')}")
            print(f"Collection Name: {db_info.get('collection_name', 'N/A')}")
            print(f"Vector Count: {db_info.get('vector_count', 0)}")
        
        print()
        if db_info['is_pinecone']:
            print("✓ SUCCESS: Using Pinecone cloud vector database")
        else:
            print("ℹ INFO: Using ChromaDB local vector database")
            print("   (To use Pinecone, set PINECONE_API_KEY environment variable)")
        
        print("=" * 80)
        return 0
        
    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR:")
        print("=" * 80)
        print(f"Failed to initialize: {e}")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit(main())
