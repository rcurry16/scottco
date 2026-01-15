# Deployment Guide

## What Was Added

A modern web interface for the job evaluation tool with:

1. **DOCX Support** - Tools now accept both PDF and DOCX files
2. **FastAPI Backend** - Two REST endpoints:
   - `/api/classify` - Single document classification
   - `/api/full-workflow` - Complete analysis (compare → gauge → classify)
3. **Modern Frontend** - Vanilla HTML/CSS/JS interface with:
   - Drag-and-drop file upload
   - Two workflow modes
   - Formatted report display
   - Copy-to-clipboard functionality

## Quick Start

```bash
# 1. Install dependencies
uv pip install -e .

# 2. Ensure .env has your API key
echo "ANTHROPIC_API_KEY=your_key" > .env

# 3. Extract classification standards (if not done)
uv run python src/job_eval/extract_standards.py

# 4. Start server
job-eval serve

# 5. Open http://localhost:8000
```

## File Structure

```
src/job_eval/
├── api.py                  # FastAPI app with endpoints
├── server.py               # Server runner
├── document_processor.py   # Unified PDF/DOCX handler
├── docx_processor.py       # DOCX text extraction
├── pdf_processor.py        # PDF text extraction (existing)
├── static/
│   ├── index.html          # Main UI
│   ├── styles.css          # Modern styling
│   └── app.js              # Frontend logic
└── [existing tools updated for DOCX support]
```

## Usage

### Web Interface

1. **Full Analysis Mode**:
   - Upload BEFORE document (PDF or DOCX)
   - Upload AFTER document (PDF or DOCX)
   - Click Analyze
   - Get comprehensive report from all 3 tools

2. **Quick Classification Mode**:
   - Upload single position description
   - Click Analyze
   - Get classification recommendation

3. **Copy Results**:
   - Click "Copy to Clipboard" button
   - Paste formatted report anywhere

### CLI (Still Available)

```bash
# Full workflow
job-eval compare old.pdf new.pdf --with-classify

# Single classification
job-eval classify position.docx
```

## VPS Deployment

### Basic Setup

```bash
# On VPS
git clone <your-repo>
cd job-eval

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .

# Create .env
echo "ANTHROPIC_API_KEY=your_key" > .env

# Extract standards (one-time)
uv run python src/job_eval/extract_standards.py

# Run server
job-eval serve --host 0.0.0.0 --port 8000
```

### Systemd Service (Auto-restart)

Create `/etc/systemd/system/job-eval.service`:

```ini
[Unit]
Description=Job Evaluation Tool
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/job-eval
Environment="PATH=/home/youruser/.local/bin:/usr/bin"
Environment="ANTHROPIC_API_KEY=your_key_here"
ExecStart=/home/youruser/.local/bin/job-eval serve --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable job-eval
sudo systemctl start job-eval
sudo systemctl status job-eval
```

### Nginx Reverse Proxy (Optional)

`/etc/nginx/sites-available/job-eval`:

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

        # Large file uploads
        client_max_body_size 50M;
        proxy_read_timeout 300s;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/job-eval /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL with Let's Encrypt (Optional)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Server Commands

```bash
# Start server (default: 0.0.0.0:8000)
job-eval serve

# Custom host/port
job-eval serve --host 127.0.0.1 --port 5000

# Development mode (auto-reload on code changes)
job-eval serve --reload

# Help
job-eval serve --help
```

## Testing

### Local Testing

```bash
# Start server
job-eval serve --reload

# Open browser
open http://localhost:8000

# Test with sample PDFs
# Upload Position Levels/EC 02 and EC 05 files
```

### API Testing (curl)

```bash
# Health check
curl http://localhost:8000/api/health

# Classify single doc
curl -X POST http://localhost:8000/api/classify \
  -F "file=@position.pdf"

# Full workflow
curl -X POST http://localhost:8000/api/full-workflow \
  -F "old_file=@old.pdf" \
  -F "new_file=@new.pdf"
```

## Security Notes

- **No authentication** - Currently open access
- **API key security** - Keep .env file private, never commit
- **File uploads** - Temporary files cleaned up after processing
- **CORS** - Currently allows all origins (change in production if needed)

For production with multiple users, consider:
- Adding basic auth (password or API key)
- Rate limiting
- File size limits (currently unlimited)
- HTTPS (via reverse proxy)

## Troubleshooting

### Server won't start

```bash
# Check if port is in use
lsof -i :8000

# Try different port
job-eval serve --port 8001
```

### Import errors

```bash
# Reinstall dependencies
uv pip install -e .

# Check installation
uv run python -c "from job_eval.api import app; print('OK')"
```

### DOCX files not processing

```bash
# Verify python-docx installed
uv pip list | grep python-docx

# Reinstall
uv pip install python-docx
```

### API key not found

```bash
# Check .env exists
cat .env

# Set in environment directly
export ANTHROPIC_API_KEY=your_key
job-eval serve
```

## Development

### Frontend changes

Edit files in `src/job_eval/static/`:
- `index.html` - Structure
- `styles.css` - Styling
- `app.js` - Logic

Refresh browser to see changes.

### Backend changes

Edit `src/job_eval/api.py`, then:

```bash
# Restart with auto-reload
job-eval serve --reload
```

### Adding new endpoints

1. Add route in `api.py`:
```python
@app.post("/api/your-endpoint")
async def your_endpoint():
    # Your logic
    return {"result": "data"}
```

2. Call from frontend in `app.js`:
```javascript
const response = await fetch('/api/your-endpoint', {
    method: 'POST',
    body: formData
});
```

## Support

For issues:
- Check logs: `journalctl -u job-eval -f` (if using systemd)
- Test CLI still works: `job-eval classify test.pdf`
- Verify API key: Check .env file
- Check dependencies: `uv pip list`
