"""
Public Interface for Module A (Law Explanation)
This module provides a clean API for other parts of the application to use.
"""

import logging
import re
from typing import Dict, List, Any, Optional

from .rag_chain import LegalRAGChain
from .context_analyzer import ConversationContextAnalyzer
from .config import LOG_LEVEL
from .logging_setup import setup_logging

# Configure logging with file output
setup_logging("module_a.interface")
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
            self.context_analyzer = ConversationContextAnalyzer()
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

            # Check for letter generation opportunity
            letter_suggestion = self._detect_letter_generation_opportunity(
                parsed.get('next_steps', ''),
                query
            )
            if letter_suggestion:
                parsed['suggested_action'] = letter_suggestion

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

    def get_explanation_with_context(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Get explanation with conversation context awareness.
        This method intelligently handles:
        1. Non-legal queries (greetings, thanks, etc.)
        2. Independent queries (new topics)
        3. Dependent queries (continuation of conversation)

        Args:
            query: Current user message
            conversation_history: List of previous messages in format:
                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]

        Returns:
            Dict containing structured explanation (same format as get_explanation)
        """
        try:
            # Step 1: Check if this is a non-legal query
            if self.context_analyzer.is_non_legal_query(query):
                logger.info(f"Non-legal query detected: {query[:50]}...")
                return self._generate_non_legal_response(query)

            # Step 2: If no context, treat as new conversation
            if not conversation_history or len(conversation_history) == 0:
                logger.info("No conversation history, processing as new query")
                return self.get_explanation(query)

            # Step 3: Check if the query is independent of previous context
            is_independent = self.context_analyzer.is_independent_query(query, conversation_history)

            if is_independent:
                logger.info("Independent query detected, processing without context")
                return self.get_explanation(query)

            # Step 4: Dependent query - summarize conversation context
            logger.info("Dependent query detected, summarizing conversation context")
            summarized_query = self.context_analyzer.summarize_conversation(query, conversation_history)
            logger.info(f"Summarized query: {summarized_query[:100]}...")

            # Step 5: Send summarized query to RAG pipeline
            result = self.get_explanation(summarized_query)

            # Add metadata indicating context was used
            result['context_used'] = True
            result['original_query'] = query
            result['summarized_query'] = summarized_query

            # Step 6: Check for letter generation opportunity
            letter_suggestion = self._detect_letter_generation_opportunity(
                result.get('next_steps', ''),
                query
            )
            if letter_suggestion:
                result['suggested_action'] = letter_suggestion

            return result

        except Exception as e:
            logger.error(f"Error in get_explanation_with_context: {e}")
            # Fallback to basic explanation
            return self.get_explanation(query)

    def _detect_letter_generation_opportunity(self, next_steps: str, query: str) -> Optional[Dict[str, str]]:
        """
        Detect if the next steps suggest a letter generation opportunity using Mistral LLM.

        Args:
            next_steps: The next steps text from RAG response
            query: Original user query

        Returns:
            Dict with suggestion details if letter generation is applicable, None otherwise
        """
        try:
            # Use Mistral LLM to intelligently detect letter generation needs
            system_prompt = """You are an intelligent assistant that determines if a user's legal query requires generating a formal letter or application.

Analyze the user's query and the recommended next steps to determine:
1. Does this process require submitting a formal letter, application, or written document?
2. What type of document is needed?

Common scenarios requiring letters:
- Citizenship applications
- Property dispute complaints
- Appeals to authorities
- Registration requests
- Formal complaints to government offices
- Petitions for legal matters

Respond in this EXACT format:
REQUIRES_LETTER: YES or NO
LETTER_TYPE: [type of letter/application if YES, otherwise empty]

Examples:
Query: "I want to apply for citizenship of my daughter"
Next Steps: "1. Gather documents 2. Visit Department of Immigration"
Response:
REQUIRES_LETTER: YES
LETTER_TYPE: citizenship application

Query: "What are my property rights?"
Next Steps: "You have the right to own property..."
Response:
REQUIRES_LETTER: NO
LETTER_TYPE:
"""

            prompt = f"""User Query: "{query}"

Recommended Next Steps: "{next_steps}"

Analyze if this requires generating a formal letter or application:"""

            response = self.context_analyzer.llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1  # Low temperature for consistent classification
            )

            # Parse the response
            lines = response.strip().split('\n')
            requires_letter = False
            letter_type = None

            for line in lines:
                if 'REQUIRES_LETTER:' in line:
                    requires_letter = 'YES' in line.upper()
                elif 'LETTER_TYPE:' in line and ':' in line:
                    letter_type = line.split(':', 1)[1].strip()

            logger.info(f"Letter detection - Query: '{query[:50]}...' Requires: {requires_letter}, Type: {letter_type}")

            if requires_letter and letter_type:
                return {
                    "action": "generate_letter",
                    "description": query,
                    "letter_type": letter_type,
                    "prompt": f"Would you like me to help you draft a {letter_type}?"
                }

            return None

        except Exception as e:
            logger.error(f"Error in letter generation detection: {e}")
            # Fallback to keyword-based detection
            return self._fallback_keyword_detection(next_steps, query)

    def _fallback_keyword_detection(self, next_steps: str, query: str) -> Optional[Dict[str, str]]:
        """Fallback keyword-based detection if LLM fails"""
        letter_keywords = [
            'write', 'letter', 'application', 'submit', 'file', 'petition',
            'request', 'appeal', 'complaint', 'notice', 'draft', 'apply'
        ]

        intent_keywords = [
            'apply for', 'want to apply', 'need to apply', 'how to apply',
            'get citizenship', 'obtain', 'register', 'request for'
        ]

        next_steps_lower = next_steps.lower()
        query_lower = query.lower()

        has_letter_keyword = any(keyword in next_steps_lower or keyword in query_lower for keyword in letter_keywords)
        has_intent_keyword = any(keyword in query_lower for keyword in intent_keywords)

        if has_letter_keyword or has_intent_keyword:
            letter_type = None
            if 'citizenship' in query_lower or 'citizenship' in next_steps_lower:
                letter_type = "citizenship application"
            elif 'complaint' in next_steps_lower or 'complaint' in query_lower:
                letter_type = "formal complaint"
            elif 'appeal' in next_steps_lower or 'appeal' in query_lower:
                letter_type = "appeal"
            elif 'application' in next_steps_lower or 'application' in query_lower:
                letter_type = "application"
            else:
                letter_type = "formal letter"

            return {
                "action": "generate_letter",
                "description": query,
                "letter_type": letter_type,
                "prompt": f"Would you like me to help you draft a {letter_type}?"
            }

        return None

    def _generate_non_legal_response(self, query: str) -> Dict[str, Any]:
        """
        Generate a friendly response for non-legal queries (greetings, thanks, etc.)

        Args:
            query: The non-legal message

        Returns:
            Response dict matching the standard explanation format
        """
        # Detect type of non-legal query
        query_lower = query.lower()

        if any(greeting in query_lower for greeting in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']):
            response = "Hello! I'm here to help you with legal questions. Feel free to ask me anything about laws, regulations, or legal procedures."
        elif any(thanks in query_lower for thanks in ['thank', 'thanks', 'appreciate']):
            response = "You're welcome! I'm glad I could help. If you have any more legal questions, feel free to ask."
        elif any(bye in query_lower for bye in ['bye', 'goodbye', 'see you']):
            response = "Goodbye! Feel free to come back anytime you have legal questions."
        else:
            response = "I'm here to assist you with legal matters. How can I help you today?"

        return {
            "summary": response,
            "key_point": "",
            "explanation": response,
            "next_steps": "",
            "sources": [],
            "query": query,
            "is_non_legal": True,
            "context_used": False
        }

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
