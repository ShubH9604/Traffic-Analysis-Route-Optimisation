import googlemaps
import datetime

# Load API Key
API_KEY = "AIzaSyCCEbSfQkPOmkbeYaphpCgTkB4GFA1wQj8"
gmaps = googlemaps.Client(key=API_KEY)

def get_traffic_info(start, end, mode="driving"):
    """
    Fetch traffic data including ETA, distance, route summary, and polyline,
    based on the selected mode of transport.
    """
    try:
        # Request directions with user-selected transport mode
        directions = gmaps.directions(
            start, end, mode=mode,  # Mode now changes dynamically
            traffic_model="best_guess",
            departure_time="now",
            alternatives=True
        )

        if directions:
            routes_info = []
            for route in directions:
                route_details = {
                    "eta": route['legs'][0]['duration']['text'] if mode in ["walking", "bicycling", "transit"]
                           else route['legs'][0]['duration_in_traffic']['text'],
                    "distance": route['legs'][0]['distance']['text'],
                    "polyline": route['overview_polyline']['points'],
                    "summary": route['summary']
                }
                routes_info.append(route_details)
            return routes_info
        return None
    except Exception as e:
        print("Error fetching traffic data:", e)
        return None

def get_traffic_trend(start, end, mode="driving"):
    """
    Fetch traffic data at different time intervals to analyze trends,
    based on the selected mode of transport.
    """
    traffic_data = []
    current_time = datetime.datetime.now()

    for i in range(6):  # Get traffic data for the next 6 hours
        departure_time = current_time + datetime.timedelta(hours=i)
        try:
            directions = gmaps.directions(
                start, end, mode=mode,  # Mode now changes dynamically
                traffic_model="best_guess",
                departure_time=departure_time
            )

            if directions:
                eta_seconds = directions[0]['legs'][0]['duration']['value'] if mode in ["walking", "bicycling", "transit"] \
                              else directions[0]['legs'][0]['duration_in_traffic']['value']
                eta_minutes = eta_seconds / 60  # Convert to minutes
                traffic_data.append((departure_time.strftime("%H:%M"), eta_minutes))
        except Exception as e:
            print("Error fetching traffic trend:", e)

    return traffic_data  # ✅ ETA updates according to selected mode