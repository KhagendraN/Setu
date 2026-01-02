"""
Text chunking module
Intelligently splits legal documents into meaningful chunks
"""

import re
import logging
from typing import List, Tuple, Optional, Dict
from pathlib import Path

from .config import (
    CHUNK_SIZE_MIN_WORDS,
    CHUNK_SIZE_MAX_WORDS,
    CHUNK_SIZE_TARGET_WORDS,
    CHUNK_OVERLAP_WORDS,
    COMPILED_SECTION_PATTERNS
)
from .models import DocumentChunk, ChunkMetadata

logger = logging.getLogger(__name__)


class LegalDocumentChunker:
    """Chunks legal documents with section/article awareness"""
    
    def __init__(
        self,
        min_words: int = CHUNK_SIZE_MIN_WORDS,
        max_words: int = CHUNK_SIZE_MAX_WORDS,
        target_words: int = CHUNK_SIZE_TARGET_WORDS,
        overlap_words: int = CHUNK_OVERLAP_WORDS
    ):
        """
        Initialize chunker
        
        Args:
            min_words: Minimum words per chunk
            max_words: Maximum words per chunk
            target_words: Target words per chunk
            overlap_words: Words to overlap between chunks
        """
        self.min_words = min_words
        self.max_words = max_words
        self.target_words = target_words
        self.overlap_words = overlap_words
    
    def chunk_document(
        self,
        text: str,
        source_file: str,
        pages_data: List[Dict[str, any]] = None
    ) -> List[DocumentChunk]:
        """
        Chunk a document into meaningful pieces
        
        Args:
            text: Full document text
            source_file: Source filename
            pages_data: Optional page data for page number tracking
            
        Returns:
            List of DocumentChunk objects
        """
        logger.info(f"Chunking document: {source_file}")
        
        # First, try to split by sections/articles
        sections = self._split_by_sections(text)
        
        # Then chunk each section appropriately
        all_chunks = []
        chunk_counter = 0
        
        for section_title, section_text in sections:
            section_chunks = self._chunk_section(
                section_text,
                section_title,
                source_file,
                chunk_counter
            )
            all_chunks.extend(section_chunks)
            chunk_counter += len(section_chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {source_file}")
        
        return all_chunks
    
    def _split_by_sections(self, text: str) -> List[Tuple[Optional[str], str]]:
        """
        Split text by sections/articles
        
        Returns:
            List of (section_title, section_text) tuples
        """
        sections = []
        current_section = None
        current_text = []
        
        lines = text.split('\n')
        
        for line in lines:
            # Check if line contains a section marker
            section_match = self._detect_section(line)
            
            if section_match:
                # Save previous section if it has content
                if current_text:
                    sections.append((current_section, '\n'.join(current_text)))
                    current_text = []
                
                # Start new section with this title
                current_section = section_match
                # Include the section header line in the text
                current_text = [line]
            else:
                current_text.append(line)
        
        # Add final section
        if current_text:
            sections.append((current_section, '\n'.join(current_text)))
        
        # If no sections detected, return entire text as one section
        if len(sections) == 0:
            sections.append((None, text))
        
        logger.info(f"Detected {len(sections)} sections in document")
        
        return sections
    
    def _detect_section(self, line: str) -> Optional[str]:
        """
        Detect if a line contains a section/article marker
        
        Returns:
            Section title if detected, None otherwise
        """
        for pattern in COMPILED_SECTION_PATTERNS:
            match = pattern.search(line)
            if match:
                # For numbered sections like "11. Citizenship:", return "11. Citizenship"
                if len(match.groups()) >= 2:
                    # Pattern has both number and title
                    return f"{match.group(1)}. {match.group(2)}"
                else:
                    # Pattern has just the identifier, return the full match
                    return match.group(0)
        
        return None
    
    def _chunk_section(
        self,
        section_text: str,
        section_title: Optional[str],
        source_file: str,
        start_counter: int
    ) -> List[DocumentChunk]:
        """
        Chunk a single section into appropriate sizes
        
        Args:
            section_text: Text of the section
            section_title: Title/identifier of the section
            source_file: Source filename
            start_counter: Starting chunk number
            
        Returns:
            List of chunks for this section
        """
        words = section_text.split()
        word_count = len(words)
        
        # If section is small enough, keep as single chunk
        if word_count <= self.max_words:
            chunk = self._create_chunk(
                text=section_text,
                chunk_id=f"{Path(source_file).stem}_chunk_{start_counter:04d}",
                source_file=source_file,
                article_section=section_title
            )
            return [chunk]
        
        # Otherwise, split into multiple chunks
        chunks = []
        start_idx = 0
        chunk_num = start_counter
        max_iterations = word_count  # Safety limit to prevent infinite loops
        iteration_count = 0
        
        while start_idx < word_count and iteration_count < max_iterations:
            iteration_count += 1
            
            # Calculate end index
            end_idx = min(start_idx + self.target_words, word_count)
            
            # Ensure we make progress (end_idx must be greater than start_idx)
            if end_idx <= start_idx:
                logger.warning(f"Chunking issue: end_idx ({end_idx}) <= start_idx ({start_idx}), breaking")
                break
            
            # Try to find a good break point (sentence end)
            if end_idx < word_count:
                # Look for sentence endings near target
                chunk_words = words[start_idx:end_idx]
                chunk_text = ' '.join(chunk_words)
                
                # Find last sentence ending
                last_period = max(
                    chunk_text.rfind('. '),
                    chunk_text.rfind('! '),
                    chunk_text.rfind('? ')
                )
                
                if last_period > len(chunk_text) * 0.5:  # At least 50% through
                    # Adjust end_idx to sentence boundary
                    words_before_period = chunk_text[:last_period + 1].split()
                    new_end_idx = start_idx + len(words_before_period)
                    # Only use the new end_idx if it's actually moving forward
                    if new_end_idx > start_idx:
                        end_idx = new_end_idx
            
            # Create chunk
            chunk_words = words[start_idx:end_idx]
            chunk_text = ' '.join(chunk_words)
            
            chunk = self._create_chunk(
                text=chunk_text,
                chunk_id=f"{Path(source_file).stem}_chunk_{chunk_num:04d}",
                source_file=source_file,
                article_section=section_title
            )
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            # Ensure we always move forward by at least 1 word
            overlap = min(self.overlap_words, end_idx - start_idx - 1)
            next_start_idx = end_idx - overlap
            
            # Safety check: ensure we're making progress
            if next_start_idx <= start_idx:
                next_start_idx = start_idx + 1
            
            start_idx = next_start_idx
            chunk_num += 1
        
        if iteration_count >= max_iterations:
            logger.warning(f"Hit max iterations ({max_iterations}) while chunking section")
        
        return chunks
    
    def _create_chunk(
        self,
        text: str,
        chunk_id: str,
        source_file: str,
        article_section: Optional[str] = None
    ) -> DocumentChunk:
        """Create a DocumentChunk object"""
        words = text.split()
        
        metadata = ChunkMetadata(
            source_file=source_file,
            article_section=article_section,
            word_count=len(words),
            char_count=len(text)
        )
        
        return DocumentChunk(
            chunk_id=chunk_id,
            text=text,
            metadata=metadata
        )
