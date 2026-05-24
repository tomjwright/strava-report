# Quick Vercel Deployment - Your Specific Configuration

## Your Environment Variables (Copy These for Vercel)

Based on your current `.env` file, add these exact values to Vercel:

### Vercel Environment Variables:

```
NEXT_PUBLIC_SUPABASE_URL=https://pnidlzgqvflwlyxbmlcf.supabase.co
NEXT_PUBLIC_SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuaWRsemdxdmZsd2x5eGJtbGNmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk0Mjg1MDAsImV4cCI6MjA5NTAwNDUwMH0.cvKr-D_WIGlsrBe_2p9DxG7bL43O14oE8nr2OR1LGqw
```

**Note**: These are safe to use in Vercel - they're your Supabase public/anon credentials designed for frontend use.

## Quick Deployment Steps:

### 1. Go to Vercel
Visit [vercel.com](https://vercel.com) and login/signup

### 2. Import Your Repository
- Click "Add New..." → "Project"
- Select: `tomjwright/strava-report`
- Click "Import"

### 3. Configure Project (IMPORTANT!)
Vercel should now detect Next.js correctly. Make sure:
- **Root Directory**: `frontend` (CRITICAL - this fixes the detection issue!)
- **Framework Preset**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`

**Note**: I've fixed the Vercel detection issue by:
- Moving `vercel.json` to the `frontend/` directory
- Adding `.vercelignore` to ignore Python files
- Configuring proper Next.js detection

If Vercel still detects incorrectly, manually set the framework to "Next.js" and ensure root directory is `frontend`.

### 4. Add Environment Variables
In Vercel project settings:
1. Go to Settings → Environment Variables
2. Add the two variables above (copy exactly)
3. Click "Save"

### 5. Deploy
- Click "Deploy"
- Wait 2-3 minutes for build
- Visit your new Vercel URL!

### 6. Test the Dashboard
Your dashboard should show:
- Dark theme with blue/purple accents
- Statistics cards with your activity data
- Multiple charts (distance, time, activity types)
- Recent activities list

## Current Database Status

Your Supabase database already has:
- ✅ 143 activities loaded
- ✅ Data from 2026 (352.83 km total distance)
- ✅ Activity breakdown: Run, Swim, WeightTraining, etc.

## Optional: Deploy Backend

If you want the FastAPI backend deployed:

### Render Deployment:
1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect repository: `tomjwright/strava-report`
4. Environment variables:
```
SUPABASE_URL=https://pnidlzgqvflwlyxbmlcf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuaWRsemdxdmZsd2x5eGJtbGNmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk0Mjg1MDAsImV4cCI6MjA5NTAwNDUwMH0.cvKr-D_WIGlsrBe_2p9DxG7bL43O14oE8nr2OR1LGqw
STRAVA_CLIENT_ID=249256
STRAVA_CLIENT_SECRET=96af13f3695346651a76fd82e646f7de2be91510
STRAVA_REFRESH_TOKEN=975e24a5926053f60b1891724b87912f42977c50
```
5. Start command: `uvicorn simple_backend:app --host 0.0.0.0 --port $PORT`

## Next Steps After Deployment

1. **Test the live dashboard** at your Vercel URL
2. **Set up custom domain** (optional) in Vercel settings
3. **Configure CI/CD** for auto-deployment (see VERCEL_SETUP.md)
4. **Set up automated data loading** with auto_loader.py

## Troubleshooting

If dashboard shows no data:
- Check Supabase database has `strava_activities` table
- Verify environment variables are copied correctly
- Check Vercel deployment logs for errors

If charts don't display:
- Check browser console (F12) for JavaScript errors
- Verify Recharts is installed (check build logs)
- Ensure data format is correct

Your setup is ready to go! 🚀