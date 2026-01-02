"""
Text cleaning and normalization module
Removes headers, footers, page numbers, and fixes formatting
"""

import re
import logging
from typing import List, Dict

from .config import CLEANING_PATTERNS

logger = logging.getLogger(__name__)


class TextCleaner:
    """Cleans and normalizes extracted text"""
    
    def __init__(self):
        """Initialize text cleaner with compiled patterns"""
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile all regex patterns for efficiency"""
        compiled = {}
        for category, patterns in CLEANING_PATTERNS.items():
            compiled[category] = [re.compile(p, re.MULTILINE | re.IGNORECASE) for p in patterns]
        return compiled
    
    def clean_text(self, text: str) -> str:
        """
        Apply all cleaning operations to text
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove page numbers
        text = self._remove_page_numbers(text)
        
        # Remove headers and footers
        text = self._remove_headers_footers(text)
        
        # Remove table of contents patterns
        text = self._remove_toc_patterns(text)
        
        # Fix line breaks and whitespace
        text = self._normalize_whitespace(text)
        
        # Additional cleaning
        text = self._additional_cleaning(text)
        
        return text.strip()
    
    def _remove_page_numbers(self, text: str) -> str:
        """Remove page numbers"""
        for pattern in self.patterns['page_numbers']:
            text = pattern.sub('', text)
        return text
    
    def _remove_headers_footers(self, text: str) -> str:
        """Remove common headers and footers"""
        for pattern in self.patterns['headers_footers']:
            text = pattern.sub('', text)
        return text
    
    def _remove_toc_patterns(self, text: str) -> str:
        """Remove table of contents patterns"""
        for pattern in self.patterns['toc_patterns']:
            text = pattern.sub('', text)
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Fix excessive whitespace and line breaks"""
        # Replace multiple blank lines with double newline
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Replace multiple spaces/tabs with single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Fix broken words (hyphenation at line breaks)
        text = re.sub(r'-\s*\n\s*', '', text)
        
        # Normalize line breaks within paragraphs
        # Keep double line breaks (paragraph separators)
        lines = text.split('\n')
        normalized_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                # Check if this line and next are both non-empty (within paragraph)
                if i < len(lines) - 1 and lines[i + 1].strip():
                    # Check if line ends with sentence-ending punctuation
                    if not line.endswith(('.', '!', '?', ':', ';')):
                        # Join with next line
                        normalized_lines.append(line + ' ')
                    else:
                        normalized_lines.append(line + '\n')
                else:
                    normalized_lines.append(line + '\n')
        
        text = ''.join(normalized_lines)
        
        return text
    
    def _additional_cleaning(self, text: str) -> str:
        """Additional cleaning operations"""
        # Remove standalone numbers that might be page/section numbers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Remove very short lines (likely artifacts)
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if len(line.strip()) > 3 or line.strip() == '']
        text = '\n'.join(cleaned_lines)
        
        # Normalize unicode characters
        text = text.replace('\u2019', "'")  # Right single quotation mark
        text = text.replace('\u2018', "'")  # Left single quotation mark
        text = text.replace('\u201c', '"')  # Left double quotation mark
        text = text.replace('\u201d', '"')  # Right double quotation mark
        text = text.replace('\u2013', '-')  # En dash
        text = text.replace('\u2014', '--')  # Em dash
        
        return text
    
    def clean_pages(self, pages_data: List[Dict[str, any]]) -> str:
        """
        Clean text from multiple pages and combine
        
        Args:
            pages_data: List of dicts with 'page_number' and 'text'
            
        Returns:
            Combined cleaned text
        """
        combined_text = []
        
        for page_data in pages_data:
            page_text = page_data.get('text', '')
            if page_text:
                cleaned = self.clean_text(page_text)
                if cleaned:
                    combined_text.append(cleaned)
        
        # Join pages with double newline
        full_text = '\n\n'.join(combined_text)
        
        logger.info(f"Cleaned {len(pages_data)} pages into {len(full_text)} characters")
        
        return full_text
