# Strava Activity Dashboard (Next.js + Vercel)

Modern Strava activity dashboard with Next.js frontend, FastAPI backend, and Supabase database. Deployed on Vercel for optimal performance and developer experience.

## 🚀 Features

- **Modern Next.js Frontend**: React-based dashboard with dark theme
- **FastAPI Backend**: Python API with CORS enabled
- **Supabase Database**: Reliable PostgreSQL database
- **Strava Integration**: Fetch and store activities automatically
- **CI/CD Pipeline**: Automated testing and deployment
- **Vercel Hosting**: Optimized for Next.js applications
- **Responsive Design**: Works on desktop and mobile

## 🛠️ Technology Stack

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Modern utility-first styling
- **Recharts**: Beautiful chart library
- **Supabase Client**: Database connectivity

### Backend
- **Python 3.11+**: Modern Python
- **FastAPI**: High-performance API framework
- **Supabase**: Database client
- **Uvicorn**: ASGI server

### Infrastructure
- **Vercel**: Frontend hosting and CI/CD
- **Render/Railway**: Backend hosting (optional)
- **GitHub Actions**: Automated testing and deployment

## 🚦 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account (free tier)
- Strava API credentials

### Frontend Setup

```bash
cd frontend
npm install
cp ../.env.example .env.local
# Edit .env.local with your Supabase credentials
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### Backend Setup

```bash
# From project root
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn simple_backend:app --reload
```

Backend runs on [http://localhost:8006](http://localhost:8006)

### Database Setup

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Run this SQL in the SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS strava_activities (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    distance FLOAT NOT NULL,
    moving_time INTEGER NOT NULL,
    elapsed_time INTEGER NOT NULL,
    total_elevation_gain FLOAT DEFAULT 0,
    average_speed FLOAT DEFAULT 0,
    max_speed FLOAT DEFAULT 0,
    average_heartrate FLOAT,
    max_heartrate FLOAT,
    location_city VARCHAR(255),
    location_country VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 📊 Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Vercel (Frontend) │  ──▶  │  FastAPI Backend  │
│  - Next.js      │         │  - API Endpoints  │
│  - React Charts │         │  - CORS Enabled  │
└─────────────────┘         └──────────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │  Supabase    │
                              │  Database    │
                              └──────────────┘
```

## 🔧 Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_KEY=your_supabase_key
```

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
STRAVA_REFRESH_TOKEN=your_strava_refresh_token
```

## 🚀 Deployment

### Vercel (Frontend)
1. Connect your GitHub repository to Vercel
2. Set root directory to `frontend`
3. Add environment variables
4. Deploy automatically on push to main/develop

### Backend (Render/Railway)
1. Create a new web service
2. Connect your GitHub repository
3. Add environment variables
4. Deploy with `uvicorn simple_backend:app --host 0.0.0.0 --port $PORT`

## 📁 Project Structure

```
strava-report/
├── frontend/              # Next.js frontend
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and clients
│   └── package.json      # Frontend dependencies
├── simple_backend.py      # FastAPI backend
├── simple_data_loader.py # Strava data ingestion
├── auto_loader.py        # Scheduled data loading
├── tests/                # Test suite
├── .github/              # CI/CD workflows
└── requirements.txt      # Python dependencies
```

## 🔄 CI/CD Pipeline

- **develop branch**: Auto-deploy to Vercel preview
- **main branch**: Auto-deploy to Vercel production
- **All branches**: Run tests and linting

## 🧪 Testing

```bash
# Backend tests
pytest tests/ -v

# Frontend build
cd frontend
npm run build
```

## 📄 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Complete deployment instructions
- [Branch Strategy](BRANCH_STRATEGY.md) - Git workflow and branching
- [Frontend README](frontend/README.md) - Frontend-specific documentation

## 🎯 Current Status

- ✅ Next.js frontend with dark theme
- ✅ FastAPI backend with CORS
- ✅ Supabase database integration
- ✅ CI/CD pipeline configured
- ✅ Vercel deployment ready
- ⏳ Charts implementation pending
- ⏳ Production deployment pending

## 📄 License

This project is licensed under the MIT License.