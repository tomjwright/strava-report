# Deployment Guide

## Vercel vs Streamlit Cloud

**Important Note**: While Vercel is excellent for web apps, Streamlit requires a long-running Python server process, which Vercel's serverless architecture doesn't support natively. 

**Recommended**: Use **Streamlit Cloud** (free) - it's designed specifically for Streamlit apps and requires minimal configuration.

## Streamlit Cloud Deployment (Recommended)

### Steps:
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Select the repository and branch
5. Configure:
   - **Main file**: `clean_dashboard.py`
   - **Python version**: 3.11
   - **Requirements file**: `requirements.txt`
6. Add environment variables (from your `.env` file):
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `STRAVA_CLIENT_ID`
   - `STRAVA_CLIENT_SECRET`
7. Click "Deploy"

### Environment Variables for Streamlit Cloud:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
```

## Alternative: Render (Free Tier)

If you prefer Render over Streamlit Cloud:

1. Create a `render.yaml` file (included)
2. Go to [render.com](https://render.com)
3. Connect GitHub repository
4. Create new "Web Service"
5. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run clean_dashboard.py --server.port=$PORT --server.address=0.0.0.0`
6. Add same environment variables

## Automated Deployment with CI/CD

The GitHub Actions workflow is set up for:
- **develop branch**: Deploy to preview environment
- **main branch**: Deploy to production environment

For Streamlit Cloud, deployments are automatic when you push to connected branches.

## Current Status

- ✅ CI/CD pipeline configured
- ✅ Branch strategy (Main + Develop)
- ✅ Testing infrastructure
- ⏳ Awaiting your hosting platform choice

## Next Steps

1. Choose hosting platform (recommend: Streamlit Cloud)
2. Configure environment variables in hosting platform
3. Test deployment
4. Update CI/CD workflow with deployment scripts if needed