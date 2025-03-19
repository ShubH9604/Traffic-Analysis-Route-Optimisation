import folium
import polyline
import streamlit as st
from streamlit_folium import folium_static

def display_map(encoded_polyline, start_point, destination):
    """
    Displays the route map with a polyline and start/destination markers.
    """
    # Decode polyline into a list of coordinate tuples (lat, lon)
    decoded_route = polyline.decode(encoded_polyline)

    # Extract latitude & longitude of start and destination
    start_lat, start_lon = start_point
    dest_lat, dest_lon = destination

    # Create a folium map centered at the start position
    m = folium.Map(location=[start_lat, start_lon], zoom_start=12)

    # Add polyline to the map
    folium.PolyLine(decoded_route, color="blue", weight=5, opacity=0.7).add_to(m)

    # Add markers for start and destination
    folium.Marker([start_lat, start_lon], popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([dest_lat, dest_lon], popup="Destination", icon=folium.Icon(color="red")).add_to(m)

    # Display map in Streamlit
    folium_static(m)
