# Vercel Deployment Setup Guide

Complete step-by-step guide to deploy your Strava Dashboard to Vercel.

## Prerequisites

- GitHub account with the repository pushed
- Vercel account (free)
- Supabase project with your data

## Step 1: Connect Repository to Vercel

1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "Add New..." → "Project"
3. Import your GitHub repository: `tomjwright/strava-report`
4. Vercel will automatically detect the Next.js configuration

## Step 2: Configure Vercel Project

### Project Settings:
- **Framework Preset**: Next.js
- **Root Directory**: `frontend` (important!)
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`

### Environment Variables:
Add these in Vercel project settings → Environment Variables:

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_KEY=your_supabase_anon_key
```

**Where to find these values:**
- Go to your [Supabase Dashboard](https://supabase.com/dashboard)
- Select your project
- Settings → API
- Copy Project URL and anon/public key

## Step 3: Deploy

1. Click "Deploy" button
2. Vercel will build and deploy your frontend
3. Wait for the build to complete (2-3 minutes)
4. You'll get a URL like: `https://your-project.vercel.app`

## Step 4: Verify Deployment

1. Visit your Vercel URL
2. You should see the Strava Dashboard
3. Check that activities load from your Supabase database
4. Test the dark theme and charts

## Step 5: Set Up Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Domains → Add Domain
3. Add your custom domain (e.g., `strava.yourdomain.com`)
4. Update DNS records as instructed by Vercel

## Step 6: Configure CI/CD for Auto-Deployment

### Get Vercel Credentials:

1. Vercel Account Settings → Tokens
2. Create a new token named "GitHub Actions"
3. Copy the token

4. Go to your Vercel project → Settings → General
5. Copy Project ID and Team ID (if applicable)

### Add GitHub Secrets:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:

```
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_team_id (or personal)
VERCEL_PROJECT_ID=your_project_id
```

### Test CI/CD:

Push to `develop` branch → should deploy to preview
Push to `main` branch → should deploy to production

## Step 7: Backend Deployment (Optional)

If you need the FastAPI backend:

### Option 1: Render (Recommended)

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repository
4. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn simple_backend:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   STRAVA_CLIENT_ID=your_strava_client_id
   STRAVA_CLIENT_SECRET=your_strava_client_secret
   STRAVA_REFRESH_TOKEN=your_strava_refresh_token
   ```

### Option 2: Railway

1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub repo
3. Add environment variables (same as above)
4. Railway will automatically deploy

## Step 8: Update Frontend URLs (If Using Backend)

If you deploy the backend separately, update the frontend to call the backend API instead of Supabase directly:

```typescript
// In frontend/lib/supabase.ts
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8006'

export async function fetchActivities() {
  const response = await fetch(`${BACKEND_URL}/api/activities`)
  return response.json()
}
```

Add to Vercel environment variables:
```
NEXT_PUBLIC_BACKEND_URL=your_backend_url
```

## Troubleshooting

### Build Fails:
- Check that root directory is set to `frontend`
- Verify Node.js version (Vercel uses 18+ by default)
- Check environment variables are set correctly

### Data Not Loading:
- Verify Supabase credentials are correct
- Check Supabase database has the `strava_activities` table
- Ensure Row Level Security (RLS) allows public access

### Charts Not Displaying:
- Check browser console for errors
- Verify Recharts is installed correctly
- Ensure data format matches expected structure

## Current Status

✅ Frontend: Complete with charts and dark theme
✅ Backend: Tested and working
✅ CI/CD: Configured for Vercel deployment
✅ Documentation: Complete setup guides

## Next Steps

1. Deploy frontend to Vercel (follow steps above)
2. Test the deployed application
3. Optionally deploy backend to Render/Railway
4. Set up custom domain (optional)
5. Configure automated data loading