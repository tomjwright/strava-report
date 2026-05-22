# Deployment Guide

This guide covers deploying the Strava Activity Dashboard to various platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Options](#deployment-options)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

- Strava API credentials (Client ID, Client Secret, Refresh Token)
- Supabase project (or PostgreSQL database)
- Domain name (optional, for custom domains)
- Hosting account (depending on deployment option)

## Environment Setup

### 1. Prepare Environment Variables

Create a `.env` file with the following variables:

```env
# Strava API Configuration
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
STRAVA_REFRESH_TOKEN=your_strava_refresh_token
STRAVA_ACCESS_TOKEN=your_strava_access_token
STRAVA_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Application Configuration
APP_NAME=Strava Report
APP_VERSION=0.1.0
DEBUG=False
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False

# Webhook Configuration
WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_TIMEOUT=30

# ETL Configuration
ETL_BATCH_SIZE=100
ETL_RETRY_ATTEMPTS=3
ETL_RETRY_DELAY=5

# Frontend Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 2. Set Up Database

#### Using Supabase (Recommended)

1. Create a free Supabase account at [supabase.com](https://supabase.com)
2. Create a new project
3. Run database migrations:

```bash
cd backend
alembic upgrade head
```

4. Get your database URL from Supabase settings

#### Using PostgreSQL Directly

1. Set up a PostgreSQL instance
2. Create database and user
3. Run migrations:

```bash
cd backend
alembic upgrade head
```

### 3. Configure Strava Webhook

For real-time updates, you need to set up a Strava webhook:

1. Ensure your backend is publicly accessible
2. Subscribe to Strava webhooks:

```python
from app.services.strava_client import strava_client

# Replace with your actual webhook URL
callback_url = "https://your-domain.com/webhook"
verify_token = "your_verify_token"

subscription = strava_client.create_subscription(callback_url, verify_token)
print(f"Subscription created: {subscription}")
```

3. Add the subscription ID to your environment variables if needed

## Deployment Options

### Option 1: Streamlit Community Cloud (Free)

**Best for**: Simple deployment, prototyping, personal use

**Pros**:
- Completely free
- Easy setup
- Automatic deployments from Git
- Built-in authentication

**Cons**:
- Limited to apps under 200MB
- No custom backend deployment
- Limited customization

#### Steps:

1. **Deploy Backend to Render.com or Railway**

   Follow Option 2 for backend deployment first.

2. **Deploy Frontend to Streamlit**

   a. Create account at [streamlit.io](https://streamlit.io)
   
   b. Connect your GitHub repository
   
   c. Configure app:
   - Repository: `yourusername/strava-report`
   - Branch: `main`
   - Main file: `frontend/streamlit_app.py`
   
   d. Add environment variables in Streamlit settings:
   - `API_BASE_URL`: Your backend URL
   - Add any other required variables

3. **Test deployment**

   Visit your Streamlit app URL and verify functionality.

### Option 2: Render.com (Free Tier Available)

**Best for**: Full-stack deployment, custom backend

**Pros**:
- Free tier available
- Supports both frontend and backend
- Automatic SSL
- Easy database integration

**Cons**:
- Limited resources on free tier
- Cold starts on free tier
- Region limitations

#### Backend Deployment:

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up for free account

2. **Deploy Backend as Web Service**

   a. Click "New +" → "Web Service"
   
   b. Connect GitHub repository
   
   c. Configure:
   - Name: `strava-report-backend`
   - Branch: `main`
   - Root Directory: `backend`
   - Build Command: `pip install -r ../requirements.txt`
   - Start Command: `python -m app.main`
   - Instance Type: `Free` (or paid for better performance)

3. **Add Environment Variables**
   
   In Render dashboard, add all environment variables from your `.env` file

4. **Deploy**
   
   Render will automatically deploy on push to `main`

#### Frontend Deployment:

1. **Deploy Frontend as Web Service**

   a. Click "New +" → "Web Service"
   
   b. Configure:
   - Name: `strava-report-frontend`
   - Branch: `main`
   - Root Directory: `frontend`
   - Build Command: `pip install -r ../requirements.txt`
   - Start Command: `streamlit run streamlit_app.py --server.port=8501`
   - Instance Type: `Free`

2. **Add Environment Variables**
   
   - `API_BASE_URL`: Your backend Render URL
   - Other required variables

### Option 3: Railway.app (Free Tier Available)

**Best for**: Modern deployment experience, good free tier

**Pros**:
- Excellent free tier
- Modern UI
- Easy database deployment
- Good performance

**Cons**:
- Monthly free credits limit
- Learning curve for some features

#### Steps:

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up for free account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Services**

   Railway will detect your services automatically. Configure each:

   **Backend Service:**
   - Root directory: `backend`
   - Command: `python -m app.main`
   - Add environment variables

   **Frontend Service:**
   - Root directory: `frontend`
   - Command: `streamlit run streamlit_app.py`
   - Add environment variables

   **Database:**
   - Add PostgreSQL service
   - Run migrations in build command

4. **Deploy**

   Railway will automatically deploy all services

### Option 4: Self-Hosted (VPS)

**Best for**: Complete control, cost-effective at scale

**Pros**:
- Complete control
- Cost-effective for high traffic
- Can customize everything
- No platform limitations

**Cons**:
- Requires DevOps knowledge
- Must manage security
- Manual scaling
- No automatic updates

#### Requirements:
- VPS (DigitalOcean, Linode, AWS Lightsail, etc.)
- Domain name (recommended)
- SSL certificate (Let's Encrypt)

#### Steps:

1. **Set up VPS**
   - Choose VPS provider
   - Install Ubuntu 22.04 LTS
   - Secure with SSH keys

2. **Install Dependencies**

   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib certbot
   ```

3. **Set up Database**

   ```bash
   sudo -u postgres createdb strava_report
   sudo -u postgres createuser strava_user
   sudo -u postgres psql -c "ALTER USER strava_user PASSWORD 'secure_password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE strava_report TO strava_user;"
   ```

4. **Deploy Application**

   ```bash
   # Clone repository
   cd /var/www
   git clone https://github.com/yourusername/strava-report.git
   cd strava-report
   
   # Set up virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Run migrations
   cd backend
   alembic upgrade head
   
   # Set up systemd service for backend
   sudo nano /etc/systemd/system/strava-backend.service
   ```

   Create systemd service file:

   ```ini
   [Unit]
   Description=Strava Report Backend
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/strava-report/backend
   Environment="PATH=/var/www/strava-report/venv/bin"
   EnvironmentFile=/var/www/strava-report/.env
   ExecStart=/var/www/strava-report/venv/bin/python -m app.main
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl enable strava-backend
   sudo systemctl start strava-backend
   ```

5. **Set up Nginx**

   ```bash
   sudo nano /etc/nginx/sites-available/strava-report
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location /api/ {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /webhook {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location / {
           proxy_pass http://127.0.0.1:8501;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/strava-report /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. **Set up SSL**

   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## Monitoring

### Health Checks

Set up automated health checks:

```bash
# Check backend health
curl https://your-domain.com/health

# Expected response:
# {"status":"healthy","app_name":"Strava Report","version":"0.1.0","timestamp":"..."}
```

### Logging

Check application logs:

- **Render/Railway**: Check platform logs
- **Self-hosted**: Check `/var/log/strava-report/` or systemd journal
- **Streamlit**: Check Streamlit logs

### Monitoring Services

Consider using:
- **Uptime Robot** (Free): Uptime monitoring
- **Sentry** (Free tier): Error tracking
- **Prometheus + Grafana**: Advanced monitoring

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Problem**: Application can't connect to database

**Solutions**:
- Verify DATABASE_URL is correct
- Check database is running
- Verify firewall allows connections
- Check database credentials

#### 2. Strava API Errors

**Problem**: Strava API requests failing

**Solutions**:
- Verify API credentials are correct
- Check rate limits (100 requests/15min)
- Refresh access token if expired
- Check webhook subscription is active

#### 3. Webhook Not Receiving Events

**Problem**: Webhook events not being received

**Solutions**:
- Verify webhook is subscribed in Strava
- Check webhook URL is publicly accessible
- Verify WEBHOOK_VERIFY_TOKEN matches
- Check webhook handler logs

#### 4. Deployment Fails

**Problem**: Deployment fails on platform

**Solutions**:
- Check build logs for errors
- Verify all dependencies are in requirements.txt
- Check environment variables are set
- Verify branch protection rules aren't blocking

#### 5. Frontend Can't Connect to Backend

**Problem**: Dashboard shows connection errors

**Solutions**:
- Verify API_BASE_URL is correct
- Check CORS configuration
- Verify backend is running
- Check network/firewall settings

## Backup and Recovery

### Database Backups

#### Supabase
- Automatic daily backups
- Manual backups available in dashboard
- Point-in-time recovery up to 7 days

#### Self-hosted PostgreSQL
```bash
# Backup
pg_dump strava_report > backup.sql

# Restore
psql strava_report < backup.sql
```

### Code Backup
- Git repository serves as backup
- GitHub provides redundancy
- Regular commits recommended

## Security Checklist

- [ ] Environment variables for all secrets
- [ ] HTTPS enabled
- [ ] Database credentials secure
- [ ] API rate limiting implemented
- [ ] Input validation enabled
- [ ] CORS configured correctly
- [ ] Regular security updates
- [ ] Firewall rules configured
- [ ] Regular backups enabled
- [ ] Monitoring/alerting configured

## Performance Optimization

### Database
- Add indexes for frequently queried columns
- Use connection pooling
- Optimize queries
- Regular maintenance (VACUUM, ANALYZE)

### Application
- Enable caching where appropriate
- Use async operations
- Optimize ETL batch sizes
- Monitor memory usage

### Frontend
- Minimize API calls
- Use pagination
- Optimize chart rendering
- Lazy load components

---

For questions or issues with deployment, please open an issue on GitHub.
