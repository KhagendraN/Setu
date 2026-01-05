"""
PDF Regenerator Module
Handles regenerating PDFs with approved bias-free sentences using PyMuPDF
"""

import logging
import fitz  # PyMuPDF
import re
from typing import List, Tuple, Optional, Dict
from api.schemas import BiasReviewItem

logger = logging.getLogger(__name__)


class PDFRegenerator:
    """
    Regenerates PDFs by replacing biased sentences with approved alternatives.
    Uses PyMuPDF to modify the original PDF while preserving formatting.
    """

    def __init__(self):
        """Initialize PDF regenerator."""
        # Try to register Nepali font support
        self.nepali_font = self._get_nepali_font()

    def _get_nepali_font(self) -> str:
        """
        Get the best available font for Nepali text.
        Returns font name to use for text insertion.
        """
        # Try to use a font that supports Devanagari script
        # Common fonts that support Nepali/Devanagari:
        # - NotoSansDevanagari
        # - Mangal
        # - Nirmala UI (Windows)
        # - Lohit Devanagari (Linux)

        # PyMuPDF built-in fonts that might work
        fonts_to_try = [
            "times-roman",  # Has better Unicode support than helv
            "helv",
            "cour"
        ]

        # For now, use times-roman as it has better Unicode support
        # In production, you should embed a proper Devanagari font
        return "times-roman"

    def regenerate_pdf(
        self,
        original_pdf_bytes: bytes,
        sentences: List[BiasReviewItem],
        output_filename: str = "debiased_document.pdf"
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Regenerate PDF with approved sentences replacing biased ones.

        Args:
            original_pdf_bytes: Original PDF content as bytes
            sentences: List of BiasReviewItem with approved suggestions
            output_filename: Name for the output PDF file

        Returns:
            Tuple of (success, pdf_bytes, error_message)
        """
        try:
            logger.info(f"Starting PDF regeneration for {output_filename}")

            # Open the original PDF from bytes
            doc = fitz.open(stream=original_pdf_bytes, filetype="pdf")

            # Count replacements
            replacements_made = 0

            # Process each sentence that has an approved suggestion
            for item in sentences:
                if item.is_biased and item.approved_suggestion and item.status == "approved":
                    # Replace the biased sentence with approved suggestion
                    replacements_made += self._replace_text_in_pdf(
                        doc,
                        item.original_sentence,
                        item.approved_suggestion
                    )

            logger.info(f"Made {replacements_made} text replacements in PDF")

            # Convert the modified document to bytes
            output_bytes = doc.tobytes()
            doc.close()

            return (True, output_bytes, None)

        except Exception as e:
            error_msg = f"PDF regeneration failed: {str(e)}"
            logger.error(error_msg)
            return (False, None, error_msg)

    def _replace_text_in_pdf(
        self,
        doc: fitz.Document,
        old_text: str,
        new_text: str
    ) -> int:
        """
        Replace text in PDF document using PyMuPDF's redaction feature.

        Args:
            doc: PyMuPDF Document object
            old_text: Text to find and replace
            new_text: Replacement text

        Returns:
            Number of replacements made
        """
        replacements = 0

        try:
            # Search for the text across all pages
            for page_num in range(len(doc)):
                page = doc[page_num]

                # Search for the old text
                text_instances = page.search_for(old_text)

                if text_instances:
                    logger.debug(f"Found {len(text_instances)} instances on page {page_num + 1}")

                    for inst in text_instances:
                        # Get the rectangle coordinates
                        rect = inst

                        # Add redaction annotation to remove old text
                        page.add_redact_annot(rect, fill=(1, 1, 1))  # White fill

                        # Apply redactions
                        page.apply_redactions()

                        # Insert new text at the same location
                        # Get font size from the area (approximate)
                        fontsize = rect.height * 0.8  # Approximate font size

                        # Insert the new text
                        page.insert_textbox(
                            rect,
                            new_text,
                            fontsize=fontsize,
                            fontname="helv",  # Use Helvetica as default
                            align=fitz.TEXT_ALIGN_LEFT
                        )

                        replacements += 1
                        logger.debug(f"Replaced text on page {page_num + 1}")

        except Exception as e:
            logger.warning(f"Error during text replacement: {e}")

        return replacements

    def create_simple_pdf_from_sentences(
        self,
        sentences: List[BiasReviewItem],
        filename: str = "debiased_document.pdf"
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Create a simple new PDF from sentences (fallback method).
        Uses approved suggestions for biased sentences, original text for neutral ones.

        Args:
            sentences: List of BiasReviewItem objects
            filename: Output filename

        Returns:
            Tuple of (success, pdf_bytes, error_message)
        """
        try:
            logger.info("Creating new PDF from sentences")

            # Create a new PDF
            doc = fitz.open()
            page = doc.new_page(width=595, height=842)  # A4 size

            # Starting position
            y_position = 50
            x_margin = 50
            page_width = 595 - 2 * x_margin
            font_size = 12
            line_height = 20

            # Write each sentence
            for item in sentences:
                # Use approved suggestion if available, otherwise original
                text = item.approved_suggestion if (item.is_biased and item.approved_suggestion) else item.original_sentence

                # Check if we need a new page
                if y_position > 750:  # Near bottom of page
                    page = doc.new_page(width=595, height=842)
                    y_position = 50

                # Insert text
                rect = fitz.Rect(x_margin, y_position, x_margin + page_width, y_position + line_height * 3)
                page.insert_textbox(
                    rect,
                    text,
                    fontsize=font_size,
                    fontname="helv",
                    align=fitz.TEXT_ALIGN_LEFT
                )

                y_position += line_height * 2

            # Convert to bytes
            output_bytes = doc.tobytes()
            doc.close()

            logger.info("Successfully created new PDF")
            return (True, output_bytes, None)

        except Exception as e:
            error_msg = f"Failed to create PDF from sentences: {str(e)}"
            logger.error(error_msg)
            return (False, None, error_msg)
