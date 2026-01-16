"""Test fixtures for job-description tests."""
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set dummy API keys for testing before importing app
os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
os.environ["MISTRAL_API_KEY"] = "test-mistral-key"


@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    from job_description.app import app
    return TestClient(app)


@pytest.fixture
def sample_generation_request():
    """Sample job description generation request."""
    return {
        "job_title": "Software Developer",
        "department": "IT",
        "division_section": "Engineering",
        "reports_to": "Senior Manager",
        "primary_responsibilities": "Develop and maintain software applications",
        "key_deliverables": "Working software, documentation",
        "unique_aspects": "Full-stack development",
        "manages_people": False,
        "num_direct_reports": "",
        "num_indirect_reports": "",
        "other_resources_managed": "",
        "key_contacts": "Team members, stakeholders",
        "decision_authority": "Technical decisions within scope",
        "innovation_problem_solving": "Moderate problem-solving",
        "impact_of_results": "Team-level impact",
        "special_requirements": ""
    }


@pytest.fixture
def sample_config_update():
    """Sample config update request."""
    return {
        "organization_name": "Test Organization",
        "industry": "Technology",
        "location": "Halifax, NS",
        "organization_description": "A test organization"
    }


# Removed mock_job_description fixture - not needed for smoke tests
