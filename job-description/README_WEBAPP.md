# Job Description Generator - Web Application

Web interface for generating AI-powered job descriptions using both Mistral and Anthropic models with side-by-side comparison.

## Features

- ✅ **Dual Model Generation**: Runs both Mistral & Anthropic models in parallel
- ✅ **Side-by-Side Comparison**: Compare outputs from both models
- ✅ **Editable Config**: Update organizational context (name, industry, location) from the web UI
- ✅ **Easy Export**: Copy-to-clipboard and download as .txt files
- ✅ **No Authentication**: Single-user testing tool
- ✅ **Simple Deployment**: Easy to deploy on any VPS or cloud platform

## Prerequisites

- Python 3.9+
- API Keys:
  - Mistral API key
  - Anthropic API key

## Local Development

### 1. Install Dependencies

```bash
cd job-desc-tool/
pip install -r requirements_webapp.txt
```

### 2. Set Environment Variables

```bash
export MISTRAL_API_KEY=your_mistral_api_key_here
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Run the Application

```bash
uvicorn app:app --reload
```

Or use the built-in runner:

```bash
python app.py
```

### 4. Open in Browser

Navigate to: **http://localhost:8000**

## Deployment on Digital Ocean / VPS

### Option 1: Manual Deployment

#### 1. SSH into your server

```bash
ssh root@your-server-ip
```

#### 2. Install Python 3.9+

```bash
apt update
apt install python3 python3-pip python3-venv -y
```

#### 3. Clone or Upload Your Code

```bash
mkdir -p /var/www/job-desc-generator
cd /var/www/job-desc-generator
# Upload your code here or use git clone
```

#### 4. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_webapp.txt
```

#### 5. Set Environment Variables

Create a `.env` file or add to `/etc/environment`:

```bash
export MISTRAL_API_KEY=your_mistral_key
export ANTHROPIC_API_KEY=your_anthropic_key
```

Or create a systemd service file with environment variables (recommended).

#### 6. Create Systemd Service

Create `/etc/systemd/system/job-desc-generator.service`:

```ini
[Unit]
Description=Job Description Generator Web App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/job-desc-generator
Environment="MISTRAL_API_KEY=your_mistral_key"
Environment="ANTHROPIC_API_KEY=your_anthropic_key"
ExecStart=/var/www/job-desc-generator/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 7. Enable and Start Service

```bash
systemctl daemon-reload
systemctl enable job-desc-generator
systemctl start job-desc-generator
systemctl status job-desc-generator
```

#### 8. Setup Nginx Reverse Proxy (Optional but Recommended)

Install Nginx:

```bash
apt install nginx -y
```

Create `/etc/nginx/sites-available/job-desc-generator`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or your server IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
ln -s /etc/nginx/sites-available/job-desc-generator /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 9. Setup Firewall

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

#### 10. Optional: Setup SSL with Let's Encrypt

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

### Option 2: Docker Deployment (Alternative)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_webapp.txt .
RUN pip install --no-cache-dir -r requirements_webapp.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./output:/app/output
    restart: unless-stopped
```

Run:

```bash
docker-compose up -d
```

## Usage

1. **Configure Organization** (top section):
   - Set your organization name, industry, and location
   - Click "Save Configuration"

2. **Fill Out Job Information**:
   - Complete all 12 questions about the position
   - Required fields are marked with *

3. **Generate**:
   - Click "Generate Job Descriptions"
   - Wait 30-60 seconds for both models to complete

4. **Review & Export**:
   - Compare Mistral and Anthropic outputs side-by-side
   - Use "Copy All" to copy to clipboard
   - Use "Download .txt" to save individual files

## Directory Structure

```
job-desc-tool/
├── app.py                          # FastAPI application
├── config.py                       # Configuration file
├── models.py                       # Pydantic data models
├── output_formatter.py             # Output formatting utilities
├── job_desc_generator_v2_mistral.py    # Mistral generator
├── job_desc_generator_v2_anthropic.py  # Anthropic generator
├── requirements_webapp.txt         # Web app dependencies
├── static/
│   ├── index.html                  # Frontend HTML
│   ├── styles.css                  # Styling
│   └── script.js                   # Frontend JavaScript
└── output/                         # Generated job descriptions
```

## Configuration

Edit organizational defaults in `config.py`:

```python
ORGANIZATION_NAME = "Your Organization Name"
INDUSTRY = "Public Sector"
LOCATION = "Nova Scotia, Canada"
```

These can also be edited from the web UI without restarting the app.

## Troubleshooting

### Application won't start

- Check that both API keys are set:
  ```bash
  echo $MISTRAL_API_KEY
  echo $ANTHROPIC_API_KEY
  ```

- Check application logs:
  ```bash
  journalctl -u job-desc-generator -f
  ```

### Generation fails

- Verify API keys are correct
- Check API rate limits
- Review error messages in the web UI
- Check server logs for detailed error information

### Port already in use

- Change the port in the systemd service or when running locally:
  ```bash
  uvicorn app:app --port 8001
  ```

### Can't access from outside

- Ensure firewall allows port 80/443
- If using Nginx, verify proxy configuration
- Check that app is bound to `0.0.0.0` not `127.0.0.1`

## Security Notes

⚠️ **Important**: This is a single-user testing tool with no authentication.

For production use:
- Add authentication (Basic Auth, OAuth, etc.)
- Use HTTPS (Let's Encrypt)
- Restrict access via firewall or VPN
- Store API keys securely (environment variables, not in code)
- Add rate limiting
- Add input validation and sanitization

## Performance

- Each generation takes approximately 30-60 seconds
- Both models run in parallel to minimize total time
- Results are cached in memory during the session
- Output files are saved to `output/` directory

## Support

For issues or questions:
- Check the main project CLAUDE.md for architecture details
- Review API provider documentation
- Ensure all dependencies are installed correctly

## License

Same as parent project.
