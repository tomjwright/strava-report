"""Streamlit page for Running activities."""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_ACTIVITIES_URL = f"{API_BASE_URL}/api/activities"

st.set_page_config(
    page_title="Running Activities",
    page_icon="🏃",
    layout="wide",
)


def format_seconds(seconds: float) -> str:
    """Format seconds to human-readable time."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def format_distance(meters: float) -> str:
    """Format meters to kilometers."""
    km = meters / 1000
    return f"{km:.2f} km"


def main():
    """Main running page."""
    st.title("🏃 Running Activities")
    st.markdown("Detailed analysis of your running activities")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Fetch running activities
    with st.spinner("Loading running activities..."):
        try:
            params = {
                "activity_type": "Running",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "limit": 500
            }
            response = requests.get(f"{API_ACTIVITIES_URL}/", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            activities = data.get("activities", [])
        except Exception as e:
            st.error(f"Error fetching running activities: {e}")
            return
    
    if not activities:
        st.warning("No running activities found in the selected date range.")
        return
    
    df = pd.DataFrame(activities)
    
    # Statistics
    st.header("📊 Running Statistics")
    
    total_runs = len(df)
    total_distance = df["distance"].sum() / 1000  # km
    total_time = df["moving_time"].sum()  # seconds
    avg_pace = (total_time / 60) / total_distance if total_distance > 0 else 0  # min/km
    avg_speed = df["average_speed"].mean() if "average_speed" in df.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Runs", total_runs)
    col2.metric("Total Distance", f"{total_distance:.1f} km")
    col3.metric("Total Time", format_seconds(total_time))
    col4.metric("Avg Pace", f"{avg_pace:.2f} min/km")
    
    # Progress over time
    st.header("📈 Running Progress")
    
    if "start_date" in df.columns:
        df["start_date_dt"] = pd.to_datetime(df["start_date"])
        df["date"] = df["start_date_dt"].dt.date
        df["distance_km"] = df["distance"] / 1000
        df["pace_min_km"] = (df["moving_time"] / 60) / df["distance_km"]
        
        # Cumulative distance
        df_sorted = df.sort_values("date")
        df_sorted["cumulative_distance"] = df_sorted["distance_km"].cumsum()
        
        fig = px.line(
            df_sorted,
            x="date",
            y="cumulative_distance",
            title="Cumulative Distance Over Time",
            labels={"cumulative_distance": "Cumulative Distance (km)", "date": "Date"},
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Pace analysis
    if "pace_min_km" in df.columns:
        st.header("⏱️ Pace Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(
                df,
                x="pace_min_km",
                title="Pace Distribution",
                nbins=20,
                labels={"pace_min_km": "Pace (min/km)"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(
                df,
                x="distance_km",
                y="pace_min_km",
                title="Distance vs Pace",
                labels={"distance_km": "Distance (km)", "pace_min_km": "Pace (min/km)"}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Runs table
    st.header("📋 All Runs")
    
    display_df = df[["name", "distance", "moving_time", "average_speed", "start_date_local"]].copy()
    display_df["distance"] = display_df["distance"].apply(format_distance)
    display_df["moving_time"] = display_df["moving_time"].apply(format_seconds)
    display_df["start_date_local"] = pd.to_datetime(display_df["start_date_local"]).dt.strftime("%Y-%m-%d")
    display_df.columns = ["Name", "Distance", "Time", "Speed (m/s)", "Date"]
    
    st.dataframe(display_df, use_container_width=True)


if __name__ == "__main__":
    main()
