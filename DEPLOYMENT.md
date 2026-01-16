# Deployment Guide - Scottco HR Tools Suite

This document describes how the scottco HR tools are deployed and configured on the VPS at `178.128.230.133`.

## Overview

The scottco suite consists of three components deployed together:
- **Landing Page** - Static HTML/CSS marketing page
- **Job Description Generator** - FastAPI web application (Python)
- **Job Evaluation Tool** - FastAPI web application (Python)

**Domain:** https://swift-base-8x4m.ca

## VPS Configuration

### Server Details
- **IP:** 178.128.230.133
- **OS:** Ubuntu
- **Web Server:** Nginx
- **Deployment Location:** `/var/www/scottco-github/`

### Directory Structure
```
/var/www/scottco-github/
├── landing/              # Static landing page
│   ├── index.html
│   ├── landing-styles.css
│   └── shared-styles.css
│
├── job-description/      # Job description generator
│   ├── .venv/           # Python virtual environment
│   ├── .env             # Environment variables (API keys)
│   ├── pyproject.toml   # Dependencies
│   ├── src/
│   │   └── job_description/  # Main package
│   │       ├── app.py        # FastAPI application
│   │       └── ...
│   └── static/          # Web UI files
│
└── job-evaluation/       # Job evaluation tool
    ├── .venv/           # Python virtual environment
    ├── .env             # Environment variables (API keys)
    ├── pyproject.toml   # Dependencies
    └── src/job_eval/    # Main package
```

## Deployment Process

### Automated Deployment (GitHub Actions)

Every push to `main` triggers automatic deployment:

1. **Code Pull** - Latest code pulled from GitHub
2. **Dependencies** - Installed via `uv` (fast Python package installer)
3. **Environment Variables** - Created from GitHub Secrets
4. **Services Restart** - systemd services restarted

See `.github/workflows/deploy.yml` for workflow details.

### Manual Deployment

If you need to deploy manually:

```bash
# SSH into VPS
ssh root@178.128.230.133

# Pull latest code
cd /var/www/scottco-github
git pull origin main

# Update job-description
cd job-description
source .venv/bin/activate
uv pip install pydantic-ai==0.1.6 pydantic>=2.0.0 anthropic>=0.40.0 fastapi>=0.104.0 'uvicorn[standard]>=0.24.0' python-multipart>=0.0.6 python-dotenv>=1.0.0
deactivate

# Update job-evaluation
cd ../job-evaluation
source .venv/bin/activate
uv pip install -e .
deactivate

# Restart services
sudo systemctl restart scottco job-eval
```

## System Services

### Job Description Generator (scottco.service)

**Service File:** `/etc/systemd/system/scottco.service`

```ini
[Unit]
Description=Scottco Job Description Generator (FastAPI)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/scottco-github/job-description
Environment="PATH=/var/www/scottco-github/job-description/.venv/bin"
EnvironmentFile=/var/www/scottco-github/job-description/.env
ExecStart=/var/www/scottco-github/job-description/.venv/bin/uvicorn job_description.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
sudo systemctl status scottco
sudo systemctl restart scottco
sudo systemctl stop scottco
sudo systemctl start scottco
sudo journalctl -u scottco -f  # View logs
```

### Job Evaluation Tool (job-eval.service)

**Service File:** `/etc/systemd/system/job-eval.service`

```ini
[Unit]
Description=Job Evaluation Tool
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/scottco-github/job-evaluation
Environment="PATH=/var/www/scottco-github/job-evaluation/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=/var/www/scottco-github/job-evaluation/.env
ExecStart=/var/www/scottco-github/job-evaluation/.venv/bin/job-eval serve --host 0.0.0.0 --port 8002
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
sudo systemctl status job-eval
sudo systemctl restart job-eval
sudo systemctl stop job-eval
sudo systemctl start job-eval
sudo journalctl -u job-eval -f  # View logs
```

## Nginx Configuration

**Config File:** `/etc/nginx/sites-available/multiapp`

### Landing Page (Root Path)
```nginx
location = / {
    root /var/www/scottco-github/landing;
    index index.html;
    try_files /index.html =404;
}

location /shared-styles.css {
    alias /var/www/scottco-github/landing/shared-styles.css;
}

location /landing-styles.css {
    alias /var/www/scottco-github/landing/landing-styles.css;
}
```

### Job Description Generator
```nginx
location /job-description {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Prefix /job-description;
    # ... additional proxy headers
}
```

### Job Evaluation Tool
```nginx
location /job-evaluation {
    proxy_pass http://127.0.0.1:8002;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Prefix /job-evaluation;
    # ... additional proxy headers
}
```

**Nginx Commands:**
```bash
sudo nginx -t              # Test configuration
sudo systemctl reload nginx # Reload config
sudo systemctl restart nginx # Restart Nginx
```

## SSL Certificates

Managed by Certbot (Let's Encrypt):

```bash
# Renew certificates
sudo certbot renew

# View certificate info
sudo certbot certificates

# Certificate location
/etc/letsencrypt/live/swift-base-8x4m.ca/
```

Auto-renewal is configured via systemd timer.

## Environment Variables

Environment variables are managed through GitHub Secrets and deployed automatically.

### Job Description (.env)
```bash
ANTHROPIC_API_KEY=sk-ant-...
MISTRAL_API_KEY=...
PORT=8000
```

### Job Evaluation (.env)
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

**To update API keys:**
1. Update GitHub Secrets at: https://github.com/rcurry16/scottco/settings/secrets/actions
2. Push any change to trigger redeployment (or manually update .env files)

## GitHub Secrets Required

Navigate to: https://github.com/rcurry16/scottco/settings/secrets/actions

**Deployment Secrets:**
- `VPS_HOST` - `178.128.230.133`
- `VPS_USER` - `root`
- `VPS_SSH_KEY` - Private SSH key for deployment

**API Keys:**
- `ANTHROPIC_API_KEY_JOB_DESC` - Claude API key for job description tool
- `ANTHROPIC_API_KEY_JOB_EVAL` - Claude API key for job evaluation tool
- `MISTRAL_API_KEY` - Mistral AI API key

## SSH Configuration

The VPS has a dedicated SSH key for accessing this GitHub repo:

**File:** `/root/.ssh/config`

```
Host github.com-scottco
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_scottco
    StrictHostKeyChecking no
```

**Public Key:** Added as deploy key at https://github.com/rcurry16/scottco/settings/keys

## URLs

- **Landing:** https://swift-base-8x4m.ca/
- **Job Description:** https://swift-base-8x4m.ca/job-description/
- **Job Evaluation:** https://swift-base-8x4m.ca/job-evaluation/

## Troubleshooting

### Service Won't Start
```bash
# Check service status
sudo systemctl status scottco
sudo systemctl status job-eval

# View recent logs
sudo journalctl -u scottco -n 50
sudo journalctl -u job-eval -n 50

# Check if ports are in use
sudo lsof -i :8000
sudo lsof -i :8002
```

### Nginx Issues
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Verify proxy connections
curl http://localhost:8000  # Should return job-description app
curl http://localhost:8002  # Should return job-eval app
```

### GitHub Actions Failing
1. Check workflow runs: https://github.com/rcurry16/scottco/actions
2. Verify secrets are set correctly
3. Check SSH key permissions on VPS
4. Verify `/var/www/scottco-github` exists and is accessible

### Dependency Issues
```bash
# Reinstall dependencies
cd /var/www/scottco-github/job-description
source .venv/bin/activate
uv pip install --force-reinstall pydantic-ai==0.1.6 pydantic>=2.0.0 anthropic>=0.40.0 fastapi>=0.104.0 'uvicorn[standard]>=0.24.0' python-multipart>=0.0.6 python-dotenv>=1.0.0
deactivate

cd /var/www/scottco-github/job-evaluation
source .venv/bin/activate
uv pip install --force-reinstall -e .
deactivate

sudo systemctl restart scottco job-eval
```

## Initial Setup (For Reference)

If setting up on a new server:

1. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv nginx certbot python3-certbot-nginx
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Generate SSH key for GitHub:**
   ```bash
   ssh-keygen -t ed25519 -C "vps-scottco@178.128.230.133" -f ~/.ssh/id_ed25519_scottco
   cat ~/.ssh/id_ed25519_scottco.pub  # Add to GitHub deploy keys
   ```

3. **Clone repository:**
   ```bash
   git clone git@github.com-scottco:rcurry16/scottco.git /var/www/scottco-github
   ```

4. **Set up virtual environments and dependencies** (as shown in Manual Deployment section)

5. **Create systemd service files** (content shown in System Services section)

6. **Enable and start services:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable scottco job-eval
   sudo systemctl start scottco job-eval
   ```

7. **Configure Nginx** (as shown in Nginx Configuration section)

8. **Get SSL certificate:**
   ```bash
   sudo certbot --nginx -d swift-base-8x4m.ca -d www.swift-base-8x4m.ca
   ```

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python 3.9+, FastAPI, uvicorn
- **AI:** Anthropic Claude, Mistral AI (via pydantic-ai)
- **Package Management:** uv (fast Python package installer)
- **Web Server:** Nginx
- **Process Management:** systemd
- **SSL:** Let's Encrypt via Certbot
- **CI/CD:** GitHub Actions

## Maintenance

### Regular Tasks
- Monitor disk space: `df -h`
- Check service status: `sudo systemctl status scottco job-eval`
- Review logs periodically: `sudo journalctl -u scottco -u job-eval --since "1 day ago"`
- SSL certificates auto-renew, but verify: `sudo certbot renew --dry-run`

### Updating Dependencies
Dependencies are updated on every deployment. To manually update:
- Update version numbers in `job-description/pyproject.toml` or `job-evaluation/pyproject.toml`
- Push to GitHub (triggers auto-deployment)
- Or manually run installation commands shown above

## Support

For issues or questions:
- Check logs: `sudo journalctl -u scottco -u job-eval -f`
- Review GitHub Actions runs: https://github.com/rcurry16/scottco/actions
- Verify all URLs are accessible
- Check that services are running: `sudo systemctl status scottco job-eval`
