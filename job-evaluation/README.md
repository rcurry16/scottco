# Job Classification Tool

AI-powered tool for analyzing and comparing position descriptions using Claude API. Automates manual review tasks for classification consultants.

**Status:**
- Tool 1.1 (Position Description Side by Side) - Complete ✅
- Tool 1.2 (Revaluation Gauge) - Complete ✅
- Tool 1.3 (First Pass Classifier) - Complete ✅

---

## Quick Start

### Web Interface (Recommended)

```bash
# 1. Install dependencies
uv pip install -e .

# 2. Create .env file with your Anthropic API key
ANTHROPIC_API_KEY=your_key_here

# 3. Extract classification standards (one-time)
uv run python src/job_eval/extract_standards.py

# 4. Start the web server
job-eval serve

# 5. Open browser to http://localhost:8000
```

### CLI Usage

```bash
# Full pipeline - compare + gauge + classify
job-eval compare "Position Levels/EC 02 Project Assistant - 90001351.pdf" \
                 "Position Levels/EC 05 Executive Assistant - 90005280.pdf" \
                 --with-classify

# Single document classification
job-eval classify "Position Levels/EC 10 Policy Analyst.pdf"
```

Get your API key: https://console.anthropic.com/

---

## Installation

Dependencies already installed via uv. If starting fresh:

```bash
source .venv/bin/activate
uv pip install -e .
```

---

## Usage

### Compare PDFs (Tool 1.1)

```bash
job-eval compare <old_pdf> <new_pdf>
```

Output includes:
- Summary of changes
- Overall significance (minor/moderate/major)
- Changes by document section (additions/deletions/modifications)
- Classification impact across six categories:
  - Accountabilities
  - Knowledge & Experience
  - Decision Making
  - Customer & Relationship Management
  - Leadership
  - Project Management

### Revaluation Gauge (Tool 1.2)

Assess if changes warrant formal re-evaluation with full position context:

```bash
# Run on comparison results
job-eval compare old.pdf new.pdf --output results.json
job-eval gauge results.json

# Or run both at once
job-eval compare old.pdf new.pdf --with-gauge
# Shorthand: -g flag
job-eval compare old.pdf new.pdf -g
```

Output includes:
- Current classification level (auto-detected from filename)
- Expected new level range (e.g., "EC-10 to EC-11")
- Yes/No recommendation with confidence %
- Detailed rationale comparing changes to current level expectations
- Risk assessment (low/medium/high)
- Classification categories affected
- Key factors influencing decision

**How it works:**
- Loads full position description (not just changes)
- Extracts current level from filename
- Compares changes against what's expected at that level
- Provides contextual recommendation (e.g., "these changes elevate beyond EC-10 baseline")

### First Pass Classifier (Tool 1.3)

Propose classification level for a position description:

```bash
# Standalone classification
job-eval classify position.pdf

# With context from previous tools (recommended)
job-eval classify position.pdf --from-results gauge_results.json

# Full integrated pipeline (1.1 → 1.2 → 1.3)
job-eval compare old.pdf new.pdf --with-classify
# Shorthand: -c flag (implies -g)
job-eval compare old.pdf new.pdf -c
```

Output includes:
- Recommended classification level (EC-01 to EC-17)
- Confidence score (0-100%)
- Previous level (if available from context)
- Detailed rationale with evidence from position description
- Category analysis (all 6 classification categories)
- Supporting evidence for recommendation
- Alternative levels to consider
- Comparable positions at this level

**How it works:**
- Analyzes position against all 17 classification levels
- Can work standalone or with context from Tools 1.1/1.2
- When context provided: considers documented changes + current level baseline
- Provides category-by-category analysis
- Recommends best-fit level with justification

### Save Results

```bash
# JSON export
job-eval compare old.pdf new.pdf --output results.json

# JSON only (for scripting)
job-eval compare old.pdf new.pdf --json
job-eval gauge results.json --json
job-eval classify position.pdf --json
```

### Other Commands

```bash
# PDF information
job-eval info "Position Levels/EC 08 Governance Consultant - 90004214.pdf"

# Extract text
job-eval extract-text "Position Levels/EC 05 Executive Assistant - 90005280.pdf"

# Version
job-eval version

# Help
job-eval --help
```

---

## Testing

### Basic Validation

```bash
# Test PDF extraction
job-eval info "Position Levels/EC 05 Executive Assistant - 90005280.pdf"

# Test comparison (different levels)
job-eval compare \
  "Position Levels/EC 02 Project Assistant - 90001351.pdf" \
  "Position Levels/EC 05 Executive Assistant - 90005280.pdf"

# Validate JSON output
job-eval compare old.pdf new.pdf --json | python -m json.tool
```

### Blind Classification Testing

Tool 1.3 was validated with blind tests (titles/levels removed from 4 positions):

**Results:**
- 0/4 exact matches (expected baseline ~25%)
- 3/4 within ±1 level (75% near-accuracy)
- Confidence scores: 78-82% (appropriate uncertainty)

**Observed Patterns:**
- Tends to classify 1-2 levels higher at mid-ranges (EC-03 to EC-10)
- Correctly distinguishes divisional vs departmental scope at senior levels
- Requires calibration on coordinator vs manager boundaries (EC-09/10 vs EC-11)

**Use Case:**
- Best for preliminary analysis requiring consultant validation
- Useful for identifying positions needing detailed review
- Category-by-category analysis helps understand classification reasoning

### Expected Behavior

- PDF metadata displays correctly
- Text extraction produces readable output
- Comparisons identify additions, deletions, modifications
- Changes map to classification categories
- Significance assessment makes sense
- JSON output is valid
- Classification recommendations are within ±1-2 levels of actual

---

## Configuration

Set environment variables in `.env`:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

---

## Troubleshooting

**Error: "ANTHROPIC_API_KEY must be set"**
- Run `job-eval init` and edit `.env` file

**Error: "PDF not found"**
- Check file path is correct
- Use quotes around paths with spaces

**Poor comparison quality**
- Verify PDFs have extractable text (not scanned images)
- Ensure documents are position descriptions

---

## Architecture

```
User Input (PDFs)
    ↓
PDF Processor (pdfplumber) → Raw text extraction
    ↓
Comparator (Claude API) → Semantic analysis
    ↓
Structured Output (Pydantic) → Validation
    ↓
CLI Display (Rich) → Formatted report / JSON
```

### Key Design Decisions

- **LLM-based parsing** - Handles varying document formats flexibly
- **Semantic comparison** - Identifies comparable sections regardless of naming
- **Classification mapping** - Links changes to standard evaluation categories
- **Modular design** - Core logic separated from CLI for future FastAPI deployment

### Project Structure

```
job-eval/
├── src/job_eval/
│   ├── cli.py                 # CLI interface (Typer + Rich)
│   ├── comparator.py          # Document comparison logic (Tool 1.1)
│   ├── gauge.py               # Revaluation assessment (Tool 1.2)
│   ├── classifier.py          # Position classification (Tool 1.3)
│   ├── pdf_processor.py       # PDF text extraction
│   └── extract_standards.py   # Classification standards extraction
├── data/
│   └── classification_standards.json  # Generated from Grade Matrix
├── Position Levels/           # 41 sample PDFs (EC 02-16)
├── Rationale Docs/            # Classification references
├── pyproject.toml             # Dependencies (uv)
└── .env                       # API keys (create this)
```

---

## Tech Stack

**Backend:**
- Python 3.12+
- FastAPI (web framework)
- uvicorn (ASGI server)
- pdfplumber (PDF extraction)
- python-docx (DOCX extraction)
- Claude Haiku 4.5 (Anthropic API)
- Pydantic (validation)

**CLI:**
- Typer + Rich (CLI interface)

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Modern responsive design
- No build step required

**Package Management:**
- uv (fast Python package manager)

---

## Roadmap

### ✅ Tool 1.1: Position Description Side by Side (Complete)
Compare position descriptions and identify changes

### ✅ Tool 1.2: Revaluation Gauge (Complete)
Determine if changes warrant re-evaluation with confidence scoring

### ✅ Tool 1.3: First Pass Classifier (Complete)
Propose new classification level with justification
- Standalone or context-aware modes
- Analysis across all 6 classification categories
- Confidence scoring with supporting evidence

### ✅ Web Interface (Complete)
- FastAPI backend with file upload
- Modern HTML/CSS/JS frontend
- Support for PDF and DOCX files
- Full workflow and quick classification modes
- Copy-to-clipboard formatted reports

---

## Deployment

### VPS Deployment

```bash
# 1. On your VPS, clone the repo
git clone <repo-url>
cd job-eval

# 2. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv pip install -e .

# 4. Create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 5. Extract classification standards (one-time)
uv run python src/job_eval/extract_standards.py

# 6. Run server (production)
job-eval serve --host 0.0.0.0 --port 8000

# 7. Optional: Run with systemd for auto-restart
# Create /etc/systemd/system/job-eval.service
```

Example systemd service file:

```ini
[Unit]
Description=Job Evaluation Tool
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/job-eval
Environment="PATH=/home/youruser/.local/bin:/usr/bin"
ExecStart=/home/youruser/.local/bin/job-eval serve --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl enable job-eval
sudo systemctl start job-eval
```

### Nginx Reverse Proxy (Optional)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase upload size for large PDFs
        client_max_body_size 50M;
    }
}
```

---

## Development

### Adding New Features

Core modules are in `src/job_eval/`:
- `pdf_processor.py` - PDF text extraction
- `docx_processor.py` - DOCX text extraction
- `document_processor.py` - Unified document handler
- `comparator.py` - Comparison logic (Tool 1.1)
- `gauge.py` - Revaluation assessment (Tool 1.2)
- `classifier.py` - Position classification (Tool 1.3)
- `api.py` - FastAPI backend
- `server.py` - Server runner
- `cli.py` - CLI commands
- `static/` - Frontend files (HTML/CSS/JS)

### Testing Locally

```bash
# Run web interface in development mode (with auto-reload)
job-eval serve --reload

# Run CLI commands
job-eval compare old.pdf new.pdf
job-eval classify position.pdf
```

---

## Data Sources

**Position Levels/** - 41 example position descriptions (EC 02-16)

**Rationale Docs/** - Classification references:
- PSC EC Grade Matrix (classification levels 1-17)
- 5 position examples with rationale documents

These inform the classification standards used by all three tools.

---

For non-technical overview, see [OVERVIEW.md](OVERVIEW.md)
