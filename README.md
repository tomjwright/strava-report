# Strava Activity Dashboard (Simplified)

A streamlined Strava activity dashboard using Supabase for database operations. This version bypasses DNS issues by using the Supabase HTTP API instead of direct PostgreSQL connections.

## 🚀 Features

- **Strava API Integration**: Fetch and store activities from Strava
- **Supabase Database**: Reliable database operations via HTTP API
- **FastAPI Backend**: Modern Python web framework
- **Bronze Layer ETL**: Raw data ingestion from Strava
- **Memory Efficient**: Uses Polars for data processing

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Database**: Supabase PostgreSQL (via HTTP API)
- **Data Processing**: Polars (memory efficient)
- **API Client**: httpx for Strava API
- **Configuration**: Pydantic Settings

## 🚦 Quick Start

### Prerequisites

- Python 3.11+
- Supabase account (free tier)
- Strava API credentials

### Setup

1. **Clone and install**:
```bash
cd strava-report
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
# .env file should contain:
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
STRAVA_REFRESH_TOKEN=your_strava_refresh_token
STRAVA_ACCESS_TOKEN=your_strava_access_token
STRAVA_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

DATABASE_URL=  # Leave empty to use Supabase client
```

3. **Create database tables in Supabase**:
   - Go to https://supabase.com/dashboard
   - Navigate to your project
   - Open SQL Editor
   - Run the SQL to create tables:

```sql
CREATE TABLE IF NOT EXISTS bronze_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strava_id INTEGER UNIQUE NOT NULL,
    raw_data JSONB NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strava_id INTEGER UNIQUE NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    sport_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    distance FLOAT,
    moving_time INTEGER,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    start_date_local TIMESTAMP WITH TIME ZONE NOT NULL,
    -- Add other fields as needed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

4. **Run backend**:
```bash
cd backend
python -m app.main
```

Backend runs on http://localhost:8000 with API docs at /docs

## 🔧 API Endpoints

- `GET /` - Root endpoint with app info
- `GET /health` - Health check and database status
- `GET /api/activities` - List activities (with optional filtering)
- `POST /api/ingest` - Ingest a sample activity for testing
- `GET /docs` - Interactive API documentation (Swagger UI)

## 📊 Current Architecture

**Simplified Design**:
- Direct Supabase HTTP API client (bypasses DNS issues)
- Bronze layer for raw Strava data
- No complex ETL pipeline (dbt removed for simplicity)
- No webhooks (removed for simplicity)
- No silver/gold layers (removed for simplicity)

## 🧪 Testing the App

```bash
# Start the server
cd backend
python -m app.main

# The app runs on http://localhost:8003

# In another terminal, test the endpoints
curl http://localhost:8003/health
curl http://localhost:8003/api/activities
curl http://localhost:8003/api/bronze-activities
curl -X POST http://localhost:8003/api/ingest
curl -X POST "http://localhost:8003/api/fetch-strava?limit=10"
```

## 🎯 Demo Mode

The app includes a demo mode that automatically falls back to mock data from 2026 onwards if Strava API credentials are invalid. This allows you to test the functionality without needing valid Strava credentials.

The mock data includes:
- Running activities (5km runs)
- Cycling activities (15km rides)  
- Swimming activities (1km swims)
- Strength training activities

All mock activities are from **January 2026 onwards** as requested.

## 📁 Project Structure

```
strava-report/
├── backend/
│   └── app/
│       ├── main.py          # FastAPI application
│       ├── config.py        # Configuration settings
│       ├── db/
│       │   ├── database.py  # Database interface
│       │   └── supabase_adapter.py  # Supabase client
│       ├── services/
│       │   └── strava_client.py  # Strava API client
│       ├── etl/
│       │   └── bronze.py   # Bronze layer ETL
│       └── models/
│           └── activity.py  # Pydantic models
├── frontend/               # Streamlit dashboard (if configured)
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

## ⚠️ Why This Simplified Version?

This version was created to address Windows DNS resolution issues with PostgreSQL connections. By using the Supabase HTTP API client instead of direct PostgreSQL connections, we bypass the DNS problems entirely while maintaining full functionality.

## 🔄 From Complex to Simple

**Removed for simplicity**:
- dbt SQL transformations (Windows installation issues)
- Alembic database migrations (not needed with Supabase client)
- Webhook handling (removed for simplicity)
- Silver/Gold ETL layers (removed for simplicity)
- Complex CI/CD pipelines (simplified)
- Extensive testing (basic functionality only)

**Kept for functionality**:
- Strava API integration
- Supabase database operations
- FastAPI backend
- Basic ETL pipeline (Bronze layer)
- Streamlit dashboard framework

## 🎯 Next Steps

1. **Create the database tables** in Supabase SQL Editor
2. **Test the Strava API** by ingesting real activities
3. **Configure the dashboard** if using Streamlit
4. **Add features** as needed based on your requirements

## 📄 License

This project is licensed under the MIT License.