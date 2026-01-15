# Scottco - HR Tools Suite

Professional HR tools for job description generation, job evaluation, and classification. Deployed at [swift-base-8x4m.ca](https://swift-base-8x4m.ca).

## Components

### 1. Landing Page (`landing/`)
- Marketing/info page for the HR tools suite
- Static HTML/CSS
- Served at root path: https://swift-base-8x4m.ca/

### 2. Job Description Generator (`job-description/`)
- AI-powered job description generator
- Dual AI models: Mistral Small + Anthropic Claude
- Side-by-side comparison with cost tracking
- FastAPI web application
- Served at: https://swift-base-8x4m.ca/job-description

**Tech Stack:** Python, FastAPI, pydantic-ai, Mistral AI, Anthropic Claude

### 3. Job Evaluation Tool (`job-evaluation/`)
- Position classification and evaluation system
- Analyzes job descriptions against classification standards
- Provides EC grade recommendations with rationale
- Python CLI + web interface
- Served at: https://swift-base-8x4m.ca/job-evaluation

**Tech Stack:** Python, FastAPI, Anthropic Claude, PDF processing

## Deployment

### Automated Deployment (GitHub Actions)

Pushing to `main` automatically deploys to VPS:

1. Code is pulled to `/var/www/scottco-github/`
2. `.env` files are created from GitHub Secrets
3. Services are restarted (if configured)

### Environment Variables

Required secrets in GitHub (Settings → Secrets → Actions):

- `VPS_HOST` - VPS IP address
- `VPS_USER` - SSH user
- `VPS_SSH_KEY` - Private SSH key for deployment
- `ANTHROPIC_API_KEY_JOB_DESC` - Claude API key for job description tool
- `ANTHROPIC_API_KEY_JOB_EVAL` - Claude API key for job evaluation tool
- `MISTRAL_API_KEY` - Mistral AI API key

### Local Development

Each component has its own setup instructions in its subdirectory.

**Job Description Generator:**
```bash
cd job-description
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn app:app --reload --port 8000
```

**Job Evaluation Tool:**
```bash
cd job-evaluation
python3 -m venv .venv
source .venv/bin/activate
uv pip install -e .
cp .env.example .env  # Add your API key
job-eval serve --port 8002
```

## Repository Structure

```
scottco/
├── landing/              # Static landing page
│   ├── index.html
│   ├── landing-styles.css
│   └── shared-styles.css
│
├── job-description/      # Job description generator
│   ├── app.py           # FastAPI web app
│   ├── models.py        # Data models
│   ├── config.py        # Configuration
│   ├── static/          # Web UI files
│   └── requirements.txt
│
├── job-evaluation/       # Job evaluation tool
│   ├── src/job_eval/    # Main package
│   ├── data/            # Classification standards
│   ├── Position Levels/ # Sample JDs
│   └── pyproject.toml
│
└── .github/
    └── workflows/
        └── deploy.yml   # Auto-deployment workflow
```

## Production URLs

- **Landing:** https://swift-base-8x4m.ca/
- **Job Description:** https://swift-base-8x4m.ca/job-description
- **Job Evaluation:** https://swift-base-8x4m.ca/job-evaluation

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI, uvicorn
- **AI:** Anthropic Claude, Mistral AI
- **Deployment:** GitHub Actions, Nginx, systemd
- **Server:** Ubuntu VPS

## License

Private repository - all rights reserved.
