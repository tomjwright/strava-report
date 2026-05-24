"""Simple Strava data loader - fetch and insert directly into database."""
import os
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import requests

load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Strava API configuration
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

def get_strava_access_token():
    """Get fresh Strava access token."""
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'refresh_token': STRAVA_REFRESH_TOKEN,
            'grant_type': 'refresh_token'
        }
    )
    return response.json()['access_token']

def get_strava_activities(access_token):
    """Fetch ALL activities from Strava API from 2026 onwards."""
    activities = []
    page = 1
    per_page = 200  # Max per page

    # 2026-01-01 timestamp (correct)
    after_timestamp = 1767225600  # January 1, 2026 00:00:00 UTC

    print(f"Fetching ALL activities from 2026 onwards...")

    while True:
        response = requests.get(
            f'https://www.strava.com/api/v3/athlete/activities',
            headers={'Authorization': f'Bearer {access_token}'},
            params={
                'page': page,
                'per_page': per_page,
                'after': after_timestamp  # Get activities from 2026 onwards
            }
        )

        if response.status_code != 200:
            print(f"Error fetching activities: {response.status_code}")
            break

        new_activities = response.json()
        if not new_activities:
            print(f"No more activities found. Total fetched: {len(activities)}")
            break

        activities.extend(new_activities)
        print(f"Fetched {len(new_activities)} activities (page {page}, total: {len(activities)})")
        page += 1

        # Stop if we got fewer than max per page (reached the end)
        if len(new_activities) < per_page:
            print(f"Reached end of activities. Total: {len(activities)}")
            break

    return activities

def transform_activity(activity):
    """Transform Strava activity to simple format."""
    return {
        'id': activity['id'],
        'name': activity.get('name', 'Untitled'),
        'type': activity.get('type', 'Unknown'),
        'sport_type': activity.get('sport_type', 'Unknown'),
        'distance_km': activity.get('distance', 0) / 1000 if activity.get('distance') else 0,
        'moving_time_minutes': activity.get('moving_time', 0) / 60 if activity.get('moving_time') else 0,
        'elapsed_time_minutes': activity.get('elapsed_time', 0) / 60 if activity.get('elapsed_time') else 0,
        'total_elevation_gain_m': activity.get('total_elevation_gain', 0),
        'average_speed_kmh': (activity.get('average_speed', 0) * 3.6) if activity.get('average_speed') else 0,
        'max_speed_kmh': (activity.get('max_speed', 0) * 3.6) if activity.get('max_speed') else 0,
        'start_date': activity.get('start_date'),
        'start_date_local': activity.get('start_date_local'),
        'timezone': activity.get('timezone', 'UTC'),
        'achievement_count': activity.get('achievement_count', 0),
        'kudos_count': activity.get('kudos_count', 0),
        'comment_count': activity.get('comment_count', 0),
        'athlete_count': activity.get('athlete_count', 0),
        'photo_count': activity.get('photo_count', 0),
        'trainer': activity.get('trainer', False),
        'commute': activity.get('commute', False),
        'manual': activity.get('manual', False),
        'private': activity.get('private', False),
        'flagged': activity.get('flagged', False),
        'updated_at': datetime.utcnow().isoformat()
    }

def clear_database():
    """Clear all existing data from database."""
    print("Clearing existing data from database...")
    try:
        # Delete all existing activities
        response = supabase.table('strava_activities').delete().neq('id', 0).execute()
        print(f"Cleared existing data")
    except Exception as e:
        print(f"Error clearing database: {e}")

def load_activities_to_database():
    """Load activities from Strava to database."""
    print("Getting Strava access token...")
    access_token = get_strava_access_token()

    # Clear old data first to ensure we only have 2026 data
    clear_database()

    print("Fetching ALL activities from Strava from 2026 onwards...")
    activities = get_strava_activities(access_token)
    print(f"Fetched {len(activities)} total activities")

    print("Loading activities into database...")
    success_count = 0

    for activity in activities:
        try:
            transformed = transform_activity(activity)

            # Upsert to database
            response = supabase.table('strava_activities').upsert(
                transformed,
                on_conflict='id'
            ).execute()

            success_count += 1
            if success_count % 50 == 0:
                print(f"Loaded {success_count}/{len(activities)} activities...")

        except Exception as e:
            print(f"Error loading activity {activity.get('id')}: {e}")

    print(f"Successfully loaded {success_count}/{len(activities)} activities")
    return success_count

if __name__ == '__main__':
    load_activities_to_database()