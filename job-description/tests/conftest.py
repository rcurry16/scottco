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
    from app import app
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


@pytest.fixture
def mock_job_description():
    """Mock JobDescription result."""
    from models import (
        JobDescription,
        ClassificationJobInformation,
        JobInformation,
        PeopleManagement,
        ScopeSection,
        WorkingConditions,
        BoilerplateElements,
        ExclusionStatus
    )

    return JobDescription(
        classification_info=ClassificationJobInformation(
            sap_job_id="TEST001",
            position_title="Test Position",
            pay_grade="Test Grade",
            add_on_eligible="No",
            standardized="Yes",
            inactive="No",
            date_last_evaluated="2026-01-15"
        ),
        job_info=JobInformation(
            job_working_title="Test Title",
            department="Test Department",
            division_section="Test Division",
            reports_to="Test Manager",
            exclusion_status=ExclusionStatus.NOT_EXCLUDED
        ),
        overall_purpose="Test purpose",
        key_responsibilities=["Responsibility 1", "Responsibility 2"],
        people_management=PeopleManagement(
            type_of_role="Individual Contributor",
            num_direct_reports="0",
            num_indirect_reports="0",
            other_resources_managed=""
        ),
        scope=ScopeSection(
            contacts="Test contacts",
            innovation="Test innovation",
            decision_making="Test decisions",
            impact_of_results="Test impact",
            other=""
        ),
        licenses_certifications=[],
        working_conditions=WorkingConditions(
            physical_effort="Light",
            physical_environment="Office",
            sensory_attention="Moderate",
            psychological_pressures="Low"
        ),
        boilerplate=BoilerplateElements()
    )
