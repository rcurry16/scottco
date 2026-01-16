"""Test fixtures for job-evaluation tests."""
import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    from job_eval.api import app
    return TestClient(app)


@pytest.fixture
def sample_pdf_file():
    """Create a mock PDF file for testing."""
    content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n"
    return ("test.pdf", io.BytesIO(content), "application/pdf")


@pytest.fixture
def sample_docx_file():
    """Create a mock DOCX file for testing."""
    # Minimal DOCX structure
    content = b"PK\x03\x04" + b"\x00" * 100  # ZIP file header
    return ("test.docx", io.BytesIO(content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@pytest.fixture
def sample_invalid_file():
    """Create an invalid file for testing."""
    content = b"This is not a valid file"
    return ("test.txt", io.BytesIO(content), "text/plain")


@pytest.fixture
def mock_classifier():
    """Mock FirstPassClassifier."""
    with patch("job_eval.api.FirstPassClassifier") as mock:
        instance = MagicMock()
        instance.classify.return_value = MagicMock(
            position_title="Senior Developer",
            model_dump=lambda: {
                "position_title": "Senior Developer",
                "classification_level": "Level 5",
                "reasoning": "Test reasoning"
            }
        )
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_comparator():
    """Mock PositionComparator."""
    with patch("job_eval.api.PositionComparator") as mock:
        instance = MagicMock()
        instance.compare.return_value = MagicMock(
            model_dump=lambda: {
                "changes": ["Responsibility scope increased"],
                "significance": "moderate"
            }
        )
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_gauge():
    """Mock RevaluationGauge."""
    with patch("job_eval.api.RevaluationGauge") as mock:
        instance = MagicMock()
        instance.assess.return_value = MagicMock(
            model_dump=lambda: {
                "recommendation": "revaluation_needed",
                "reasoning": "Significant changes detected"
            }
        )
        mock.return_value = instance
        yield mock
