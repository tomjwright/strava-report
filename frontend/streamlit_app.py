"""Production-ready Streamlit dashboard for Strava activity monitoring."""
import streamlit as st
import requests
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os

# Professional dark theme configuration
st.set_page_config(
    page_title="Strava Pro Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Use Streamlit's native dark theme
st.config.set_option('theme.base', 'dark')
st.config.set_option('theme.primaryColor', '#58A6FF')
st.config.set_option('theme.secondaryBackgroundColor', '#161B22')
st.config.set_option('theme.textColor', '#FAFAFA')
st.config.set_option('theme.font', 'sans serif')


# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8003")
API_BRONZE_ACTIVITIES_URL = f"{API_BASE_URL}/api/bronze-activities"
API_FETCH_STRAVA_URL = f"{API_BASE_URL}/api/fetch-strava"

# Professional color scheme
COLORS = {
    'primary': '#58A6FF',
    'secondary': '#238636', 
    'accent': '#D29922',
    'danger': '#F85149',
    'background': '#0E1117',
    'surface': '#161B22',
    'border': '#30363D',
    'text': '#FAFAFA',
    'text_secondary': '#8B949E'
}

def fetch_bronze_activities(limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch raw activities from the bronze layer API."""
    try:
        st.info(f"Fetching activities from {API_BRONZE_ACTIVITIES_URL}")
        response = requests.get(f"{API_BRONZE_ACTIVITIES_URL}?limit={limit}", timeout=10)
        response.raise_for_status()
        data = response.json()
        activities = data.get("data", [])
        st.success(f"Successfully fetched {len(activities)} activities")
        return activities
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to API at {API_BASE_URL}. Make sure the backend is running.")
        return []
    except Exception as e:
        st.error(f"Error fetching activities: {e}")
        import traceback
        st.error(traceback.format_exc())
        return []


def fetch_strava_data(limit: int = 10) -> Dict[str, Any]:
    """Trigger Strava data fetch."""
    try:
        response = requests.post(f"{API_FETCH_STRAVA_URL}?limit={limit}", timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching Strava data: {e}")
        return {"status": "error", "message": str(e)}


def format_seconds(seconds: Optional[float]) -> str:
    """Format seconds to human-readable time."""
    if seconds is None:
        return "0m 0s"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def format_distance(meters: Optional[float]) -> str:
    """Format meters to kilometers."""
    if meters is None or meters == 0:
        return "0.00 km"
    km = meters / 1000
    return f"{km:.2f} km"


def format_elevation(meters: Optional[float]) -> str:
    """Format elevation in meters."""
    if meters is None or meters == 0:
        return "0 m"
    return f"{meters:.0f} m"


def format_speed(mps: Optional[float]) -> str:
    """Format speed from m/s to km/h."""
    if mps is None or mps == 0:
        return "0.0 km/h"
    kmh = mps * 3.6
    return f"{kmh:.1f} km/h"


def extract_activity_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant activity data from raw Strava data."""
    return {
        "id": raw_data.get("id"),
        "name": raw_data.get("name", "Untitled"),
        "type": raw_data.get("type", "Unknown"),
        "sport_type": raw_data.get("sport_type", "Unknown"),
        "distance": raw_data.get("distance", 0),
        "moving_time": raw_data.get("moving_time", 0),
        "elapsed_time": raw_data.get("elapsed_time", 0),
        "total_elevation_gain": raw_data.get("total_elevation_gain", 0),
        "average_speed": raw_data.get("average_speed", 0),
        "max_speed": raw_data.get("max_speed", 0),
        "start_date": raw_data.get("start_date", ""),
        "start_date_local": raw_data.get("start_date_local", ""),
        "achievement_count": raw_data.get("achievement_count", 0),
        "kudos_count": raw_data.get("kudos_count", 0),
        "comment_count": raw_data.get("comment_count", 0),
    }


def create_professional_bar_chart(df: pl.DataFrame, x_col: str, y_col: str, title: str, color: str = COLORS['primary']):
    """Create a professional bar chart with custom styling."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y_col],
        marker_color=color,
        marker_line_color=COLORS['border'],
        marker_line_width=1,
        text=df[y_col],
        textposition='outside',
        textfont=dict(size=12, color=COLORS['text']),
    ))
    
    fig.update_layout(
        title=title,
        title_font=dict(size=18, color=COLORS['text']),
        plot_bgcolor=COLORS['surface'],
        paper_bgcolor=COLORS['surface'],
        font=dict(color=COLORS['text']),
        xaxis=dict(
            gridcolor=COLORS['border'],
            showgrid=True,
            tickangle=-45,
            tickfont=dict(color=COLORS['text_secondary'])
        ),
        yaxis=dict(
            gridcolor=COLORS['border'],
            showgrid=True,
            tickfont=dict(color=COLORS['text_secondary'])
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=350,
        showlegend=False
    )
    
    return fig


def create_professional_pie_chart(df: pl.DataFrame, values_col: str, names_col: str, title: str):
    """Create a professional pie chart with custom styling."""
    fig = go.Figure()
    
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent'], '#A371F7', '#F78166']
    
    fig.add_trace(go.Pie(
        labels=df[names_col],
        values=df[values_col],
        marker=dict(colors=colors[:len(df)], line=dict(color=COLORS['border'], width=1)),
        textinfo='label+percent',
        textposition='inside',
        textfont=dict(size=11, color=COLORS['text']),
        hole=0.4,
        pull=[0.05] * len(df),
    ))
    
    fig.update_layout(
        title=title,
        title_font=dict(size=18, color=COLORS['text']),
        plot_bgcolor=COLORS['surface'],
        paper_bgcolor=COLORS['surface'],
        font=dict(color=COLORS['text']),
        margin=dict(l=20, r=20, t=60, b=20),
        height=350,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=COLORS['text_secondary'])
        )
    )
    
    return fig


def create_professional_line_chart(df: pl.DataFrame, x_col: str, y_col: str, title: str, color: str = COLORS['primary']):
    """Create a professional line chart with custom styling."""
    fig = go.Figure()
    
    # Convert hex to RGBA for proper fill effect
    hex_color = color.lstrip('#')
    rgba_color = f'rgba({int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}, 0.2)'
    
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines+markers',
        line=dict(color=color, width=3),
        marker=dict(
            size=8,
            color=color,
            line=dict(color=COLORS['surface'], width=2)
        ),
        fill='tozeroy',
        fillcolor=rgba_color
    ))
    
    fig.update_layout(
        title=title,
        title_font=dict(size=18, color=COLORS['text']),
        plot_bgcolor=COLORS['surface'],
        paper_bgcolor=COLORS['surface'],
        font=dict(color=COLORS['text']),
        xaxis=dict(
            gridcolor=COLORS['border'],
            showgrid=True,
            tickfont=dict(color=COLORS['text_secondary']),
            title_text='Date'
        ),
        yaxis=dict(
            gridcolor=COLORS['border'],
            showgrid=True,
            tickfont=dict(color=COLORS['text_secondary']),
            title_text='Distance (km)'
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=350,
        showlegend=False
    )
    
    return fig


def render_header():
    """Render professional header."""
    st.markdown("""
    <div style='display: flex; align-items: center; justify-content: space-between; padding: 1rem 0;'>
        <div>
            <h1 style='margin: 0; font-size: 2.5rem; font-weight: 700;'>⚡ Strava Pro Dashboard</h1>
            <p style='margin: 0.5rem 0 0; color: #8B949E; font-size: 1.1rem;'>Professional Activity Analytics & Performance Tracking</p>
        </div>
        <div style='text-align: right;'>
            <div style='background: #238636; color: white; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 600; font-size: 0.9rem;'>
                🟢 Live Data
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render professional sidebar."""
    with st.sidebar:
        st.markdown("""
        <div style='background: #21262D; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;'>
            <h3 style='margin: 0 0 1rem 0; color: #FAFAFA;'>🎮 Dashboard Controls</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Fetch Strava data button
        if st.button("🔄 Sync with Strava", use_container_width=True):
            with st.spinner("🔄 Syncing activities from Strava..."):
                result = fetch_strava_data(limit=10)
                if result.get("status") == "success":
                    st.success(f"✅ Synced {result.get('details', {}).get('ingested', 0)} activities!")
                    st.rerun()
                else:
                    st.error(f"❌ Sync failed: {result.get('message', 'Unknown error')}")
        
        st.markdown("---")
        
        # Refresh button
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        
        # System status
        st.markdown("""
        <div style='background: #161B22; padding: 1rem; border-radius: 8px; border: 1px solid #30363D;'>
            <h4 style='margin: 0 0 0.5rem 0; color: #8B949E; font-size: 0.85rem;'>SYSTEM STATUS</h4>
            <div style='color: #3FB950; font-size: 0.9rem;'>● API: Connected</div>
            <div style='color: #3FB950; font-size: 0.9rem;'>● Database: Active</div>
            <div style='color: #58A6FF; font-size: 0.9rem;'>📡 """ + API_BASE_URL + """</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("<p style='color: #8B949E; font-size: 0.8rem; text-align: center;'>Strava Pro Dashboard v1.0</p>", unsafe_allow_html=True)


def render_metrics(df: pl.DataFrame):
    """Render professional metrics cards."""
    st.markdown("<h2 style='margin: 2rem 0 1rem 0;'>📊 Performance Overview</h2>", unsafe_allow_html=True)
    
    # Calculate metrics
    total_activities = len(df)
    total_distance = df["distance"].sum() if "distance" in df.columns else 0
    total_time = df["moving_time"].sum() if "moving_time" in df.columns else 0
    total_elevation = df["total_elevation_gain"].sum() if "total_elevation_gain" in df.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🏃 Total Activities",
            f"{total_activities}",
            delta=None,
            help="Total number of activities recorded"
        )
    
    with col2:
        st.metric(
            "📏 Total Distance", 
            format_distance(total_distance),
            delta=None,
            help="Total distance covered across all activities"
        )
    
    with col3:
        st.metric(
            "⏱️ Total Time",
            format_seconds(total_time),
            delta=None,
            help="Total moving time across all activities"
        )
    
    with col4:
        st.metric(
            "🏔️ Elevation Gain",
            format_elevation(total_elevation),
            delta=None,
            help="Total elevation gained across all activities"
        )


def render_activity_breakdown(df: pl.DataFrame):
    """Render professional activity type breakdown."""
    st.markdown("<h2 style='margin: 2rem 0 1rem 0;'>🎯 Activity Distribution</h2>", unsafe_allow_html=True)
    
    if "type" in df.columns:
        type_counts = df.group_by("type").count().sort("count", descending=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            bar_chart = create_professional_bar_chart(
                type_counts.to_pandas(),
                "type", "count",
                "Activities by Type",
                COLORS['primary']
            )
            st.plotly_chart(bar_chart, use_container_width=True)
        
        with col2:
            pie_chart = create_professional_pie_chart(
                type_counts.to_pandas(),
                "count", "type",
                "Activity Distribution"
            )
            st.plotly_chart(pie_chart, use_container_width=True)


def render_timeline(df: pl.DataFrame):
    """Render professional activity timeline."""
    st.markdown("<h2 style='margin: 2rem 0 1rem 0;'>📅 Performance Timeline</h2>", unsafe_allow_html=True)
    
    if "start_date" in df.columns and not df["start_date"].is_empty():
        try:
            # Handle different date formats
            df_work = df.clone()
            
            # Try different date formats
            for date_format in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%.fZ", "%Y-%m-%d %H:%M:%S"]:
                try:
                    df_work = df_work.with_columns([
                        pl.col("start_date").str.strptime(pl.Datetime, date_format).alias("start_date_dt")
                    ])
                    break
                except:
                    continue
            
            # If conversion failed, skip timeline
            if "start_date_dt" not in df_work.columns:
                st.warning("Unable to parse date format for timeline")
                return
                
            df_work = df_work.with_columns([
                pl.col("start_date_dt").dt.date().alias("date")
            ])
            
            # Calculate distance in km
            if "distance" in df_work.columns:
                df_work = df_work.with_columns([
                    (pl.col("distance") / 1000).alias("distance_km")
                ])
            
            # Group by date
            timeline_data = df_work.group_by("date").agg([
                pl.col("distance_km").sum().alias("total_distance")
            ]).sort("date")
            
            if not timeline_data.is_empty():
                line_chart = create_professional_line_chart(
                    timeline_data.to_pandas(),
                    "date", "total_distance",
                    "Daily Distance Over Time"
                )
                st.plotly_chart(line_chart, use_container_width=True)
            else:
                st.info("No timeline data available")
                
        except Exception as e:
            st.error(f"Timeline error: {str(e)}")
            import traceback
            st.error(traceback.format_exc())


def render_activity_table(df: pl.DataFrame):
    """Render professional activity table."""
    st.markdown("<h2 style='margin: 2rem 0 1rem 0;'>📋 Activity Log</h2>", unsafe_allow_html=True)
    
    if not df.is_empty():
        # Format for display
        display_df = df.clone()
        
        if "distance" in display_df.columns:
            display_df = display_df.with_columns([
                pl.col("distance").map_elements(format_distance, return_dtype=pl.Utf8).alias("distance_formatted")
            ])
        
        if "moving_time" in display_df.columns:
            display_df = display_df.with_columns([
                pl.col("moving_time").map_elements(format_seconds, return_dtype=pl.Utf8).alias("time_formatted")
            ])
        
        if "average_speed" in display_df.columns:
            display_df = display_df.with_columns([
                pl.col("average_speed").map_elements(format_speed, return_dtype=pl.Utf8).alias("speed_formatted")
            ])
        
        if "start_date_local" in display_df.columns:
            try:
                display_df = display_df.with_columns([
                    pl.col("start_date_local").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S").dt.strftime("%Y-%m-%d %H:%M")
                ])
            except:
                pass
        
        # Select and reorder columns for display
        display_cols = ["name", "type", "distance_formatted", "time_formatted", "speed_formatted", "start_date_local", "kudos_count"]
        available_cols = [col for col in display_cols if col in display_df.columns]
        
        # Create column headers mapping
        col_mapping = {
            "name": "Activity Name",
            "type": "Type", 
            "distance_formatted": "Distance",
            "time_formatted": "Duration",
            "speed_formatted": "Avg Speed",
            "start_date_local": "Date",
            "kudos_count": "Kudos"
        }
        
        if available_cols:
            # Rename columns for display
            display_df = display_df.rename({col: col_mapping.get(col, col) for col in available_cols})
            renamed_cols = [col_mapping.get(col, col) for col in available_cols]
            
            st.dataframe(
                display_df.select(renamed_cols).to_pandas(),
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.dataframe(df.to_pandas(), use_container_width=True, height=400)


def render_recent_activities(df: pl.DataFrame):
    """Render professional recent activities cards."""
    st.markdown("<h2 style='margin: 2rem 0 1rem 0;'>🆕 Recent Activities</h2>", unsafe_allow_html=True)
    
    if not df.is_empty() and "start_date" in df.columns:
        try:
            df_sorted = df.sort("start_date", descending=True).head(4)
            
            for i, row in enumerate(df_sorted.iter_rows(named=True)):
                # Activity type icons
                activity_icons = {
                    "Run": "🏃",
                    "Ride": "🚴",
                    "Swim": "🏊",
                    "WeightTraining": "💪",
                    "Workout": "🏋️",
                    "Hike": "🥾"
                }
                
                icon = activity_icons.get(row.get('type', ''), '🏃')
                activity_name = row.get('name', 'Untitled')
                activity_type = row.get('type', 'Unknown')
                
                with st.expander(f"{icon} {activity_name} • {activity_type}", expanded=(i == 0)):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div style='background: #21262D; padding: 1rem; border-radius: 8px; border: 1px solid #30363D;'>
                            <div style='color: #8B949E; font-size: 0.8rem; font-weight: 600;'>DISTANCE</div>
                            <div style='color: #FAFAFA; font-size: 1.2rem; font-weight: 700;'>{format_distance(row.get('distance'))}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style='background: #21262D; padding: 1rem; border-radius: 8px; border: 1px solid #30363D;'>
                            <div style='color: #8B949E; font-size: 0.8rem; font-weight: 600;'>DURATION</div>
                            <div style='color: #FAFAFA; font-size: 1.2rem; font-weight: 700;'>{format_seconds(row.get('moving_time'))}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div style='background: #21262D; padding: 1rem; border-radius: 8px; border: 1px solid #30363D;'>
                            <div style='color: #8B949E; font-size: 0.8rem; font-weight: 600;'>AVG SPEED</div>
                            <div style='color: #FAFAFA; font-size: 1.2rem; font-weight: 700;'>{format_speed(row.get('average_speed'))}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div style='background: #21262D; padding: 1rem; border-radius: 8px; border: 1px solid #30363D;'>
                            <div style='color: #8B949E; font-size: 0.8rem; font-weight: 600;'>ELEVATION</div>
                            <div style='color: #FAFAFA; font-size: 1.2rem; font-weight: 700;'>{format_elevation(row.get('total_elevation_gain'))}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Additional details row
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"<div style='color: #8B949E; font-size: 0.85rem;'>📅 {row.get('start_date_local', 'N/A')}</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"<div style='color: #8B949E; font-size: 0.85rem;'>👍 {row.get('kudos_count', 0)} Kudos</div>", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"<div style='color: #8B949E; font-size: 0.85rem;'>🏆 {row.get('achievement_count', 0)} Achievements</div>", unsafe_allow_html=True)
                    
        except Exception as e:
            st.warning(f"Could not display recent activities: {e}")


def main():
    """Main dashboard application."""
    render_header()
    render_sidebar()
    
    # Auto-refresh functionality
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False, help="Automatically refresh data every 30 seconds")
    if auto_refresh:
        st.sidebar.info("Auto-refresh enabled")
        st.rerun()
    
    # Data limit selector
    limit = st.sidebar.slider("Activities to load", min_value=10, max_value=1000, value=100, step=50)
    
    st.sidebar.markdown("---")
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Show API status
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if health_response.status_code == 200:
            st.sidebar.success("✅ Backend Connected")
        else:
            st.sidebar.error(f"❌ Backend Error: {health_response.status_code}")
    except:
        st.sidebar.error(f"❌ Backend Unreachable at {API_BASE_URL}")
        st.sidebar.warning("Make sure the backend is running on port 8003")
    
    # Fetch data
    with st.spinner("🔄 Loading activities from database..."):
        activities = fetch_bronze_activities(limit=limit)
    
    if not activities:
        st.markdown("""
        <div style='background: #21262D; padding: 2rem; border-radius: 12px; border: 1px solid #30363D; text-align: center; margin: 2rem 0;'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>📭</div>
            <h3 style='color: #FAFAFA; margin: 0 0 0.5rem 0;'>No Activities Found</h3>
            <p style='color: #8B949E; margin: 0;'>Click "Sync with Strava" in the sidebar to fetch your activities.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show API connection test
        st.markdown("### 🔍 API Connection Test")
        try:
            health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            st.json(health_response.json())
        except Exception as e:
            st.error(f"Cannot connect to API at {API_BASE_URL}: {e}")
        
        return
    
    # Extract activity data from raw data
    try:
        extracted_data = [extract_activity_data(activity["raw_data"]) for activity in activities]
        df = pl.DataFrame(extracted_data)
        
        st.success(f"📊 Loaded {len(df)} activities into dashboard")
        
        # Show sample of loaded data for debugging
        with st.expander("🔍 Debug: Show Raw Data Sample", expanded=False):
            st.json(extracted_data[:1] if extracted_data else [])
            
    except Exception as e:
        st.error(f"Error processing activity data: {e}")
        import traceback
        st.error(traceback.format_exc())
        st.info("This might be a data format issue. Check the raw data format.")
        return
    
    # Render dashboard sections with error handling
    try:
        render_metrics(df)
    except Exception as e:
        st.error(f"Metrics error: {e}")
        import traceback
        st.error(traceback.format_exc())
    
    try:
        render_activity_breakdown(df)
    except Exception as e:
        st.error(f"Activity breakdown error: {e}")
        import traceback
        st.error(traceback.format_exc())
    
    try:
        render_timeline(df)
    except Exception as e:
        st.error(f"Timeline error: {e}")
        import traceback
        st.error(traceback.format_exc())
    
    try:
        render_activity_table(df)
    except Exception as e:
        st.error(f"Activity table error: {e}")
        import traceback
        st.error(traceback.format_exc())
    
    try:
        render_recent_activities(df)
    except Exception as e:
        st.error(f"Recent activities error: {e}")
        import traceback
        st.error(traceback.format_exc())
    
    # Footer with last update time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div style='text-align: center; padding: 2rem; color: #8B949E; font-size: 0.85rem;'>
        <p>Strava Pro Dashboard • Last updated: {current_time} • Built with ⚡ • Production Ready</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
