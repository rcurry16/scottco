"""Unified document processing for PDF and DOCX files."""
from pathlib import Path

from job_eval.docx_processor import DOCXProcessor
from job_eval.pdf_processor import PDFProcessor


class DocumentProcessor:
    """Extract text from position description documents (PDF or DOCX)."""

    def __init__(self, doc_path: str | Path):
        """Initialize processor with document path."""
        self.doc_path = Path(doc_path)
        if not self.doc_path.exists():
            raise FileNotFoundError(f"Document not found: {self.doc_path}")

        # Determine file type and create appropriate processor
        suffix = self.doc_path.suffix.lower()
        if suffix == ".pdf":
            self.processor = PDFProcessor(self.doc_path)
        elif suffix in [".docx", ".doc"]:
            self.processor = DOCXProcessor(self.doc_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}. Only PDF and DOCX supported.")

    def extract_text(self) -> str:
        """
        Extract all text from document.

        Returns:
            Full text content
        """
        return self.processor.extract_text()

    def extract_metadata(self) -> dict:
        """
        Extract document metadata.

        Returns:
            Dictionary with title, author, etc.
        """
        return self.processor.extract_metadata()
