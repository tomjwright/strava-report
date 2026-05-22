"""Streamlit page for Cycling activities."""
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
    page_title="Cycling Activities",
    page_icon="🚴",
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
    """Main cycling page."""
    st.title("🚴 Cycling Activities")
    st.markdown("Detailed analysis of your cycling activities")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Fetch cycling activities
    with st.spinner("Loading cycling activities..."):
        try:
            params = {
                "activity_type": "Cycling",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "limit": 500
            }
            response = requests.get(f"{API_ACTIVITIES_URL}/", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            activities = data.get("activities", [])
        except Exception as e:
            st.error(f"Error fetching cycling activities: {e}")
            return
    
    if not activities:
        st.warning("No cycling activities found in the selected date range.")
        return
    
    df = pd.DataFrame(activities)
    
    # Statistics
    st.header("📊 Cycling Statistics")
    
    total_rides = len(df)
    total_distance = df["distance"].sum() / 1000  # km
    total_time = df["moving_time"].sum()  # seconds
    avg_speed = df["average_speed"].mean() * 3.6 if "average_speed" in df.columns else 0  # km/h
    total_elevation = df["total_elevation_gain"].sum() if "total_elevation_gain" in df.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rides", total_rides)
    col2.metric("Total Distance", f"{total_distance:.1f} km")
    col3.metric("Avg Speed", f"{avg_speed:.1f} km/h")
    col4.metric("Total Elevation", f"{total_elevation:.0f} m")
    
    # Power analysis (if available)
    if "average_watts" in df.columns and df["average_watts"].notna().any():
        st.header("⚡ Power Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(
                df,
                x="average_watts",
                title="Power Distribution",
                nbins=20,
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            avg_power = df["average_watts"].mean()
            max_power = df["max_watts"].max() if "max_watts" in df.columns else 0
            st.metric("Average Power", f"{avg_power:.0f} W")
            st.metric("Max Power", f"{max_power:.0f} W")
    
    # Progress over time
    st.header("📈 Cycling Progress")
    
    if "start_date" in df.columns:
        df["start_date_dt"] = pd.to_datetime(df["start_date"])
        df["date"] = df["start_date_dt"].dt.date
        df["distance_km"] = df["distance"] / 1000
        
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
    
    # Rides table
    st.header("📋 All Rides")
    
    display_df = df[["name", "distance", "moving_time", "average_speed", "start_date_local"]].copy()
    display_df["distance"] = display_df["distance"].apply(format_distance)
    display_df["moving_time"] = display_df["moving_time"].apply(format_seconds)
    display_df["start_date_local"] = pd.to_datetime(display_df["start_date_local"]).dt.strftime("%Y-%m-%d")
    display_df.columns = ["Name", "Distance", "Time", "Speed (m/s)", "Date"]
    
    st.dataframe(display_df, use_container_width=True)


if __name__ == "__main__":
    main()
