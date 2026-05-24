# Deployment Guide

## Architecture Overview

This project now uses a modern **Next.js + Vercel** architecture:

```
┌─────────────────┐         ┌──────────────────┐
│  Vercel (Frontend) │  ──▶  │  Render/Railway  │
│  - Next.js      │         │  - FastAPI Backend│
│  - React Charts │         │  - API Endpoints  │
└─────────────────┘         └──────────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │  Supabase    │
                              │  Database    │
                              └──────────────┘
```

## Vercel Deployment (Frontend)

### Setup Steps:

1. **Install Vercel CLI** (optional):
   ```bash
   npm install -g vercel
   ```

2. **Deploy via Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Configure:
     - **Framework Preset**: Next.js
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `.next`

3. **Add Environment Variables**:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_KEY=your_supabase_key
   ```

4. **Deploy**: Click "Deploy"

### Automatic Deployment with CI/CD:

The GitHub Actions workflow automatically deploys to Vercel:
- **develop branch** → Vercel Preview
- **main branch** → Vercel Production

Required GitHub Secrets:
- `VERCEL_TOKEN` (from Vercel account settings)
- `VERCEL_ORG_ID` (from Vercel project)
- `VERCEL_PROJECT_ID` (from Vercel project)

## Backend Deployment (FastAPI)

### Option 1: Render (Recommended)

1. Go to [render.com](https://render.com)
2. Create new "Web Service"
3. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn simple_backend:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   STRAVA_CLIENT_ID=your_strava_client_id
   STRAVA_CLIENT_SECRET=your_strava_client_secret
   STRAVA_REFRESH_TOKEN=your_strava_refresh_token
   ```

### Option 2: Railway

1. Go to [railway.app](https://railway.app)
2. Create new project
3. Deploy from GitHub
4. Add environment variables (same as above)

## Local Development

### Frontend (Next.js):
```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:3000
```

### Backend (FastAPI):
```bash
pip install -r requirements.txt
uvicorn simple_backend:app --reload
# Visit http://localhost:8006
```

### Environment Setup:
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
# Edit .env with your actual values
```

## Current Status

- ✅ Next.js frontend created
- ✅ Vercel configuration added
- ✅ CI/CD pipeline updated for Next.js
- ✅ Backend CORS enabled
- ✅ Dark theme implemented
- ⏳ Backend deployment pending
- ⏳ Vercel project setup pending

## Next Steps

1. Set up Vercel project and connect GitHub repo
2. Add required environment variables in Vercel
3. Deploy backend to Render/Railway
4. Update frontend API URLs if needed
5. Test the complete application

## Troubleshooting

- **Frontend build fails**: Check Node.js version (requires 18+)
- **Supabase connection fails**: Verify URL and key in environment variables
- **CORS errors**: Backend CORS is configured with wildcard for development