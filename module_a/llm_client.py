"""
Mistral API Client Module
Handles interaction with Mistral AI models
"""

import os
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

try:
    # New SDK structure (v1.0+)
    from mistralai import Mistral
    from mistralai.models import UserMessage, SystemMessage
    MISTRAL_AVAILABLE = True
except ImportError as e:
    print(f"DEBUG: Mistral import failed: {e}")
    MISTRAL_AVAILABLE = False

from .config import MISTRAL_MODEL, MISTRAL_API_KEY_ENV_VAR

logger = logging.getLogger(__name__)

# Load environment variables from .env file if present
load_dotenv()


class MistralClient:
    """Client for interacting with Mistral API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = MISTRAL_MODEL):
        """
        Initialize Mistral client
        
        Args:
            api_key: Mistral API key (optional, defaults to env var)
            model: Model to use (default: mistral-tiny)
        """
        if not MISTRAL_AVAILABLE:
            raise ImportError(
                "mistralai library not installed or incompatible. "
                "Install with: pip install mistralai"
            )
            
        self.api_key = api_key or os.getenv(MISTRAL_API_KEY_ENV_VAR)
        self.model = model
        
        if not self.api_key:
            logger.warning(f"Mistral API key not found in environment variable {MISTRAL_API_KEY_ENV_VAR}")
            
        self.client = None
        if self.api_key:
            try:
                self.client = Mistral(api_key=self.api_key)
                logger.info(f"Mistral client initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Mistral client: {e}")
    
    def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            temperature: Creativity parameter (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        if not self.client:
            raise ValueError("Mistral client not initialized. Check API key.")
            
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
            
        messages.append(UserMessage(content=prompt))
        
        try:
            logger.info(f"Sending request to Mistral API (model: {self.model})")
            
            # Use the new chat.complete API
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            
            response_text = chat_response.choices[0].message.content
            logger.info("Received response from Mistral API")
            return response_text
            
        except Exception as e:
            logger.error(f"Mistral API call failed: {e}")
            raise
