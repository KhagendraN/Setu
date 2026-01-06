"""
Pinecone Vector Database Module
Handles all Pinecone-related functionality for Module A
"""

from .pinecone_vector_db import PineconeLegalVectorDB
from ..logging_setup import setup_logging, get_pinecone_logger

__all__ = [
    'PineconeLegalVectorDB',
]
