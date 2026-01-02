"""
Integration Example for Module A
This script demonstrates how other team members can use the Law Explanation module.
"""

import os
import json
from dotenv import load_dotenv
from module_a import LawExplanationAPI

# Load env vars (MISTRAL_API_KEY)
load_dotenv()

def main():
    print("Initializing Law Explanation Engine...")
    
    # 1. Initialize the API
    # This might take a few seconds to load the embedding model and vector DB
    try:
        legal_api = LawExplanationAPI()
    except Exception as e:
        print(f"Initialization failed: {e}")
        print("Did you set MISTRAL_API_KEY in .env?")
        return

    # 2. Define a user query
    query = "What are the conditions for divorce?"
    print(f"\nQuery: {query}\n")

    # 3. Get the explanation
    print("Generating answer...")
    response = legal_api.get_explanation(query)

    # 4. Use the structured data
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print("-" * 50)
        print(f"SUMMARY: {response['summary']}")
        print("-" * 50)
        print(f"KEY POINT: {response['key_point']}")
        print("-" * 50)
        print(f"EXPLANATION:\n{response['explanation']}")
        print("-" * 50)
        print(f"NEXT STEPS:\n{response['next_steps']}")
        print("-" * 50)
        
        print("\nSources Used:")
        for source in response['sources']:
            print(f"- {source['section']} ({source['file']})")

    # 5. Example: Search only (no LLM)
    print("\n" + "="*50 + "\n")
    print("Searching for 'cyber crime' laws (no LLM)...")
    sources = legal_api.get_sources_only("cyber crime punishment")
    for s in sources:
        print(f"- {s['section']}: {s['text'][:100]}...")

if __name__ == "__main__":
    main()
