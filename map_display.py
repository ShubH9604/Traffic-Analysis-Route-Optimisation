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
    midpoint = [(start_lat + dest_lat) / 2, (start_lon + dest_lon) / 2]

    # Create a folium map centered at the midpoint
    m = folium.Map(location=start_point, zoom_start=10)

    # # Add start marker (Green)
    # folium.Marker(
    #     location=[start_lat, start_lon],
    #     popup="Start Location",
    #     icon=folium.Icon(color="green", icon="play", prefix="fa")
    # ).add_to(m)

    # # Add destination marker (Red)
    # folium.Marker(
    #     location=[dest_lat, dest_lon],
    #     popup="Destination",
    #     icon=folium.Icon(color="red", icon="map-marker", prefix="fa")
    # ).add_to(m)

    # Add polyline to the map
    folium.PolyLine(decoded_route, color="blue", weight=5, opacity=0.7).add_to(m)

    # Display map in Streamlit
    folium_static(m)