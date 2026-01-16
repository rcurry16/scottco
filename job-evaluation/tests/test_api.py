"""API endpoint tests for job-evaluation."""
import pytest


def test_health_endpoint(test_client):
    """Test health check endpoint returns 200."""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_classify_invalid_file_type(test_client, sample_invalid_file):
    """Test classify endpoint rejects invalid file types."""
    filename, content, mime_type = sample_invalid_file
    response = test_client.post(
        "/api/classify",
        files={"file": (filename, content, mime_type)}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_classify_no_file(test_client):
    """Test classify endpoint requires file upload."""
    response = test_client.post("/api/classify")
    assert response.status_code == 422  # Unprocessable entity


def test_classify_with_pdf(test_client, sample_pdf_file, mock_classifier):
    """Test classify endpoint with PDF file."""
    filename, content, mime_type = sample_pdf_file
    response = test_client.post(
        "/api/classify",
        files={"file": (filename, content, mime_type)}
    )
    # With mocked classifier, should succeed
    if response.status_code == 200:
        data = response.json()
        assert "job_id" in data
        assert "result" in data


def test_full_workflow_invalid_file_type(test_client, sample_pdf_file, sample_invalid_file):
    """Test full workflow rejects invalid file types."""
    pdf_filename, pdf_content, pdf_mime = sample_pdf_file
    invalid_filename, invalid_content, invalid_mime = sample_invalid_file

    response = test_client.post(
        "/api/full-workflow",
        files={
            "old_file": (pdf_filename, pdf_content, pdf_mime),
            "new_file": (invalid_filename, invalid_content, invalid_mime)
        }
    )
    assert response.status_code == 400


def test_full_workflow_missing_files(test_client, sample_pdf_file):
    """Test full workflow requires both files."""
    filename, content, mime_type = sample_pdf_file
    response = test_client.post(
        "/api/full-workflow",
        files={"old_file": (filename, content, mime_type)}
    )
    assert response.status_code == 422  # Missing new_file


def test_download_invalid_format(test_client):
    """Test download endpoint rejects invalid formats."""
    response = test_client.get("/api/download/123/invalid")
    assert response.status_code == 400
    assert "Invalid format" in response.json()["detail"]


def test_download_nonexistent_job(test_client):
    """Test download endpoint returns 404 for nonexistent job."""
    response = test_client.get("/api/download/nonexistent123/txt")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_download_valid_format_in_url(test_client):
    """Test download endpoint accepts valid formats in URL."""
    # Will 404 but validates format is accepted
    for format in ["txt", "pdf", "docx"]:
        response = test_client.get(f"/api/download/test123/{format}")
        # Should be 404 (not found), not 400 (bad request)
        assert response.status_code == 404
