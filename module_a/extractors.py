"""
PDF text extraction module
Handles extraction from legal PDF documents
"""

import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from .config import PDF_EXTRACTION_METHOD, PDF_FALLBACK_METHOD

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extracts text from PDF files with multiple extraction methods"""
    
    def __init__(self, method: str = PDF_EXTRACTION_METHOD):
        """
        Initialize PDF extractor
        
        Args:
            method: Extraction method ('pdfplumber' or 'pypdf2')
        """
        self.method = method
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """Check if required libraries are available"""
        if self.method == "pdfplumber" and not PDFPLUMBER_AVAILABLE:
            logger.warning("pdfplumber not available, falling back to PyPDF2")
            self.method = "pypdf2"
        
        if self.method == "pypdf2" and not PYPDF2_AVAILABLE:
            raise ImportError("No PDF extraction library available. Install pdfplumber or PyPDF2")
    
    def extract_from_file(self, pdf_path: Path) -> List[Dict[str, any]]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dicts with 'page_number' and 'text' keys
        """
        logger.info(f"Extracting text from {pdf_path.name} using {self.method}")
        
        try:
            if self.method == "pdfplumber":
                return self._extract_with_pdfplumber(pdf_path)
            else:
                return self._extract_with_pypdf2(pdf_path)
        except Exception as e:
            logger.error(f"Extraction failed with {self.method}: {e}")
            # Try fallback method
            if self.method == "pdfplumber" and PYPDF2_AVAILABLE:
                logger.info("Trying fallback method: PyPDF2")
                return self._extract_with_pypdf2(pdf_path)
            elif self.method == "pypdf2" and PDFPLUMBER_AVAILABLE:
                logger.info("Trying fallback method: pdfplumber")
                return self._extract_with_pdfplumber(pdf_path)
            else:
                raise
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> List[Dict[str, any]]:
        """Extract using pdfplumber (better for complex layouts)"""
        pages_data = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    pages_data.append({
                        'page_number': page_num,
                        'text': text
                    })
                else:
                    logger.warning(f"No text extracted from page {page_num}")
        
        logger.info(f"Extracted {len(pages_data)} pages from {pdf_path.name}")
        return pages_data
    
    def _extract_with_pypdf2(self, pdf_path: Path) -> List[Dict[str, any]]:
        """Extract using PyPDF2 (fallback method)"""
        pages_data = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                if text:
                    pages_data.append({
                        'page_number': page_num,
                        'text': text
                    })
                else:
                    logger.warning(f"No text extracted from page {page_num}")
        
        logger.info(f"Extracted {len(pages_data)} pages from {pdf_path.name}")
        return pages_data
    
    def extract_from_directory(self, directory: Path) -> Dict[str, List[Dict[str, any]]]:
        """
        Extract text from all PDFs in a directory
        
        Args:
            directory: Path to directory containing PDFs
            
        Returns:
            Dict mapping filename to list of page data
        """
        results = {}
        pdf_files = list(directory.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {directory}")
        
        for pdf_file in pdf_files:
            try:
                results[pdf_file.name] = self.extract_from_file(pdf_file)
            except Exception as e:
                logger.error(f"Failed to extract {pdf_file.name}: {e}")
                results[pdf_file.name] = []
        
        return results
