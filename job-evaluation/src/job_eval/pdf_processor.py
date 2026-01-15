"""PDF processing utilities for position descriptions."""
from pathlib import Path
from typing import Optional

import pdfplumber


class PDFProcessor:
    """Extract text from PDF position descriptions."""

    def __init__(self, pdf_path: str | Path):
        """Initialize processor with PDF path."""
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")

    def extract_text(self) -> str:
        """
        Extract all text from PDF.

        Returns:
            Full text content from all pages
        """
        pages_text = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(f"--- Page {i+1} ---\n{text}")

        return "\n\n".join(pages_text)

    def extract_metadata(self) -> dict[str, Optional[str]]:
        """
        Extract PDF metadata.

        Returns:
            Dictionary with title, author, subject, etc.
        """
        with pdfplumber.open(self.pdf_path) as pdf:
            metadata = pdf.metadata or {}

        return {
            "title": metadata.get("Title"),
            "author": metadata.get("Author"),
            "subject": metadata.get("Subject"),
            "creator": metadata.get("Creator"),
            "producer": metadata.get("Producer"),
            "creation_date": metadata.get("CreationDate"),
        }

    def get_page_count(self) -> int:
        """Get total number of pages in PDF."""
        with pdfplumber.open(self.pdf_path) as pdf:
            return len(pdf.pages)
