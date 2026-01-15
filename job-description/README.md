# AI Job Description Generator - Web App

A FastAPI web application that generates professional job descriptions using AI models (Mistral and Anthropic Claude). Generates side-by-side comparisons with detailed token usage and cost tracking.

## Features

- 🤖 **Dual AI Models**: Compare outputs from both Mistral Small and Claude 3.5 Haiku
- 💰 **Cost Tracking**: Real-time token usage and cost calculation (USD & CAD)
- 📋 **Professional Templates**: Follows Nova Scotia Government job description structure
- 🎯 **Role Level Detection**: Automatically infers Entry/Mid/Senior/Executive levels
- 🌐 **Web Interface**: Clean, responsive UI with form validation
- 📥 **Multiple Export Options**: Download as .txt files or copy to clipboard
- ⚙️ **Configurable**: Edit organizational context directly in the web UI

## Quick Start

### Prerequisites

- Python 3.9+

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd job-desc-tool
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
uvicorn app:app --reload
```

5. **Open in browser**
```
http://localhost:8000
```

## Usage

### Web Interface

1. **Configure Organization** (optional)
   - Set organization name, industry, location
   - Add detailed organizational description
   - Click "Save Configuration"

2. **Fill Job Information**
   - Complete 12 questions about the position
   - Required fields marked with *

3. **Generate**
   - Click "Generate Job Descriptions"
   - Wait 30-60 seconds for both models

4. **Review & Export**
   - Compare Mistral vs Anthropic outputs side-by-side
   - View token usage and costs at bottom of each output
   - Copy to clipboard or download .txt files

### Command Line

Run standalone generators:

```bash
# Mistral version
python job_desc_generator_v2_mistral.py

# Anthropic version
python job_desc_generator_v2_anthropic.py
```

## Configuration

### Organizational Context (`config.py`)

```python
ORGANIZATION_NAME = "Your Organization"
INDUSTRY = "Your Industry"
LOCATION = "Your Location"
ORGANIZATION_DESCRIPTION = "Detailed description..."
```

### Model Pricing (`config.py`)

```python
# Update if pricing changes
ANTHROPIC_HAIKU_INPUT_COST = 0.80   # per 1M tokens (USD)
ANTHROPIC_HAIKU_OUTPUT_COST = 4.00
MISTRAL_SMALL_INPUT_COST = 0.10
MISTRAL_SMALL_OUTPUT_COST = 0.80
USD_TO_CAD_RATE = 1.40  # Conversion rate
```

### Change AI Models

**Anthropic:** Edit `ANTHROPIC_MODEL` in `config.py`
```python
ANTHROPIC_MODEL = "claude-3-5-haiku-latest"  # or other Claude models
```

**Mistral:** Edit `MISTRAL_MODEL` in `config.py`
```python
MISTRAL_MODEL = "mistral:mistral-small-latest"  # or other Mistral models
```

## Project Structure

```
job-desc-tool/
├── app.py                              # FastAPI web application
├── config.py                           # Configuration settings
├── models.py                           # Pydantic data models
├── output_formatter.py                 # Output formatting utilities
├── job_desc_generator_v2_mistral.py    # Mistral AI generator
├── job_desc_generator_v2_anthropic.py  # Anthropic AI generator
├── static/
│   ├── index.html                      # Web UI
│   ├── styles.css                      # Styling
│   └── script.js                       # Frontend logic
├── output/                             # Generated job descriptions
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## Architecture

### 6-Agent System

Each generator uses 6 specialized AI agents:

1. **Job Info & Purpose Agent** - Creates metadata and overall purpose, infers role level
2. **Responsibilities Agent** - Generates 6-10 key responsibilities
3. **People Management Agent** - Determines management structure
4. **Scope Agent** - Creates contacts, innovation, decision-making, impact sections
5. **Requirements Agent** - Identifies licenses/certifications
6. **Working Conditions Agent** - Selects appropriate working condition templates

### Token Tracking

- Tracks input/output tokens for each agent call
- Calculates total usage across all 6 agents
- Computes costs based on model pricing
- Converts USD to CAD automatically
- Appends summary to generated job descriptions

## API Endpoints

### Web App

- `GET /` - Main web interface
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `POST /api/generate` - Generate job descriptions (both models)
- `GET /api/download/{provider}/{job_id}` - Download .txt file

## Deployment

### Local/Development

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Production (Linux/VPS)

See [README_WEBAPP.md](README_WEBAPP.md) for detailed deployment instructions.

## Cost Estimation

**Example: CTO Job Description**

| Model | Input Tokens | Output Tokens | Cost (USD) | Cost (CAD) |
|-------|-------------|---------------|------------|------------|
| Mistral Small | ~12,000 | ~6,000 | $0.006 | $0.008 |
| Claude Haiku | ~12,000 | ~6,000 | $0.034 | $0.048 |

*Costs vary based on job complexity and model responses*

## Troubleshooting

### Validation Errors
- Models have `retries=3` configured
- If errors persist, check API rate limits
- Try switching to different model variants in `config.py`

### Port Already in Use
```bash
# Use different port
uvicorn app:app --port 8001
```

## Support

For issues or questions:
- Check existing documentation in `CLAUDE.md`
- Review API provider documentation:
  - [Mistral AI Docs](https://docs.mistral.ai/)
  - [Anthropic Docs](https://docs.anthropic.com/)

---

**Note**: This tool generates draft job descriptions. Always review and customize outputs to match your specific organizational needs and legal requirements.
