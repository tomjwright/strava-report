# Data Model Documentation

This document describes the database schema and data model for the Strava Activity Dashboard.

## Overview

The database follows a medallion architecture with three layers:

1. **Bronze Layer**: Raw data ingestion (audit trail)
2. **Silver Layer**: Data cleaning and validation (quality assurance)
3. **Gold Layer**: Business-ready data (dashboard consumption)

## Entity Relationship Diagram

```
┌─────────────────────┐
│  bronze_activities  │
│  - id (UUID) PK    │
│  - strava_id (INT) │◄──────────────┐
│  - raw_data (JSONB)│               │
│  - ingested_at     │               │
│  - processed       │               │
│  - processed_at    │               │
└─────────────────────┘               │
                                     │
┌─────────────────────┐               │
│ silver_activities   │               │
│  - id (UUID) PK    │◄──────────────┤
│  - strava_id (INT) │               │
│  - cleaned_data    │               │
│  - validation_status│              │
│  - validation_errors│             │
│  - processed_at    │               │
│  - enriched        │               │
└─────────────────────┘               │
                                     │
┌─────────────────────┐               │
│    activities       │◄──────────────┘
│  - id (UUID) PK    │
│  - strava_id (INT) │
│  - activity_type   │
│  - sport_type      │
│  - name            │
│  - distance        │
│  - moving_time     │
│  - ... (metrics)   │
│  - start_date      │
│  - created_at      │
│  - updated_at      │
└─────────────────────┘
```

## Bronze Layer: `bronze_activities`

### Purpose
Store raw data from Strava API without transformation. Used for audit trail and data recovery.

### Schema

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier for the record |
| `strava_id` | INTEGER | UNIQUE, INDEXED | Strava activity ID |
| `raw_data` | JSONB | NOT NULL | Complete Strava API response |
| `ingested_at` | TIMESTAMP | NOT NULL | When the data was ingested |
| `processed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether processed by silver layer |
| `processed_at` | TIMESTAMP | NULLABLE | When processing was completed |

### Indexes
- `ix_bronze_activities_strava_id` on `strava_id` (unique)

### Example Data

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "strava_id": 123456789,
  "raw_data": {
    "id": 123456789,
    "name": "Morning Run",
    "type": "Run",
    "distance": 5000.0,
    "moving_time": 1800,
    "start_date": "2024-01-15T08:00:00Z",
    "complete_strava_response": true
  },
  "ingested_at": "2024-01-15T09:00:00Z",
  "processed": false,
  "processed_at": null
}
```

## Silver Layer: `silver_activities`

### Purpose
Store cleaned and validated data with standardization and quality checks.

### Schema

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier for the record |
| `strava_id` | INTEGER | UNIQUE, INDEXED | Strava activity ID |
| `cleaned_data` | JSONB | NOT NULL | Cleaned and standardized data |
| `validation_status` | VARCHAR(50) | NOT NULL | Status: 'valid', 'invalid', 'warning' |
| `validation_errors` | JSONB | NULLABLE | List of validation errors |
| `processed_at` | TIMESTAMP | NOT NULL | When data was processed |
| `enriched` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether enriched by gold layer |

### Indexes
- `ix_silver_activities_strava_id` on `strava_id` (unique)

### Validation Rules

#### Required Fields
- `id`: Activity ID must be present
- `type`: Activity type must be present
- `name`: Activity name must be present
- `start_date`: Start date must be present

#### Type Standardization
- `Run` → `Running`
- `Ride` → `Cycling`
- `Swim` → `Swimming`
- `WeightTraining` → `Strength`
- `Workout` → `Strength`
- etc.

#### Data Cleaning
- NULL numeric values → 0.0
- NULL boolean values → FALSE
- String whitespace trimming
- Coordinate validation

### Example Data

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "strava_id": 123456789,
  "cleaned_data": {
    "id": 123456789,
    "name": "Morning Run",
    "type": "Run",
    "standardized_type": "Running",
    "distance": 5000.0,
    "moving_time": 1800,
    "start_date": "2024-01-15T08:00:00Z",
    "distance": 5000.0,  // Was null, set to 0
    "cleaned_at": "2024-01-15T09:05:00Z"
  },
  "validation_status": "valid",
  "validation_errors": null,
  "processed_at": "2024-01-15T09:05:00Z",
  "enriched": false
}
```

## Gold Layer: `activities`

### Purpose
Store business-ready, enriched data optimized for dashboard queries.

### Schema

#### Identity Fields

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier for the record |
| `strava_id` | INTEGER | UNIQUE, INDEXED | Strava activity ID |

#### Activity Classification

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `activity_type` | VARCHAR(50) | NOT NULL, INDEXED | Standardized type (Running, Cycling, etc.) |
| `sport_type` | VARCHAR(50) | NOT NULL | Original Strava sport type |

#### Basic Information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `name` | VARCHAR(255) | NOT NULL | Activity name |
| `description` | VARCHAR(1000) | NULLABLE | Activity description |
| `distance` | FLOAT | NULLABLE | Distance in meters |
| `moving_time` | INTEGER | NULLABLE | Moving time in seconds |
| `elapsed_time` | INTEGER | NULLABLE | Elapsed time in seconds |
| `total_elevation_gain` | FLOAT | NULLABLE | Total elevation gain in meters |

#### Performance Metrics

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `average_speed` | FLOAT | NULLABLE | Average speed in m/s |
| `max_speed` | FLOAT | NULLABLE | Maximum speed in m/s |
| `average_heartrate` | FLOAT | NULLABLE | Average heart rate in bpm |
| `max_heartrate` | INTEGER | NULLABLE | Maximum heart rate in bpm |
| `average_cadence` | FLOAT | NULLABLE | Average cadence |
| `average_watts` | FLOAT | NULLABLE | Average power in watts |
| `max_watts` | INTEGER | NULLABLE | Maximum power in watts |
| `weighted_average_watts` | FLOAT | NULLABLE | Weighted average power in watts |
| `kilojoules` | FLOAT | NULLABLE | Energy expenditure in kJ |

#### Additional Metrics

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `average_temp` | FLOAT | NULLABLE | Average temperature |
| `max_grade` | FLOAT | NULLABLE | Maximum grade percentage |
| `average_grade` | FLOAT | NULLABLE | Average grade percentage |
| `total_weight` | FLOAT | NULLABLE | Total weight lifted (kg) - Strength |
| `rep_count` | INTEGER | NULLABLE | Total repetitions - Strength |

#### Location

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `city` | VARCHAR(100) | NULLABLE | City |
| `state` | VARCHAR(100) | NULLABLE | State/Province |
| `country` | VARCHAR(100) | NULLABLE | Country |
| `start_latlng` | JSON | NULLABLE | Start coordinates [lat, lng] |
| `end_latlng` | JSON | NULLABLE | End coordinates [lat, lng] |

#### Timing

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `start_date` | TIMESTAMP | NOT NULL, INDEXED | Activity start date (UTC) |
| `start_date_local` | TIMESTAMP | NOT NULL, INDEXED | Activity start date (local time) |
| `timezone` | VARCHAR(50) | NULLABLE | Timezone |

#### Social Metrics

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `achievement_count` | INTEGER | NULLABLE | Number of achievements |
| `kudos_count` | INTEGER | NULLABLE | Number of kudos |
| `comment_count` | INTEGER | NULLABLE | Number of comments |
| `athlete_count` | INTEGER | NULLABLE | Number of athletes |
| `photo_count` | INTEGER | NULLABLE | Number of photos |

#### Activity Flags

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `trainer` | BOOLEAN | NOT NULL, DEFAULT FALSE | Trainer activity |
| `commute` | BOOLEAN | NOT NULL, DEFAULT FALSE | Commute activity |
| `manual` | BOOLEAN | NOT NULL, DEFAULT FALSE | Manually entered |
| `private` | BOOLEAN | NOT NULL, DEFAULT FALSE | Private activity |
| `flagged` | BOOLEAN | NOT NULL, DEFAULT FALSE | Flagged activity |

#### Device Info

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `device_name` | VARCHAR(100) | NULLABLE | Device name |

#### Metadata

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `created_at` | TIMESTAMP | NOT NULL | Record creation time |
| `updated_at` | TIMESTAMP | NOT NULL | Record update time |
| `processed_at` | TIMESTAMP | NULLABLE | ETL processing timestamp |
| `data_quality_score` | FLOAT | NULLABLE | Quality score (0-1) |
| `raw_data` | JSONB | NULLABLE | Full cleaned data |

### Indexes

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| `ix_activities_strava_id` | `strava_id` | UNIQUE | Activity lookup by Strava ID |
| `ix_activities_activity_type` | `activity_type` | SINGLE | Filter by activity type |
| `ix_activities_start_date` | `start_date` | SINGLE | Chronological queries |
| `idx_activities_type_date` | `activity_type`, `start_date` | COMPOSITE | Type + date filters |
| `idx_activities_sport_date` | `sport_type`, `start_date` | COMPOSITE | Sport + date filters |
| `idx_activities_start_date_local` | `start_date_local` | SINGLE | Local time queries |

### Example Data

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "strava_id": 123456789,
  "activity_type": "Running",
  "sport_type": "Run",
  "name": "Morning Run",
  "distance": 5000.0,
  "moving_time": 1800,
  "average_speed": 2.78,
  "average_heartrate": 145.0,
  "start_date": "2024-01-15T08:00:00Z",
  "start_date_local": "2024-01-15T09:00:00Z",
  "city": "Berlin",
  "country": "Germany",
  "kudos_count": 5,
  "data_quality_score": 0.95,
  "created_at": "2024-01-15T09:10:00Z",
  "updated_at": "2024-01-15T09:10:00Z",
  "processed_at": "2024-01-15T09:10:00Z"
}
```

## Activity Type Mapping

### Standardized Types

| Strava Type | Standardized Type | Category |
|-------------|-------------------|----------|
| Run | Running | Cardio |
| TrailRun | Running | Cardio |
| VirtualRun | Running | Cardio |
| Ride | Cycling | Cardio |
| MountainBikeRide | Cycling | Cardio |
| GravelRide | Cycling | Cardio |
| EBikeRide | Cycling | Cardio |
| VirtualRide | Cycling | Cardio |
| Swim | Swimming | Cardio |
| WeightTraining | Strength | Strength |
| Workout | Strength | Strength |
| Crossfit | Strength | Strength |
| Yoga | Strength | Strength |
| Walk | Walking | Cardio |
| Hike | Hiking | Outdoor |
| AlpineSki | Skiing | Winter |
| BackcountrySki | Skiing | Winter |

## Data Quality Scoring

### Scoring Logic

The `data_quality_score` (0-1) is calculated based on field completeness:

#### Critical Fields (0.1 penalty each if missing)
- `distance`
- `moving_time`
- `start_date`

#### Important Fields (0.05 penalty each if missing)
- `total_elevation_gain`
- `average_speed`
- `average_heartrate`
- `average_cadence`
- `average_watts`

#### Location Data (0.05 penalty if missing all)
- `city`, `state`, or `country`

### Score Ranges

- **0.9 - 1.0**: Excellent data quality
- **0.7 - 0.9**: Good data quality
- **0.5 - 0.7**: Acceptable data quality
- **< 0.5**: Poor data quality

## Query Patterns

### Common Queries

#### Get Recent Activities by Type
```sql
SELECT * FROM activities
WHERE activity_type = 'Running'
AND start_date >= NOW() - INTERVAL '30 days'
ORDER BY start_date DESC
LIMIT 50;
```

#### Activity Statistics
```sql
SELECT
    activity_type,
    COUNT(*) as count,
    SUM(distance) as total_distance,
    AVG(moving_time) as avg_time
FROM activities
WHERE start_date >= NOW() - INTERVAL '30 days'
GROUP BY activity_type;
```

#### Performance Analysis
```sql
SELECT
    DATE(start_date_local) as date,
    AVG(average_speed) as avg_speed,
    AVG(average_heartrate) as avg_hr
FROM activities
WHERE activity_type = 'Running'
AND start_date >= NOW() - INTERVAL '90 days'
GROUP BY DATE(start_date_local)
ORDER BY date DESC;
```

## Migration Strategy

### Creating New Migrations

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
```

### Applying Migrations

```bash
cd backend
alembic upgrade head
```

### Rolling Back Migrations

```bash
cd backend
alembic downgrade -1
```

## Data Retention Policy

### Bronze Layer
- **Retention**: 30 days after processing
- **Purpose**: Audit trail and recovery
- **Cleanup**: Automated via scheduled job

### Silver Layer
- **Retention**: 90 days after enrichment
- **Purpose**: Quality audit and reprocessing
- **Cleanup**: Automated via scheduled job

### Gold Layer
- **Retention**: Indefinite
- **Purpose**: Dashboard and analytics
- **Cleanup**: Manual/archival only

## Performance Considerations

### Optimization Strategies

1. **Index Usage**
   - Use composite indexes for common filter combinations
   - Monitor index usage and remove unused indexes
   - Consider partial indexes for specific query patterns

2. **Query Optimization**
   - Use `EXPLAIN ANALYZE` to understand query plans
   - Avoid `SELECT *` in production
   - Use pagination for large result sets

3. **Connection Pooling**
   - Configure appropriate pool size
   - Monitor connection pool usage
   - Use read replicas for read-heavy workloads

### Monitoring

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

This data model provides a robust foundation for the Strava Activity Dashboard while maintaining data quality and performance.
