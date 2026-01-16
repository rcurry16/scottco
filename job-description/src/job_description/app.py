"""
FastAPI Web Application for Job Description Generator

Provides a web interface for generating job descriptions using both
Mistral and Anthropic models in parallel, with side-by-side comparison.

Usage:
    export MISTRAL_API_KEY=your_mistral_key
    export ANTHROPIC_API_KEY=your_anthropic_key
    uvicorn app:app --reload
"""

import os
import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

from . import config
from .logging_config import log_with_extra

# Initialize logger
logger = logging.getLogger("job_description.api")
from .models import (
    UserResponses,
    OrganizationalContext,
    JobDescription,
    ClassificationJobInformation,
    BoilerplateElements,
    ExclusionStatus
)
from .job_desc_generator_v2_mistral import generate_job_description as generate_mistral
from .job_desc_generator_v2_anthropic import generate_job_description as generate_anthropic
from . import output_formatter


# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Job Description Generator",
    version="1.0.0",
    root_path="/job-description"
)


# Logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with structured JSON logging."""

    async def dispatch(self, request: Request, call_next):
        """Log request start, process request, and log completion."""
        request_id = str(uuid.uuid4())
        client_ip = request.client.host if request.client else "unknown"
        start_time = time.time()

        # Attach request_id to request state for use in endpoints
        request.state.request_id = request_id

        # Log request start
        log_with_extra(
            logger,
            logging.INFO,
            "Request started",
            request_id=request_id,
            ip=client_ip,
            method=request.method,
            path=request.url.path,
            event="request_start"
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            total_duration = time.time() - start_time
            log_with_extra(
                logger,
                logging.ERROR,
                f"Request failed: {str(e)}",
                request_id=request_id,
                ip=client_ip,
                method=request.method,
                path=request.url.path,
                total_duration_seconds=round(total_duration, 3),
                error_type=type(e).__name__,
                error_message=str(e),
                event="error"
            )
            raise

        # Calculate total duration
        total_duration = time.time() - start_time

        # Log request completion
        log_with_extra(
            logger,
            logging.INFO,
            "Request completed",
            request_id=request_id,
            ip=client_ip,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            total_duration_seconds=round(total_duration, 3),
            event="request_complete"
        )

        return response


app.add_middleware(LoggingMiddleware)

# Mount static files directory (at project root, not in package)
static_dir = Path(__file__).parent.parent.parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============================================================================
# PYDANTIC MODELS FOR API
# ============================================================================

class ConfigUpdate(BaseModel):
    """Model for updating organizational config"""
    organization_name: str
    industry: str
    location: str
    organization_description: Optional[str] = ""


class GenerationRequest(BaseModel):
    """Model for job description generation request"""
    # Basic Information
    job_title: str
    department: str
    division_section: Optional[str] = ""
    reports_to: str

    # Role Responsibilities
    primary_responsibilities: str
    key_deliverables: str
    unique_aspects: str

    # People & Relationships
    manages_people: bool
    num_direct_reports: Optional[str] = ""
    num_indirect_reports: Optional[str] = ""
    other_resources_managed: Optional[str] = ""
    key_contacts: str

    # Scope & Decision-Making
    decision_authority: str
    innovation_problem_solving: str
    impact_of_results: str

    # Requirements
    special_requirements: Optional[str] = ""


class GenerationResponse(BaseModel):
    """Model for generation response"""
    mistral_output: str
    anthropic_output: str
    job_id: str  # Timestamp-based ID for downloads


# ============================================================================
# IN-MEMORY CONFIG STORAGE
# ============================================================================

current_config = {
    "organization_name": config.ORGANIZATION_NAME,
    "industry": config.INDUSTRY,
    "location": config.LOCATION,
    "organization_description": config.ORGANIZATION_DESCRIPTION
}


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    index_path = static_dir / "index.html"
    if not index_path.exists():
        return HTMLResponse("""
            <html>
                <head><title>Setup Required</title></head>
                <body>
                    <h1>Setup Required</h1>
                    <p>Please create static/index.html</p>
                </body>
            </html>
        """)
    return FileResponse(index_path)


@app.get("/api/config")
async def get_config():
    """Get current organizational configuration"""
    return current_config


@app.post("/api/config")
async def update_config(config_update: ConfigUpdate):
    """Update organizational configuration"""
    current_config["organization_name"] = config_update.organization_name
    current_config["industry"] = config_update.industry
    current_config["location"] = config_update.location
    current_config["organization_description"] = config_update.organization_description or ""
    return {"status": "success", "config": current_config}


@app.post("/api/generate", response_model=GenerationResponse)
async def generate_job_descriptions(request: GenerationRequest):
    """
    Generate job descriptions using both Mistral and Anthropic models in parallel
    """
    # Convert request to UserResponses model
    user_responses = UserResponses(
        job_title=request.job_title,
        department=request.department,
        division_section=request.division_section or "",
        reports_to=request.reports_to,
        primary_responsibilities=request.primary_responsibilities,
        key_deliverables=request.key_deliverables,
        unique_aspects=request.unique_aspects,
        manages_people=request.manages_people,
        num_direct_reports=request.num_direct_reports or "",
        num_indirect_reports=request.num_indirect_reports or "",
        other_resources_managed=request.other_resources_managed or "",
        key_contacts=request.key_contacts,
        decision_authority=request.decision_authority,
        innovation_problem_solving=request.innovation_problem_solving,
        impact_of_results=request.impact_of_results,
        special_requirements=request.special_requirements or ""
    )

    # Create organizational context from current config
    org_context = OrganizationalContext(
        organization_name=current_config["organization_name"],
        industry=current_config["industry"],
        location=current_config["location"],
        department_default="",
        organization_description=current_config["organization_description"]
    )

    # Generate job ID for this session
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Run both generators in parallel
    try:
        mistral_task = generate_mistral(user_responses, org_context)
        anthropic_task = generate_anthropic(user_responses, org_context)

        mistral_result, anthropic_result = await asyncio.gather(
            mistral_task,
            anthropic_task,
            return_exceptions=True
        )

        # Check for errors
        mistral_output = ""
        anthropic_output = ""

        if isinstance(mistral_result, Exception):
            mistral_output = f"ERROR generating with Mistral:\n\n{str(mistral_result)}"
        else:
            mistral_output = output_formatter.format_console_output(mistral_result)

        if isinstance(anthropic_result, Exception):
            anthropic_output = f"ERROR generating with Anthropic:\n\n{str(anthropic_result)}"
        else:
            anthropic_output = output_formatter.format_console_output(anthropic_result)

        # Store results for download (in memory, indexed by job_id)
        if not isinstance(mistral_result, Exception):
            _save_result(job_id, "mistral", mistral_result)
        if not isinstance(anthropic_result, Exception):
            _save_result(job_id, "anthropic", anthropic_result)

        return GenerationResponse(
            mistral_output=mistral_output,
            anthropic_output=anthropic_output,
            job_id=job_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/api/download/{provider}/{job_id}/{format}")
async def download_job_description(request: Request, provider: str, job_id: str, format: str):
    """
    Download job description in specified format

    Args:
        provider: "mistral" or "anthropic"
        job_id: The job session ID
        format: "txt", "pdf", or "docx"
    """
    request_id = getattr(request.state, "request_id", None)

    # Validate format
    if format not in ["txt", "pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Invalid format. Must be txt, pdf, or docx")

    # Look for file in output directory
    output_dir = Path(config.OUTPUT_DIRECTORY)
    pattern = f"job_description_*_{job_id}_{provider}.{format}"

    matching_files = list(output_dir.glob(pattern))

    if not matching_files:
        raise HTTPException(status_code=404, detail=f"Job description file not found for format: {format}")

    filepath = matching_files[0]

    # Log file download
    if request_id:
        log_with_extra(
            logger,
            logging.INFO,
            "File downloaded",
            request_id=request_id,
            operation="download",
            filename=filepath.name,
            file_size_bytes=filepath.stat().st_size,
            provider=provider,
            format=format,
            event="file_download"
        )

    # Set appropriate media type
    media_types = {
        "txt": "text/plain",
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    return FileResponse(
        filepath,
        media_type=media_types[format],
        filename=filepath.name
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _save_result(job_id: str, provider: str, job_desc: JobDescription):
    """Save job description in multiple formats (TXT, PDF, DOCX)"""
    from .export_utils import generate_pdf, generate_docx

    output_dir = Path(config.OUTPUT_DIRECTORY)
    output_dir.mkdir(exist_ok=True)

    job_title_sanitized = output_formatter.sanitize_filename(job_desc.job_info.job_working_title)
    base_filename = f"job_description_{job_title_sanitized}_{job_id}_{provider}"

    # Get formatted content
    formatted_output = output_formatter.format_console_output(job_desc)

    # Save TXT
    txt_path = output_dir / f"{base_filename}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(formatted_output)

    # Save PDF
    pdf_path = output_dir / f"{base_filename}.pdf"
    generate_pdf(formatted_output, pdf_path)

    # Save DOCX
    docx_path = output_dir / f"{base_filename}.docx"
    generate_docx(formatted_output, docx_path)


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Startup message"""
    print(f"\n🚀 Job Description Generator running")
    print(f"📝 Open http://localhost:8000 in your browser\n")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
