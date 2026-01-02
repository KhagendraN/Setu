"""
Data models for Module A
Defines structures for document chunks and metadata
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class ChunkMetadata:
    """Metadata for a document chunk"""
    source_file: str
    article_section: Optional[str] = None
    page_numbers: List[int] = field(default_factory=list)
    word_count: int = 0
    char_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChunkMetadata':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class DocumentChunk:
    """Represents a chunk of legal document text"""
    chunk_id: str
    text: str
    metadata: ChunkMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'chunk_id': self.chunk_id,
            'text': self.text,
            'metadata': self.metadata.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentChunk':
        """Create from dictionary"""
        return cls(
            chunk_id=data['chunk_id'],
            text=data['text'],
            metadata=ChunkMetadata.from_dict(data['metadata'])
        )
    
    def __repr__(self) -> str:
        preview = self.text[:100] + "..." if len(self.text) > 100 else self.text
        return f"DocumentChunk(id={self.chunk_id}, words={self.metadata.word_count}, preview='{preview}')"


@dataclass
class ProcessingStats:
    """Statistics from document processing"""
    total_documents: int = 0
    total_chunks: int = 0
    total_words: int = 0
    avg_chunk_size: float = 0.0
    processing_time_seconds: float = 0.0
    documents_processed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
