"""Clean, readable Strava dashboard with separate pages."""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config - clean and readable
st.set_page_config(
    page_title="Strava Activity Dashboard",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme configuration
st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
    }
    .main {
        background-color: #0f172a;
    }
    h1, h2, h3 {
        color: #f8fafc;
    }
    .metric-card {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        color: #f8fafc;
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8006"
API_ACTIVITIES_URL = f"{API_BASE_URL}/api/activities"
API_SUMMARY_URL = f"{API_BASE_URL}/api/summary"

@st.cache_data(ttl=60)
def get_activities():
    """Get activities from API."""
    try:
        response = requests.get(f"{API_ACTIVITIES_URL}?limit=500", timeout=10)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        st.error(f"Error loading activities: {e}")
        return []

@st.cache_data(ttl=60)
def get_summary():
    """Get summary statistics."""
    try:
        response = requests.get(API_SUMMARY_URL, timeout=10)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        st.error(f"Error loading summary: {e}")
        return {}

def filter_activities_by_type(activities, activity_type):
    """Filter activities by type."""
    return [a for a in activities if a.get('type') == activity_type]

def create_activity_type_page(activities, activity_type, color):
    """Create a page for a specific activity type."""
    st.header(f"{activity_type} Activities")
    
    filtered = filter_activities_by_type(activities, activity_type)
    
    if not filtered:
        st.warning(f"No {activity_type} activities found.")
        return
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    total_distance = sum(a.get('distance_km', 0) for a in filtered)
    total_time = sum(a.get('moving_time_minutes', 0) for a in filtered)
    total_elevation = sum(a.get('total_elevation_gain_m', 0) for a in filtered)
    avg_speed = total_distance / (total_time / 60) if total_time > 0 else 0
    
    col1.metric("Total Activities", len(filtered))
    col2.metric("Total Distance (km)", f"{total_distance:.1f}")
    col3.metric("Total Time (hours)", f"{total_time / 60:.1f}")
    col4.metric("Avg Speed (km/h)", f"{avg_speed:.1f}")
    
    # Activities table
    st.subheader("Recent Activities")
    df = pd.DataFrame(filtered)
    df['start_date_local'] = pd.to_datetime(df['start_date_local']).dt.strftime('%Y-%m-%d %H:%M')
    
    display_cols = ['name', 'distance_km', 'moving_time_minutes', 'start_date_local', 'kudos_count']
    display_df = df[display_cols].copy()
    display_df.columns = ['Activity', 'Distance (km)', 'Time (min)', 'Date', 'Kudos']
    st.dataframe(display_df, width='stretch')
    
    # Distance chart
    if len(filtered) > 1:
        st.subheader("Distance Over Time")
        df_sorted = df.sort_values('start_date_local')
        fig = px.line(df_sorted, x='start_date_local', y='distance_km',
                      title=f'{activity_type} Distance Over Time',
                      labels={'start_date_local': 'Date', 'distance_km': 'Distance (km)'},
                      color_discrete_sequence=[color])
        fig.update_layout(
            plot_bgcolor='#1e293b',
            paper_bgcolor='#1e293b',
            font=dict(color='#f8fafc'),
            xaxis=dict(color='#94a3b8'),
            yaxis=dict(color='#94a3b8')
        )
        st.plotly_chart(fig, width='stretch')

def main():
    """Main application."""
    activities = get_activities()
    summary = get_summary()
    
    # Sidebar navigation
    st.sidebar.title("Strava Dashboard")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Select Page",
        ["🏠 Home", "🏃 Running", "🚴 Cycling", "🏊 Swimming", "💪 Strength Training"]
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Health check
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=5).json()
        if health['status'] == 'healthy':
            st.sidebar.success("✅ Connected")
        else:
            st.sidebar.error("❌ Backend Issue")
    except:
        st.sidebar.error("❌ Not Connected")
    
    st.sidebar.markdown(f"**Total Activities:** {summary.get('total_activities', 0)}")
    
    # Page routing
    if page == "🏠 Home":
        st.title("🏠 Activity Dashboard")
        st.markdown("Overview of all your Strava activities")
        
        if summary:
            # Summary cards
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Activities", summary.get('total_activities', 0))
            col2.metric("Total Distance (km)", f"{summary.get('total_distance_km', 0):.1f}")
            col3.metric("Total Time (hours)", f"{summary.get('total_time_hours', 0):.1f}")
            col4.metric("Total Elevation (m)", f"{summary.get('total_elevation_m', 0):.0f}")
            
            # Activity breakdown
            if summary.get('activity_types'):
                st.subheader("Activity Breakdown")
                types_df = pd.DataFrame(list(summary['activity_types'].items()),
                                     columns=['Activity', 'Count'])
                fig = px.bar(types_df, x='Activity', y='Count',
                            title='Activities by Type',
                            color='Count',
                            color_continuous_scale='Viridis')
                fig.update_layout(
                    plot_bgcolor='#1e293b',
                    paper_bgcolor='#1e293b',
                    font=dict(color='#f8fafc'),
                    xaxis=dict(color='#94a3b8'),
                    yaxis=dict(color='#94a3b8')
                )
                st.plotly_chart(fig, width='stretch')
        
        # Recent activities
        st.subheader("Recent Activities")
        if activities:
            df = pd.DataFrame(activities)
            df['start_date_local'] = pd.to_datetime(df['start_date_local']).dt.strftime('%Y-%m-%d %H:%M')
            df_sorted = df.sort_values('start_date_local', ascending=False).head(20)
            
            display_cols = ['name', 'type', 'distance_km', 'moving_time_minutes', 'start_date_local', 'kudos_count']
            display_df = df_sorted[display_cols].copy()
            display_df.columns = ['Activity', 'Type', 'Distance (km)', 'Time (min)', 'Date', 'Kudos']
            st.dataframe(display_df, width='stretch')
        
        # Distance over time (all activities)
        if activities and len(activities) > 1:
            st.subheader("Activity Timeline")
            df = pd.DataFrame(activities)
            df['start_date_local'] = pd.to_datetime(df['start_date_local'])
            df_sorted = df.sort_values('start_date_local')
            df_sorted['date_only'] = df_sorted['start_date_local'].dt.strftime('%Y-%m-%d')
            
            # Group by date and count
            daily_counts = df_sorted.groupby('date_only').size().reset_index()
            daily_counts.columns = ['Date', 'Count']
            
            fig = px.bar(daily_counts, x='Date', y='Count',
                        title='Activities Per Day',
                        color_discrete_sequence=['#3B82F6'])
            fig.update_layout(
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font=dict(color='#f8fafc'),
                xaxis=dict(color='#94a3b8'),
                yaxis=dict(color='#94a3b8')
            )
            st.plotly_chart(fig, width='stretch')
    
    elif page == "🏃 Running":
        create_activity_type_page(activities, "Run", "#3B82F6")
    
    elif page == "🚴 Cycling":
        create_activity_type_page(activities, "Ride", "#10B981")
    
    elif page == "🏊 Swimming":
        create_activity_type_page(activities, "Swim", "#06B6D4")
    
    elif page == "💪 Strength Training":
        create_activity_type_page(activities, "WeightTraining", "#F59E0B")

if __name__ == "__main__":
    main()