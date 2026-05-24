"""Gold layer ETL: Transform silver data to dimensional model using Supabase client."""
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
import math

from app.db.supabase_adapter import db


def calculate_business_metrics(silver_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate business metrics for dashboard reporting.
    
    Args:
        silver_data: Cleaned activity data from silver layer
        
    Returns:
        Dictionary with calculated business metrics
    """
    try:
        distance_m = silver_data.get('distance', 0)
        duration_seconds = silver_data.get('moving_time', 0)
        average_speed_mps = silver_data.get('average_speed', 0)
        max_speed_mps = silver_data.get('max_speed', 0)
        activity_type = silver_data.get('type', 'Unknown')
        
        # Calculate distance in km
        distance_km = distance_m / 1000 if distance_m > 0 else 0
        
        # Calculate duration in minutes and hours
        duration_minutes = duration_seconds / 60 if duration_seconds > 0 else 0
        duration_hours = duration_seconds / 3600 if duration_seconds > 0 else 0
        
        # Calculate average speed in km/h
        average_speed_kmh = average_speed_mps * 3.6 if average_speed_mps > 0 else 0
        max_speed_kmh = max_speed_mps * 3.6 if max_speed_mps > 0 else 0
        
        # Calculate pace (for running and swimming)
        average_pace_min_km = None
        average_pace_min_100m = None
        
        if activity_type == 'Run' and distance_km > 0:
            average_pace_min_km = duration_minutes / distance_km if distance_km > 0 else 0
        elif activity_type == 'Swim' and distance_m > 0:
            average_pace_min_100m = (duration_minutes / distance_m) * 100 if distance_m > 0 else 0
        
        return {
            'distance_km': round(distance_km, 2),
            'duration_minutes': round(duration_minutes, 2),
            'duration_hours': round(duration_hours, 2),
            'average_speed_kmh': round(average_speed_kmh, 2),
            'max_speed_kmh': round(max_speed_kmh, 2),
            'average_pace_min_km': round(average_pace_min_km, 2) if average_pace_min_km else None,
            'average_pace_min_100m': round(average_pace_min_100m, 2) if average_pace_min_100m else None,
        }
        
    except Exception as e:
        logger.error(f"Error calculating business metrics: {e}")
        return {}


def get_activity_type_id(activity_type: str) -> Optional[int]:
    """Get dimension key for activity type.
    
    Args:
        activity_type: Activity type string
        
    Returns:
        Activity type dimension ID or None
    """
    try:
        result = db.client.table('gold.dim_activity_type').select('activity_type_id').eq('type_name', activity_type).execute()
        if result.data:
            return result.data[0]['activity_type_id']
        else:
            # Create new activity type if it doesn't exist
            new_type = {
                'type_name': activity_type,
                'sport_type': activity_type,
                'category': 'Other',
                'is_distance_based': True,
                'unit_of_measure': 'km',
                'description': f'{activity_type} activities'
            }
            insert_result = db.client.table('gold.dim_activity_type').insert(new_type).execute()
            return insert_result.data[0]['activity_type_id'] if insert_result.data else None
            
    except Exception as e:
        logger.error(f"Error getting activity type ID for {activity_type}: {e}")
        return None


def get_date_id(date_str: str) -> Optional[int]:
    """Get dimension key for date.
    
    Args:
        date_str: Date string in ISO format
        
    Returns:
        Date dimension ID or None
    """
    try:
        if not date_str:
            return None
            
        # Parse the date
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        
        # Calculate date_id in YYYYMMDD format
        date_id = int(date_obj.strftime('%Y%m%d'))
        
        # Check if date dimension exists
        result = db.client.table('gold.dim_date').select('*').eq('date_id', date_id).execute()

        if not result.data:
            # Create date dimension record if it doesn't exist
            date_record = {
                'date_id': date_id,
                'date_actual': date_obj.isoformat(),
                'day_of_week': date_obj.weekday() + 1,  # Monday=1
                'day_name': date_obj.strftime('%A'),
                'day_of_month': date_obj.day,
                'day_of_year': date_obj.timetuple().tm_yday,
                'month': date_obj.month,
                'month_name': date_obj.strftime('%B'),
                'month_name_short': date_obj.strftime('%b'),
                'quarter': (date_obj.month - 1) // 3 + 1,
                'year': date_obj.year,
                'year_month': date_obj.year * 100 + date_obj.month,
                'is_weekend': date_obj.weekday() >= 5,  # Saturday=5, Sunday=6
                'season': 'Winter' if date_obj.month in [12, 1, 2] else
                         'Spring' if date_obj.month in [3, 4, 5] else
                         'Summer' if date_obj.month in [6, 7, 8] else 'Fall'
            }
            db.client.table('gold.dim_date').insert(date_record).execute()
            logger.info(f"Created date dimension for {date_obj}")
            
        return date_id
        
    except Exception as e:
        logger.error(f"Error getting date ID for {date_str}: {e}")
        return None


def transform_silver_to_gold(activity_id: int) -> Optional[Dict[str, Any]]:
    """Transform silver activity to gold dimensional model.
    
    Args:
        activity_id: Activity ID to transform
        
    Returns:
        Gold fact record or None if failed
    """
    try:
        if not db:
            logger.error("Database not available")
            return None
        
        # Get silver activity data
        silver_result = db.client.table('silver.silver_activities').select('*').eq('activity_id', activity_id).execute()

        if not silver_result.data:
            logger.warning(f"Activity {activity_id} not found in silver layer")
            return None

        silver_data = silver_result.data[0]

        # Calculate business metrics
        metrics = calculate_business_metrics(silver_data)

        # Get dimension keys
        activity_type_id = get_activity_type_id(silver_data['type'])
        date_id = get_date_id(silver_data['start_date'])

        # Build gold fact record
        gold_fact = {
            'activity_id': activity_id,
            'activity_type_id': activity_type_id,
            'date_id': date_id,

            # Raw fields for drill-down
            'activity_name': silver_data['activity_name'],
            'sport_type': silver_data['sport_type'],
            'timezone': silver_data['timezone'],

            # Performance metrics
            'distance_m': silver_data['distance'],
            'distance_km': metrics.get('distance_km', 0),
            'duration_seconds': silver_data['moving_time'],
            'duration_minutes': metrics.get('duration_minutes', 0),
            'duration_hours': metrics.get('duration_hours', 0),
            'elevation_gain_m': silver_data['total_elevation_gain'],
            'average_speed_mps': silver_data['average_speed'],
            'average_speed_kmh': metrics.get('average_speed_kmh', 0),
            'max_speed_mps': silver_data['max_speed'],
            'max_speed_kmh': metrics.get('max_speed_kmh', 0),
            'average_pace_min_km': metrics.get('average_pace_min_km'),
            'average_pace_min_100m': metrics.get('average_pace_min_100m'),

            # Social metrics
            'kudos_count': silver_data['kudos_count'],
            'comment_count': silver_data['comment_count'],
            'achievement_count': silver_data['achievement_count'],
            'photo_count': silver_data['photo_count'],
            'athlete_count': silver_data['athlete_count'],

            # Boolean flags
            'is_trainer': silver_data['trainer'],
            'is_commute': silver_data['commute'],
            'is_manual': silver_data['manual'],
            'is_private': silver_data['private'],
            'is_flagged': silver_data['flagged'],

            # Timestamps
            'start_date': silver_data['start_date'],
            'start_date_local': silver_data['start_date_local'],

            # Metadata
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        # Upsert to gold layer
        existing = db.client.table('gold.fact_activities').select('*').eq('activity_id', activity_id).execute()

        if existing.data:
            result = db.client.table('gold.fact_activities').update(gold_fact).eq('activity_id', activity_id).execute()
            logger.info(f"Updated gold fact for activity {activity_id}")
        else:
            result = db.client.table('gold.fact_activities').insert(gold_fact).execute()
            logger.info(f"Inserted gold fact for activity {activity_id}")
            
        return result
        
    except Exception as e:
        logger.error(f"Error transforming activity {activity_id} to gold: {e}")
        return None


def update_daily_summary(date_id: int) -> Optional[Dict[str, Any]]:
    """Update daily summary aggregations for a specific date.
    
    Args:
        date_id: Date dimension ID
        
    Returns:
        Updated summary record or None if failed
    """
    try:
        if not db:
            logger.error("Database not available")
            return None
        
        # Get all activities for this date
        activities_result = db.client.table('gold.fact_activities').select('*').eq('date_id', date_id).execute()

        if not activities_result.data:
            logger.info(f"No activities found for date_id {date_id}")
            return None

        activities = activities_result.data

        # Calculate daily aggregations
        total_activities = len(activities)
        total_distance_km = sum(a.get('distance_km', 0) for a in activities)
        total_duration_hours = sum(a.get('duration_hours', 0) for a in activities)
        total_elevation_gain_m = sum(a.get('elevation_gain_m', 0) for a in activities)

        # Calculate averages
        average_distance_km = total_distance_km / total_activities if total_activities > 0 else 0
        average_duration_hours = total_duration_hours / total_activities if total_activities > 0 else 0
        average_speed_kmh = sum(a.get('average_speed_kmh', 0) for a in activities) / total_activities if total_activities > 0 else 0

        # Build activity breakdown by type
        activity_breakdown = {}
        for activity in activities:
            activity_type = activity.get('sport_type', 'Unknown')
            if activity_type not in activity_breakdown:
                activity_breakdown[activity_type] = {
                    'count': 0,
                    'total_distance_km': 0,
                    'total_duration_hours': 0
                }
            activity_breakdown[activity_type]['count'] += 1
            activity_breakdown[activity_type]['total_distance_km'] += activity.get('distance_km', 0)
            activity_breakdown[activity_type]['total_duration_hours'] += activity.get('duration_hours', 0)

        # Build summary record
        summary_record = {
            'date_id': date_id,
            'total_activities': total_activities,
            'total_distance_km': round(total_distance_km, 2),
            'total_duration_hours': round(total_duration_hours, 2),
            'total_elevation_gain_m': round(total_elevation_gain_m, 2),
            'average_distance_km': round(average_distance_km, 2),
            'average_duration_hours': round(average_duration_hours, 2),
            'average_speed_kmh': round(average_speed_kmh, 2),
            'activity_breakdown': activity_breakdown,
            'updated_at': datetime.utcnow().isoformat()
        }

        # Upsert summary
        existing = db.client.table('gold.fact_daily_summary').select('*').eq('date_id', date_id).execute()

        if existing.data:
            result = db.client.table('gold.fact_daily_summary').update(summary_record).eq('date_id', date_id).execute()
            logger.info(f"Updated daily summary for date_id {date_id}")
        else:
            result = db.client.table('gold.fact_daily_summary').insert(summary_record).execute()
            logger.info(f"Inserted daily summary for date_id {date_id}")
            
        return result
        
    except Exception as e:
        logger.error(f"Error updating daily summary for date_id {date_id}: {e}")
        return None


def transform_silver_to_gold_batch(limit: int = 100) -> int:
    """Transform batch of silver activities to gold dimensional model.
    
    Args:
        limit: Maximum number of activities to transform
        
    Returns:
        Number of successfully transformed activities
    """
    try:
        if not db:
            logger.error("Database not available")
            return 0
        
        logger.info(f"Transforming up to {limit} activities from silver to gold layer")
        
        # Get activities from silver layer
        silver_result = db.client.table('silver.silver_activities').select('*').order('updated_at', desc=True).limit(limit).execute()
        
        if not silver_result.data:
            logger.info("No activities found in silver layer")
            return 0
        
        success_count = 0
        processed_dates = set()
        
        for silver_activity in silver_result.data:
            activity_id = silver_activity['activity_id']
            if transform_silver_to_gold(activity_id):
                success_count += 1
                # Track dates for summary updates
                date_id = get_date_id(silver_activity['start_date'])
                if date_id:
                    processed_dates.add(date_id)
        
        # Update daily summaries for processed dates
        for date_id in processed_dates:
            update_daily_summary(date_id)
        
        logger.info(f"Transformed {success_count}/{len(silver_result.data)} activities to gold layer")
        logger.info(f"Updated daily summaries for {len(processed_dates)} dates")
        
        return success_count
        
    except Exception as e:
        logger.error(f"Error transforming silver to gold batch: {e}")
        return 0


def run_gold_transformation(limit: int = 100, incremental: bool = True) -> Dict[str, Any]:
    """Run gold layer transformation from silver to dimensional model.
    
    Args:
        limit: Maximum number of activities to transform
        incremental: If True, only transform new activities
        
    Returns:
        Dictionary with transformation results
    """
    try:
        logger.info("Starting gold layer transformation")
        transformed_count = transform_silver_to_gold_batch(limit=limit)
        
        return {
            'transformed': transformed_count,
            'status': 'success',
            'error': None,
            'incremental': incremental
        }
        
    except Exception as e:
        logger.error(f"Gold layer transformation failed: {e}")
        return {
            'transformed': 0,
            'status': 'error',
            'error': str(e),
            'incremental': incremental
        }