# System Architecture

This document describes the system architecture of the Strava Activity Dashboard.

## Overview

The Strava Activity Dashboard follows a modern microservices-inspired architecture with clear separation of concerns:

- **Backend API**: FastAPI-based REST API
- **ETL Pipeline**: Medallion architecture data processing
- **Frontend**: Streamlit dashboard
- **Database**: PostgreSQL with Supabase
- **Real-time**: Strava webhooks

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Layer                           │
│  ┌──────────────┐          ┌──────────────┐                │
│  │   Browser    │          │   Strava     │                │
│  │  (Dashboard) │          │     App      │                │
│  └──────┬───────┘          └──────┬───────┘                │
└─────────┼──────────────────────────┼───────────────────────┘
          │                          │
          │ HTTPS                    │ HTTPS
          ▼                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                          │
│  ┌─────────────────────┐   ┌─────────────────────┐        │
│  │  Streamlit Dashboard │   │    FastAPI Backend   │        │
│  │  - Activity Views   │◄──│  - REST API         │        │
│  │  - Analytics        │   │  - Webhook Handler  │        │
│  │  - Filtering        │   │  - Business Logic   │        │
│  └─────────────────────┘   └──────────┬──────────┘        │
└──────────────────────────────────────────┼──────────────────┘
                                             │
                                             │
┌────────────────────────────────────────────┼──────────────────┐
│                ETL Pipeline Layer          │                  │
│  ┌────────┐  ┌────────┐  ┌────────┐       │                  │
│  │ Bronze │  │ Silver │  │  Gold  │       │                  │
│  │  Raw   │──│ Clean  │──│ Final  │◄──────┘                  │
│  │  Ingest│  │ Validate│  │ Enrich │                          │
│  └────────┘  └────────┘  └────────┘                            │
└───────────────────────────────────────────────────────────────┘
                        │
                        │ SQL
                        ▼
┌───────────────────────────────────────────────────────────────┐
│                     Data Layer                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              PostgreSQL (Supabase)                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐ │  │
│  │  │   Bronze    │  │   Silver    │  │     Gold      │ │  │
│  │  │ Activities  │  │ Activities  │  │  Activities   │ │  │
│  │  └─────────────┘  └─────────────┘  └───────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Backend

**Purpose**: REST API for data access and webhook handling

**Key Components**:
- **Main Application** (`app/main.py`): FastAPI app setup
- **API Routes** (`app/api/`): REST endpoints
- **Webhook Handler** (`app/services/webhook_handler.py`): Strava webhook processing
- **Strava Client** (`app/services/strava_client.py`): Strava API integration

**Technologies**:
- FastAPI 0.104+
- Pydantic for validation
- SQLAlchemy ORM
- Uvicorn ASGI server

**Endpoints**:
- `/api/activities/` - CRUD operations for activities
- `/api/activities/stats/*` - Statistical endpoints
- `/webhook` - Strava webhook handling
- `/etl/run` - Manual ETL trigger
- `/health` - Health checks

### 2. ETL Pipeline

**Purpose**: Process and transform Strava data using medallion architecture

**Bronze Layer** (`app/etl/bronze.py`):
- **Input**: Raw Strava API responses
- **Processing**: Minimal validation, store as-is
- **Output**: `bronze_activities` table
- **Purpose**: Audit trail, data recovery

**Silver Layer** (`app/etl/silver.py`):
- **Input**: Bronze layer data
- **Processing**: 
  - Data cleaning
  - Type standardization
  - Validation
  - Null handling
- **Output**: `silver_activities` table
- **Purpose**: Quality assurance

**Gold Layer** (`app/etl/gold.py`):
- **Input**: Validated silver layer data
- **Processing**:
  - Business logic
  - Metric calculation
  - Data enrichment
  - Quality scoring
- **Output**: `activities` table
- **Purpose**: Dashboard consumption

### 3. Streamlit Dashboard

**Purpose**: User interface for data visualization and exploration

**Components**:
- **Main Dashboard** (`frontend/streamlit_app.py`): Overview and filtering
- **Activity Pages** (`frontend/pages/*.py`): Type-specific views
- **Components** (`frontend/components/`): Reusable components

**Features**:
- Real-time data refresh
- Activity type filtering
- Statistical visualizations
- Activity timeline
- Performance metrics

**Technologies**:
- Streamlit 1.29+
- Plotly for charts
- Pandas for data manipulation
- Requests for API calls

### 4. Database

**Purpose**: Persistent data storage and retrieval

**Schema**:

**bronze_activities**:
- `id`: UUID (primary key)
- `strava_id`: Integer (unique, indexed)
- `raw_data`: JSONB (Strava API response)
- `ingested_at`: Timestamp
- `processed`: Boolean
- `processed_at`: Timestamp

**silver_activities**:
- `id`: UUID (primary key)
- `strava_id`: Integer (unique, indexed)
- `cleaned_data`: JSONB
- `validation_status`: String
- `validation_errors`: JSONB
- `processed_at`: Timestamp
- `enriched`: Boolean

**activities** (Gold layer):
- `id`: UUID (primary key)
- `strava_id`: Integer (unique, indexed)
- `activity_type`: String (indexed)
- `sport_type`: String (indexed)
- Various performance metrics
- `start_date`: Timestamp (indexed)
- `data_quality_score`: Float
- Additional metadata

**Indexes**:
- Composite indexes on (activity_type, start_date)
- Composite indexes on (sport_type, start_date)
- Individual indexes on frequently queried columns

### 5. Real-time Streaming

**Purpose**: Automatic updates when new activities are posted to Strava

**Flow**:
1. User creates activity in Strava
2. Strava sends webhook event to FastAPI backend
3. Webhook handler processes event
4. Activity flows through ETL pipeline
5. Dashboard reflects new data

**Webhook Events**:
- `create`: New activity
- `update`: Activity modified
- `delete`: Activity deleted

**Handling**:
- Asynchronous processing
- Background tasks
- Error handling with retries
- Dead-letter queue for failed events

## Data Flow

### Initial Data Load

```
Strava API → Bronze ETL → Silver ETL → Gold ETL → Dashboard
```

### Real-time Update

```
Strava Webhook → Webhook Handler → Bronze → Silver → Gold → Dashboard
```

### Dashboard Query

```
Dashboard → API → Gold Layer → PostgreSQL
```

## Technology Choices

### Backend: FastAPI
- **Performance**: Async support, high performance
- **Documentation**: Automatic OpenAPI/Swagger docs
- **Validation**: Pydantic integration
- **Type Safety**: Full Python type hints

### Frontend: Streamlit
- **Rapid Development**: Low-code approach
- **Data Focus**: Built for data apps
- **Deployment**: Easy deployment options
- **Python**: Same language as backend

### Database: PostgreSQL (Supabase)
- **Reliability**: ACID compliance
- **JSONB**: Native JSON support
- **Performance**: Excellent for complex queries
- **Free Tier**: Supabase offers generous free tier
- **Features**: Built-in auth, storage, real-time

### ETL: Custom Python
- **Flexibility**: Complete control over transformation
- **Performance**: Optimized for our use case
- **Maintainability**: Python is easy to debug
- **Integration**: Seamless with FastAPI

## Security Considerations

### Authentication & Authorization
- Strava OAuth for API access
- Supabase Auth (optional for multi-user)
- Environment variables for secrets

### Data Protection
- SQL injection prevention via ORM
- Input validation via Pydantic
- HTTPS for all communications
- Webhook signature verification

### Secrets Management
- Environment variables
- GitHub Secrets for CI/CD
- No secrets in code repository

## Scalability Considerations

### Current Scale
- Designed for personal use (single user)
- Handles thousands of activities
- Optimized for reads

### Future Scaling
- Database partitioning for large datasets
- Caching layer (Redis) for frequent queries
- Horizontal scaling of API servers
- CDN for static assets
- Queue system for webhook processing

## Monitoring & Observability

### Logging
- Structured logging with loguru
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Error tracking

### Health Checks
- `/health` endpoint
- Database connectivity checks
- Strava API availability checks

### Performance Metrics
- API response times
- Database query performance
- ETL pipeline duration
- Dashboard load times

## Deployment Architecture

### Development
- Local development environment
- Local PostgreSQL
- Manual configuration

### Staging
- Continuous deployment from `develop` branch
- Staging database
- Testing environment

### Production
- Continuous deployment from `main` branch
- Production database with backups
- Monitoring and alerts
- CDN for static assets

## Disaster Recovery

### Database Backups
- Automated daily backups (Supabase)
- Point-in-time recovery
- Export functionality

### Code Recovery
- Git version control
- GitHub repository backup
- Multiple maintainers

### Data Recovery
- Bronze layer preserves raw data
- Can reprocess from bronze layer
- Audit trail for changes

## Future Enhancements

### Planned Features
- Multi-user support with authentication
- Advanced analytics and ML insights
- Social features (sharing, comparison)
- Mobile app
- Additional data sources (Garmin, Fitbit)

### Technical Improvements
- GraphQL API
- Real-time subscriptions (Supabase Realtime)
- Advanced caching strategy
- Microservices decomposition
- Event-driven architecture

---

This architecture provides a solid foundation for a production-ready Strava activity dashboard while remaining flexible for future enhancements.
