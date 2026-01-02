"""
Main document processing pipeline
Orchestrates extraction, cleaning, and chunking of legal documents
"""

import logging
import time
from pathlib import Path
from typing import List

from .config import LAW_DIR, CHUNKS_OUTPUT_FILE, LOG_LEVEL, LOG_FORMAT
from .extractors import PDFExtractor
from .cleaners import TextCleaner
from .chunkers import LegalDocumentChunker
from .storage import ChunkStorage
from .models import DocumentChunk, ProcessingStats

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Main pipeline for processing legal documents"""
    
    def __init__(self):
        """Initialize processor with all components"""
        self.extractor = PDFExtractor()
        self.cleaner = TextCleaner()
        self.chunker = LegalDocumentChunker()
        self.storage = ChunkStorage(CHUNKS_OUTPUT_FILE)
    
    def process_all_documents(self) -> ProcessingStats:
        """
        Process all PDF documents in the law directory
        
        Returns:
            Processing statistics
        """
        logger.info("=" * 80)
        logger.info("Starting document processing pipeline")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Get all PDF files
        pdf_files = list(LAW_DIR.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in {LAW_DIR}")
        
        # Process each document
        all_chunks: List[DocumentChunk] = []
        total_words = 0
        
        for pdf_file in pdf_files:
            logger.info(f"\n{'=' * 80}")
            logger.info(f"Processing: {pdf_file.name}")
            logger.info(f"{'=' * 80}")
            
            try:
                chunks = self.process_single_document(pdf_file)
                all_chunks.extend(chunks)
                
                # Calculate words
                doc_words = sum(chunk.metadata.word_count for chunk in chunks)
                total_words += doc_words
                
                logger.info(f"✓ Created {len(chunks)} chunks ({doc_words} words) from {pdf_file.name}")
                
            except Exception as e:
                logger.error(f"✗ Failed to process {pdf_file.name}: {e}")
                continue
        
        # Calculate statistics
        processing_time = time.time() - start_time
        avg_chunk_size = total_words / len(all_chunks) if all_chunks else 0
        
        stats = ProcessingStats(
            total_documents=len(pdf_files),
            total_chunks=len(all_chunks),
            total_words=total_words,
            avg_chunk_size=avg_chunk_size,
            processing_time_seconds=processing_time,
            documents_processed=[f.name for f in pdf_files]
        )
        
        # Validate and save chunks
        logger.info(f"\n{'=' * 80}")
        logger.info("Validating and saving chunks...")
        logger.info(f"{'=' * 80}")
        
        self.storage.validate_chunks(all_chunks)
        self.storage.save_chunks(all_chunks, stats)
        
        # Print summary
        self._print_summary(stats)
        
        return stats
    
    def process_single_document(self, pdf_path: Path) -> List[DocumentChunk]:
        """
        Process a single PDF document
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of chunks from this document
        """
        # Step 1: Extract text from PDF
        logger.info("Step 1: Extracting text from PDF...")
        pages_data = self.extractor.extract_from_file(pdf_path)
        
        if not pages_data:
            raise ValueError(f"No text extracted from {pdf_path.name}")
        
        # Step 2: Clean the text
        logger.info("Step 2: Cleaning extracted text...")
        cleaned_text = self.cleaner.clean_pages(pages_data)
        
        if not cleaned_text:
            raise ValueError(f"No text remaining after cleaning {pdf_path.name}")
        
        # Step 3: Chunk the text
        logger.info("Step 3: Chunking text into meaningful pieces...")
        chunks = self.chunker.chunk_document(
            text=cleaned_text,
            source_file=pdf_path.name,
            pages_data=pages_data
        )
        
        return chunks
    
    def _print_summary(self, stats: ProcessingStats):
        """Print processing summary"""
        logger.info(f"\n{'=' * 80}")
        logger.info("PROCESSING COMPLETE!")
        logger.info(f"{'=' * 80}")
        logger.info(f"Documents Processed: {stats.total_documents}")
        logger.info(f"Total Chunks Created: {stats.total_chunks}")
        logger.info(f"Total Words: {stats.total_words:,}")
        logger.info(f"Average Chunk Size: {stats.avg_chunk_size:.1f} words")
        logger.info(f"Processing Time: {stats.processing_time_seconds:.2f} seconds")
        logger.info(f"\nOutput saved to: {CHUNKS_OUTPUT_FILE}")
        logger.info(f"Summary saved to: {CHUNKS_OUTPUT_FILE.parent / 'chunks_summary.txt'}")
        logger.info(f"{'=' * 80}\n")


def main():
    """Main entry point"""
    try:
        processor = DocumentProcessor()
        stats = processor.process_all_documents()
        
        print("\n✓ Processing completed successfully!")
        print(f"✓ Created {stats.total_chunks} chunks from {stats.total_documents} documents")
        print(f"✓ Output: {CHUNKS_OUTPUT_FILE}")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        print(f"\n✗ Processing failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
