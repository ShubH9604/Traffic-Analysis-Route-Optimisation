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
        .sidebar .sidebar-content { background-color: #222; padding-top: 0px !important; }
        h1, h2, h3, h4, h5, h6, p, span, div { color: white !important; }
        .stButton button { background-color: #FF8C00; color: white; font-weight: bold; }
        .stButton button:hover { background-color: #FF7000; }
        .stTextInput input { background-color: #333; color: white; }
        .stRadio div { color: white !important; }
        .bold-text { font-size: 20px; font-weight: bold; font-family: Arial, sans-serif; }
        .highlight { color: #FF8C00; font-size: 22px; font-weight: bold; }
        .route-box { border: 2px solid white; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
        .journey-box { border: 2px solid white; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
        .insight-text { font-size: 18px; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown("<h1 style='text-align: center;'>Real-Time Traffic Analysis & Route Optimization</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("<h2 style='margin-bottom: -35px;'>🚦 Smart Travel Assistant</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Input fields
st.sidebar.markdown("### 📍 Enter Locations")
start_location = st.sidebar.text_input("Start Location", "")
destination_location = st.sidebar.text_input("Destination", "")

# Mode of Transport selection
st.sidebar.markdown("### 🚗 Select Mode of Transport")
mode_options = {
    "🚗 Driving": "driving",
    "🚶 Walking": "walking",
    "🚴 Bicycling": "bicycling",
}
selected_mode = st.sidebar.radio("", list(mode_options.keys()))

# Estimated cost calculator
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
                    <p class='bold-text'>📍 <b>Start:</b> {start_location}</p>
                    <p class='bold-text'>📍 <b>Destination:</b> {destination_location}</p>
                    <p class='bold-text'>📍 <b>Mode:</b> {selected_mode}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("---")

            st.markdown("<h2 class='highlight'>🛣 Available Routes</h2>", unsafe_allow_html=True)
            # Function to convert ETA string to total minutes
            def get_eta_in_minutes(route):
                eta_str = route['eta']
                eta_parts = eta_str.split()
                eta_hours = 0
                eta_minutes = 0

                if "hour" in eta_parts:
                    eta_hours = int(eta_parts[eta_parts.index("hour") - 1])
                elif "hours" in eta_parts:
                    eta_hours = int(eta_parts[eta_parts.index("hours") - 1])

                if "min" in eta_parts:
                    eta_minutes = int(eta_parts[eta_parts.index("min") - 1])
                elif "mins" in eta_parts:
                    eta_minutes = int(eta_parts[eta_parts.index("mins") - 1])

                return (eta_hours * 60) + eta_minutes

            # Sort routes by ETA (ascending order, fastest route first)
            traffic_routes.sort(key=get_eta_in_minutes)

            # Select the fastest route
            fastest_route = traffic_routes[0]
            eta_total_minutes = get_eta_in_minutes(fastest_route)

            # Convert ETA to display format
            eta_hours = eta_total_minutes // 60
            eta_minutes = eta_total_minutes % 60
            eta_display = f"{eta_hours} hrs {eta_minutes} min" if eta_hours else f"{eta_minutes} min"

            # Fuel cost estimation
            distance_km = float(fastest_route['distance'].split()[0].replace(',', ''))
            estimated_cost = (distance_km / fuel_efficiency) * fuel_price

            # Display only the fastest route
            st.markdown(
                f"""
                <div class="route-box">
                    <h3 class="highlight">🛣 Fastest Route: {fastest_route['summary']}</h3>
                    <p class='bold-text'>🕒 ETA: {eta_display}</p>
                    <p class='bold-text'>📏 Distance: {fastest_route['distance']}</p>
                    <p class='bold-text'>💰 Estimated Fuel Cost: ₹{estimated_cost:.2f}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown("<h2 class='highlight'>🗺 Route Map</h2>", unsafe_allow_html=True)
            start_coords = (23.0225, 72.5714)  # Dummy Ahmedabad coords
            dest_coords = (19.0760, 72.8777)  # Dummy Mumbai coords
            display_map(traffic_routes[0]['polyline'], start_coords, dest_coords)

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