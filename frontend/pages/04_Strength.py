"""Streamlit page for Strength activities."""
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
    page_title="Strength Activities",
    page_icon="💪",
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


def main():
    """Main strength page."""
    st.title("💪 Strength Training Activities")
    st.markdown("Detailed analysis of your strength training activities")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Fetch strength activities
    with st.spinner("Loading strength activities..."):
        try:
            params = {
                "activity_type": "Strength",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "limit": 500
            }
            response = requests.get(f"{API_ACTIVITIES_URL}/", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            activities = data.get("activities", [])
        except Exception as e:
            st.error(f"Error fetching strength activities: {e}")
            return
    
    if not activities:
        st.warning("No strength activities found in the selected date range.")
        return
    
    df = pd.DataFrame(activities)
    
    # Statistics
    st.header("📊 Strength Training Statistics")
    
    total_workouts = len(df)
    total_time = df["moving_time"].sum() if "moving_time" in df.columns else 0
    avg_time = df["moving_time"].mean() if "moving_time" in df.columns else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Workouts", total_workouts)
    col2.metric("Total Time", format_seconds(total_time))
    col3.metric("Avg Duration", format_seconds(avg_time))
    
    # Progress over time
    st.header("📈 Training Progress")
    
    if "start_date" in df.columns:
        df["start_date_dt"] = pd.to_datetime(df["start_date"])
        df["date"] = df["start_date_dt"].dt.date
        df["duration_min"] = df["moving_time"] / 60 if "moving_time" in df.columns else 0
        
        # Cumulative time
        df_sorted = df.sort_values("date")
        df_sorted["cumulative_time"] = df_sorted["duration_min"].cumsum()
        
        fig = px.line(
            df_sorted,
            x="date",
            y="cumulative_time",
            title="Cumulative Training Time Over Time",
            labels={"cumulative_time": "Cumulative Time (minutes)", "date": "Date"},
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Workouts table
    st.header("📋 All Workouts")
    
    display_df = df[["name", "moving_time", "start_date_local"]].copy()
    display_df["moving_time"] = display_df["moving_time"].apply(format_seconds)
    display_df["start_date_local"] = pd.to_datetime(display_df["start_date_local"]).dt.strftime("%Y-%m-%d")
    display_df.columns = ["Name", "Duration", "Date"]
    
    st.dataframe(display_df, use_container_width=True)


if __name__ == "__main__":
    main()
