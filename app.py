import streamlit as st
from traffic_analysis import get_traffic_info, get_traffic_trend
from map_display import display_map
import plotly.express as px
import pandas as pd

# Set page title and layout
st.set_page_config(page_title="Real-Time Traffic Analysis & Route Optimization", layout="wide")

# Enable caching to optimize API calls
@st.cache_data
def cached_traffic_info(start, destination, mode):
    return get_traffic_info(start, destination, mode)

# Custom Styling
st.markdown(
    """
    <style>
        body { background-color: #1E1E1E; }
        .sidebar .sidebar-content { background-color: #222; }
        h1, h2, h3, h4, h5, h6, p, span, div { color: white !important; }
        .stButton button { background-color: #FF8C00; color: white; font-weight: bold; }
        .stButton button:hover { background-color: #FF7000; }
        .stTextInput input { background-color: #333; color: white; }
        .route-box, .journey-box { border: 2px solid white; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
        .highlight { color: #FF8C00; font-size: 22px; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center;'>Real-Time Traffic Analysis & Route Optimization</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 📍 Enter Locations")
start_location = st.sidebar.text_input("Start Location", "")
destination_location = st.sidebar.text_input("Destination", "")

st.sidebar.markdown("### 🚗 Select Mode of Transport")
mode_options = {"🚗 Driving": "driving", "🚶 Walking": "walking", "🚴 Bicycling": "bicycling"}
selected_mode = st.sidebar.radio("", list(mode_options.keys()))

st.sidebar.markdown("### ⛽ Estimated Cost Calculator")
fuel_price = st.sidebar.number_input("Fuel Price per Liter (₹)", value=100, min_value=50, max_value=200, step=1)
fuel_efficiency = st.sidebar.number_input("Vehicle Fuel Efficiency (km/l)", value=15, min_value=5, max_value=50, step=1)

if st.sidebar.button("🔍 Get Traffic Data"):
    st.sidebar.success("Fetching best routes...")
    traffic_routes = cached_traffic_info(start_location, destination_location, mode_options[selected_mode])

    if not traffic_routes:
        st.sidebar.error("Invalid locations. Please enter valid city names!")
    else:
        col1, col2 = st.columns([1.6, 2.2])
        with col1:
            st.markdown("<h2 class='highlight'>📌 Journey Details</h2>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="journey-box">
                    <p>📍 <b>Start:</b> {start_location}</p>
                    <p>📍 <b>Destination:</b> {destination_location}</p>
                    <p>📍 <b>Mode:</b> {selected_mode}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("---")

            st.markdown("<h2 class='highlight'>🛣 Available Routes</h2>", unsafe_allow_html=True)

            def get_eta_in_minutes(route):
                eta_str = route['eta'].replace(',', '')
                eta_parts = eta_str.split()
                days, hours, minutes = 0, 0, 0
                
                if "day" in eta_parts:
                    days = int(eta_parts[eta_parts.index("day") - 1])
                if "days" in eta_parts:
                    days = int(eta_parts[eta_parts.index("days") - 1])
                if "hour" in eta_parts:
                    hours = int(eta_parts[eta_parts.index("hour") - 1])
                if "hours" in eta_parts:
                    hours = int(eta_parts[eta_parts.index("hours") - 1])
                if "min" in eta_parts:
                    minutes = int(eta_parts[eta_parts.index("min") - 1])
                if "mins" in eta_parts:
                    minutes = int(eta_parts[eta_parts.index("mins") - 1])
                
                return (days * 1440) + (hours * 60) + minutes

            traffic_routes.sort(key=get_eta_in_minutes)
            fastest_route = traffic_routes[0]
            eta_total_minutes = get_eta_in_minutes(fastest_route)
            
            eta_days = eta_total_minutes // 1440
            eta_hours = (eta_total_minutes % 1440) // 60
            eta_minutes = eta_total_minutes % 60
            
            eta_display = ""
            if eta_days:
                eta_display += f"{eta_days} day "
            if eta_hours:
                eta_display += f"{eta_hours} hrs "
            if eta_minutes:
                eta_display += f"{eta_minutes} min"

            distance_km = float(fastest_route['distance'].split()[0].replace(',', ''))
            estimated_cost = (distance_km / fuel_efficiency) * fuel_price

            st.markdown(
                f"""
                <div class="route-box">
                    <h3 class="highlight">🛣 Fastest Route: {fastest_route['summary']}</h3>
                    <p>🕒 ETA: {eta_display.strip()}</p>
                    <p>📏 Distance: {fastest_route['distance']}</p>
                    <p>💰 Estimated Fuel Cost: ₹{estimated_cost:.2f}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown("<h2 class='highlight'>🗺 Route Map</h2>", unsafe_allow_html=True)
            start_coords = fastest_route['start_location']  # Extract start coordinates from API
            dest_coords = fastest_route['end_location']  # Extract destination coordinates from API

            display_map(fastest_route['polyline'], start_coords, dest_coords)

        st.markdown("---")

        col3, col4 = st.columns([2.2, 1.8])

        with col3:
            st.markdown("<h2 class='highlight'>📊 Traffic Trend Analysis</h2>", unsafe_allow_html=True)
            trend_data = get_traffic_trend(start_location, destination_location, mode_options[selected_mode])

            if trend_data:
                df = pd.DataFrame(trend_data, columns=["Time", "ETA (minutes)"])
                df["ETA (minutes)"] = df["ETA (minutes)"].round(2)
                fig = px.line(df, x="Time", y="ETA (minutes)", markers=True, title="ETA Variation Over Time",
                              line_shape="spline", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Traffic trend data unavailable.")

        with col4:
            st.markdown("<h2 class='highlight'>🚦 Traffic Insights</h2>", unsafe_allow_html=True)
            st.markdown("---")
            if trend_data:
                peak_eta = df["ETA (minutes)"].max()
                min_eta = df["ETA (minutes)"].min()
                avg_eta = df["ETA (minutes)"].mean()

                st.markdown(f"<p class='insight-text'>📌 Peak ETA: {peak_eta:.2f} min</p>", unsafe_allow_html=True)
                st.markdown(f"<p>Traffic is heaviest during this time, causing delays. Consider traveling later to avoid congestion.</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='insight-text'>📌 Average ETA: {avg_eta:.2f} min</p>", unsafe_allow_html=True)
                st.markdown(f"<p>Expected travel time under normal traffic conditions.</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='insight-text'>📌 Congestion Peak: {df.iloc[df['ETA (minutes)'].idxmax()]['Time']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>Peak congestion period—expect longer travel times. Avoid if possible.</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='insight-text'>📌 Smoothest Travel Window: {df.iloc[df['ETA (minutes)'].idxmin()]['Time']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>Least crowded time—fastest travel. Plan accordingly.</p>", unsafe_allow_html=True)
            
            else:
                st.warning("Traffic insights unavailable.")

        st.markdown("<hr style='border: 1px solid #ffffff;'>", unsafe_allow_html=True)
