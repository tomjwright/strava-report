"""Streamlit page for Swimming activities."""
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
    page_title="Swimming Activities",
    page_icon="🏊",
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
    """Format meters."""
    return f"{meters:.0f} m"


def main():
    """Main swimming page."""
    st.title("🏊 Swimming Activities")
    st.markdown("Detailed analysis of your swimming activities")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Fetch swimming activities
    with st.spinner("Loading swimming activities..."):
        try:
            params = {
                "activity_type": "Swimming",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "limit": 500
            }
            response = requests.get(f"{API_ACTIVITIES_URL}/", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            activities = data.get("activities", [])
        except Exception as e:
            st.error(f"Error fetching swimming activities: {e}")
            return
    
    if not activities:
        st.warning("No swimming activities found in the selected date range.")
        return
    
    df = pd.DataFrame(activities)
    
    # Statistics
    st.header("📊 Swimming Statistics")
    
    total_swims = len(df)
    total_distance = df["distance"].sum() if "distance" in df.columns else 0
    total_time = df["moving_time"].sum() if "moving_time" in df.columns else 0
    avg_speed = df["average_speed"].mean() if "average_speed" in df.columns else 0  # m/s
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Swims", total_swims)
    col2.metric("Total Distance", format_distance(total_distance))
    col3.metric("Avg Speed", f"{avg_speed:.2f} m/s")
    
    # Progress over time
    st.header("📈 Swimming Progress")
    
    if "start_date" in df.columns:
        df["start_date_dt"] = pd.to_datetime(df["start_date"])
        df["date"] = df["start_date_dt"].dt.date
        df["distance_m"] = df["distance"] if "distance" in df.columns else 0
        
        # Cumulative distance
        df_sorted = df.sort_values("date")
        df_sorted["cumulative_distance"] = df_sorted["distance_m"].cumsum()
        
        fig = px.line(
            df_sorted,
            x="date",
            y="cumulative_distance",
            title="Cumulative Distance Over Time",
            labels={"cumulative_distance": "Cumulative Distance (m)", "date": "Date"},
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Swims table
    st.header("📋 All Swims")
    
    display_df = df[["name", "distance", "moving_time", "average_speed", "start_date_local"]].copy()
    display_df["distance"] = display_df["distance"].apply(format_distance)
    display_df["moving_time"] = display_df["moving_time"].apply(format_seconds)
    display_df["start_date_local"] = pd.to_datetime(display_df["start_date_local"]).dt.strftime("%Y-%m-%d")
    display_df.columns = ["Name", "Distance", "Time", "Speed (m/s)", "Date"]
    
    st.dataframe(display_df, use_container_width=True)


if __name__ == "__main__":
    main()
