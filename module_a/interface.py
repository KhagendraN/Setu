"""
Public Interface for Module A (Law Explanation)
This module provides a clean API for other parts of the application to use.
"""

import logging
import re
from typing import Dict, List, Any, Optional

from .rag_chain import LegalRAGChain
from .config import LOG_LEVEL

# Configure logging
logger = logging.getLogger(__name__)

class LawExplanationAPI:
    """
    Main API for the Law Explanation module.
    Hides the complexity of RAG, Vector DB, and LLM interactions.
    """
    
    def __init__(self):
        """Initialize the Law Explanation engine"""
        logger.info("Initializing LawExplanationAPI...")
        try:
            self.rag_chain = LegalRAGChain()
            logger.info("LawExplanationAPI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LawExplanationAPI: {e}")
            raise

    def get_explanation(self, query: str) -> Dict[str, Any]:
        """
        Get a structured legal explanation for a user query.
        
        Args:
            query: The user's question (e.g., "How to get citizenship?")
            
        Returns:
            Dict containing:
            - summary: Brief answer
            - key_point: Direct quote from law
            - explanation: Detailed explanation
            - next_steps: Actionable advice
            - sources: List of source documents
            - raw_response: The full LLM text (fallback)
        """
        try:
            # Run the RAG pipeline
            result = self.rag_chain.run(query)
            raw_text = result['explanation']
            
            # Parse the structured response
            parsed = self._parse_response(raw_text)
            
            # Add metadata and sources
            parsed['sources'] = result.get('sources', [])
            parsed['query'] = query
            parsed['raw_response'] = raw_text
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return {
                "error": str(e),
                "summary": "I encountered an error while processing your request.",
                "explanation": "Please try again later.",
                "sources": []
            }

    def _parse_response(self, text: str) -> Dict[str, str]:
        """
        Parse the markdown-formatted LLM response into structured fields.
        Expected format:
        **Summary** ... **Key Legal Point** ... **Explanation** ... **Next Steps** ...
        """
        parsed = {
            "summary": "",
            "key_point": "",
            "explanation": "",
            "next_steps": ""
        }
        
        # Regex patterns to extract sections
        # We use re.DOTALL to match across newlines
        patterns = {
            "summary": r"\*\*Summary\*\*\s*(.*?)\s*(?=\*\*Key Legal Point\*\*|$)",
            "key_point": r"\*\*Key Legal Point\*\*\s*(.*?)\s*(?=\*\*Explanation\*\*|$)",
            "explanation": r"\*\*Explanation\*\*\s*(.*?)\s*(?=\*\*Next Steps\*\*|$)",
            "next_steps": r"\*\*Next Steps\*\*\s*(.*?)\s*$"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                parsed[key] = match.group(1).strip()
            else:
                # Fallback: if parsing fails, try to be smart or leave empty
                pass
                
        # If parsing completely failed (e.g. LLM didn't follow format), 
        # put everything in explanation
        if not any(parsed.values()):
            parsed["explanation"] = text
            
        return parsed

    def get_sources_only(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant legal sources without generating an explanation.
        Useful for "Search Laws" feature.
        """
        # We can access the vector db directly from the chain
        embedding = self.rag_chain.embedder.generate_embedding(query)
        results = self.rag_chain.vector_db.query_with_embedding(
            embedding.tolist(), 
            n_results=k
        )
        
        sources = []
        if results['documents'][0]:
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                sources.append({
                    'text': doc,
                    'file': metadata.get('source_file'),
                    'section': metadata.get('article_section'),
                    'relevance': 1.0 - distance
                })
        return sources
