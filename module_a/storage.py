"""
Storage module for saving and loading processed chunks
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from .models import DocumentChunk, ProcessingStats

logger = logging.getLogger(__name__)


class ChunkStorage:
    """Handles saving and loading of document chunks"""
    
    def __init__(self, output_file: Path):
        """
        Initialize storage
        
        Args:
            output_file: Path to output JSON file
        """
        self.output_file = output_file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save_chunks(
        self,
        chunks: List[DocumentChunk],
        stats: ProcessingStats = None
    ) -> None:
        """
        Save chunks to JSON file
        
        Args:
            chunks: List of DocumentChunk objects
            stats: Optional processing statistics
        """
        logger.info(f"Saving {len(chunks)} chunks to {self.output_file}")
        
        # Convert chunks to dictionaries
        chunks_data = [chunk.to_dict() for chunk in chunks]
        
        # Prepare output structure
        output = {
            'metadata': {
                'total_chunks': len(chunks),
                'version': '1.0',
            },
            'chunks': chunks_data
        }
        
        # Add stats if provided
        if stats:
            output['metadata']['processing_stats'] = stats.to_dict()
        
        # Save to file with pretty formatting
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully saved chunks to {self.output_file}")
        
        # Also save a summary file
        self._save_summary(chunks, stats)
    
    def _save_summary(
        self,
        chunks: List[DocumentChunk],
        stats: ProcessingStats = None
    ) -> None:
        """Save a human-readable summary"""
        summary_file = self.output_file.parent / "chunks_summary.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DOCUMENT CHUNKS SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            
            if stats:
                f.write(f"Total Documents Processed: {stats.total_documents}\n")
                f.write(f"Total Chunks Created: {stats.total_chunks}\n")
                f.write(f"Total Words: {stats.total_words}\n")
                f.write(f"Average Chunk Size: {stats.avg_chunk_size:.1f} words\n")
                f.write(f"Processing Time: {stats.processing_time_seconds:.2f} seconds\n")
                f.write(f"\nDocuments:\n")
                for doc in stats.documents_processed:
                    f.write(f"  - {doc}\n")
                f.write("\n")
            
            f.write("-" * 80 + "\n")
            f.write("SAMPLE CHUNKS (First 5)\n")
            f.write("-" * 80 + "\n\n")
            
            for i, chunk in enumerate(chunks[:5], 1):
                f.write(f"Chunk {i}: {chunk.chunk_id}\n")
                f.write(f"Source: {chunk.metadata.source_file}\n")
                f.write(f"Section: {chunk.metadata.article_section or 'N/A'}\n")
                f.write(f"Words: {chunk.metadata.word_count}\n")
                f.write(f"Preview: {chunk.text[:200]}...\n")
                f.write("\n" + "-" * 80 + "\n\n")
        
        logger.info(f"Summary saved to {summary_file}")
    
    def load_chunks(self) -> List[DocumentChunk]:
        """
        Load chunks from JSON file
        
        Returns:
            List of DocumentChunk objects
        """
        logger.info(f"Loading chunks from {self.output_file}")
        
        if not self.output_file.exists():
            raise FileNotFoundError(f"Chunks file not found: {self.output_file}")
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = [DocumentChunk.from_dict(chunk_data) for chunk_data in data['chunks']]
        
        logger.info(f"Loaded {len(chunks)} chunks")
        
        return chunks
    
    def validate_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """
        Validate chunks before saving
        
        Args:
            chunks: List of chunks to validate
            
        Returns:
            True if valid, raises exception otherwise
        """
        if not chunks:
            raise ValueError("No chunks to save")
        
        for i, chunk in enumerate(chunks):
            if not chunk.text or not chunk.text.strip():
                raise ValueError(f"Chunk {i} has empty text")
            
            if not chunk.chunk_id:
                raise ValueError(f"Chunk {i} has no ID")
            
            if chunk.metadata.word_count == 0:
                raise ValueError(f"Chunk {i} has zero word count")
        
        logger.info(f"Validated {len(chunks)} chunks successfully")
        return True
