"""FastAPI backend for job evaluation tool."""
import json
import logging
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from .classifier import ClassificationRecommendation, FirstPassClassifier
from .comparator import ComparisonResult, PositionComparator
from .export_utils import generate_docx, generate_pdf
from .gauge import RevaluationGauge, RevaluationRecommendation
from .logging_config import log_with_extra
from .output_formatter import format_classification_only, format_full_workflow

# Initialize logger
logger = logging.getLogger("job_eval.api")

app = FastAPI(
    title="Job Evaluation Tool",
    version="0.1.0",
    root_path="/job-evaluation"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        response = await call_next(request)

        # Calculate total duration
        total_duration = time.time() - start_time

        # Log request completion (successful or error response)
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

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Output directory for generated files
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """Serve frontend."""
    return FileResponse(static_path / "index.html")


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


def save_upload_file(upload_file: UploadFile, request_id: str = None) -> Path:
    """Save uploaded file to temporary location."""
    suffix = Path(upload_file.filename).suffix if upload_file.filename else ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = upload_file.file.read()
        tmp.write(content)
        filepath = Path(tmp.name)

        # Log file upload
        if request_id:
            log_with_extra(
                logger,
                logging.INFO,
                "File uploaded",
                request_id=request_id,
                operation="upload",
                filename=upload_file.filename or "unknown",
                file_size_bytes=len(content),
                file_type=suffix,
                event="file_upload"
            )

        return filepath


def validate_file_type(filename: str | None) -> None:
    """Validate uploaded file is PDF or DOCX."""
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = Path(filename).suffix.lower()
    if suffix not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Only PDF and DOCX allowed."
        )


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace problematic characters
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in filename)
    # Replace multiple spaces/underscores with single underscore
    safe = "_".join(safe.split())
    return safe[:100]  # Limit length


def save_results(
    job_id: str, workflow_type: str, result_data: dict[str, Any], position_title: str = "evaluation"
) -> None:
    """Save evaluation results in multiple formats (TXT, PDF, DOCX)"""
    # Sanitize position title for filename
    safe_title = sanitize_filename(position_title)
    base_filename = f"job_eval_{safe_title}_{job_id}"

    # Format to plain text
    if workflow_type == "full":
        formatted_text = format_full_workflow(result_data)
    else:
        formatted_text = format_classification_only(result_data)

    # Save TXT
    txt_path = output_dir / f"{base_filename}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(formatted_text)

    # Save PDF
    pdf_path = output_dir / f"{base_filename}.pdf"
    generate_pdf(formatted_text, pdf_path)

    # Save DOCX
    docx_path = output_dir / f"{base_filename}.docx"
    generate_docx(formatted_text, docx_path)


@app.post("/api/classify", response_model=dict[str, Any])
async def classify_position(request: Request, file: UploadFile = File(...)):
    """
    Classify a single position description.

    Returns Tool 1.3 output only.
    """
    request_id = getattr(request.state, "request_id", None)
    temp_file = None
    try:
        # Validate file type
        validate_file_type(file.filename)

        # Save uploaded file
        temp_file = save_upload_file(file, request_id)

        # Run classifier
        classifier = FirstPassClassifier()
        result = classifier.classify(temp_file)

        # Generate job ID and save results
        job_id = str(int(time.time() * 1000))
        result_dict = result.model_dump()
        position_title = result_dict.get("position_title", "evaluation")

        save_results(job_id, "classification", result_dict, position_title)

        # Return result with job_id
        return {
            "job_id": job_id,
            "result": result_dict,
        }

    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors) as-is
        raise
    except Exception as e:
        # Convert other exceptions to 500 errors
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        if temp_file and temp_file.exists():
            temp_file.unlink()


@app.post("/api/full-workflow", response_model=dict[str, Any])
async def full_workflow(
    request: Request,
    old_file: UploadFile = File(...),
    new_file: UploadFile = File(...)
):
    """
    Run full workflow: compare -> gauge -> classify.

    Returns combined output from all three tools.
    """
    request_id = getattr(request.state, "request_id", None)
    temp_old = None
    temp_new = None
    temp_comparison_json = None

    try:
        # Validate file types
        validate_file_type(old_file.filename)
        validate_file_type(new_file.filename)

        # Save uploaded files
        temp_old = save_upload_file(old_file, request_id)
        temp_new = save_upload_file(new_file, request_id)

        # Tool 1.1: Compare
        comparator = PositionComparator()
        comparison_result = comparator.compare(temp_old, temp_new)

        # Save comparison result to temp JSON for gauge
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(comparison_result.model_dump(), f)
            temp_comparison_json = Path(f.name)

        # Tool 1.2: Gauge
        assessor = RevaluationGauge()
        gauge_result = assessor.assess(temp_comparison_json)

        # Tool 1.3: Classify
        classifier = FirstPassClassifier()
        classification_result = classifier.classify(
            temp_new,
            comparison_data=comparison_result.model_dump(),
            gauge_data=gauge_result.model_dump()
        )

        # Combine results
        result_data = {
            "comparison": comparison_result.model_dump(),
            "gauge": gauge_result.model_dump(),
            "classification": classification_result.model_dump()
        }

        # Generate job ID and save results
        job_id = str(int(time.time() * 1000))
        position_title = classification_result.position_title

        save_results(job_id, "full", result_data, position_title)

        # Return result with job_id
        return {
            "job_id": job_id,
            "result": result_data,
        }

    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors) as-is
        raise
    except Exception as e:
        # Convert other exceptions to 500 errors
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp files
        if temp_old and temp_old.exists():
            temp_old.unlink()
        if temp_new and temp_new.exists():
            temp_new.unlink()
        if temp_comparison_json and temp_comparison_json.exists():
            temp_comparison_json.unlink()


@app.get("/api/download/{job_id}/{format}")
async def download_evaluation(request: Request, job_id: str, format: str):
    """
    Download evaluation results in specified format

    Args:
        job_id: The job session ID
        format: "txt", "pdf", or "docx"
    """
    request_id = getattr(request.state, "request_id", None)

    # Validate format
    if format not in ["txt", "pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Invalid format. Must be txt, pdf, or docx")

    # Look for file in output directory
    pattern = f"job_eval_*_{job_id}.{format}"

    matching_files = list(output_dir.glob(pattern))

    if not matching_files:
        raise HTTPException(status_code=404, detail=f"Evaluation file not found for format: {format}")

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


# Removed global exception handler - FastAPI handles HTTPException properly by default
# Uncaught exceptions will still be logged by the middleware and return 500
