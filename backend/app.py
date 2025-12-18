from flask import Flask, request, jsonify
import requests
import math
import json
import os
from datetime import datetime, time
from collections import OrderedDict
app = Flask(__name__)

# -------------------------------
# URLs and API Keys
# -------------------------------
DORTMUND_URL = "https://open-data.dortmund.de/api/explore/v2.1/catalog/datasets/parkhauser/records"
GEOAPIFY_GEOCODE_KEY = "e49de089f7b64863bb39e194ddf6152b"
GEOAPIFY_ROUTING_KEY = "9a49c37eba2c4a87ac26e3610becac2b"

# -------------------------------
# Folder
# -------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------------
# Save json files
# -------------------------------
def save_json(data, filename):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"JSON saved: {filepath}")

# -------------------------------
# Read json files
# -------------------------------
def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# -------------------------------
# Haversine: Geometrical calculation of walking distance
# -------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# -------------------------------
# Obtain all parking houses and save json file with addresses
# -------------------------------
def fetch_and_save_parking_data():
    all_records = []
    limit = 10  # 10 registers
    offset = 0

    # List to save raw data
    raw_records = []

    while True:
        url = f"{DORTMUND_URL}?limit={limit}&offset={offset}"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            records = data.get("results", [])

            if not records:
                break

            # Save raw data
            raw_records.extend(records)

            for p in records:
                geo = p.get("geo_point_2d")
                if not geo:
                    continue
                lat = geo.get("lat")
                lon = geo.get("lon")
                if lat is None or lon is None:
                    continue

                # Reverse geocoding 
                full_address = None
                try:
                    url_geo = "https://api.geoapify.com/v1/geocode/reverse"
                    params = {"lat": lat, "lon": lon, "apiKey": "113dd9887da44fccb992d13abcb5f11f"}
                    resp_geo = requests.get(url_geo, params=params, timeout=5).json()
                    features = resp_geo.get("features", [])
                    if features:
                        full_address = features[0].get("properties", {}).get("formatted")
                except Exception as e:
                    print("Error reverse geocoding:", e)

                all_records.append({
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "lat": lat,
                    "lon": lon,
                    "capacity": p.get("capacity"),
                    "free_spots": p.get("frei"),
                    "full_address": full_address,
                    "mostart": p.get("mostart"),
                    "moende": p.get("moende"),
                    "distart": p.get("distart"),
                    "diende": p.get("diende"),
                    "mistart": p.get("mistart"),
                    "miende": p.get("miende"),
                    "dostart": p.get("dostart"),
                    "doende": p.get("doende"),
                    "frstart": p.get("frstart"),
                    "frende": p.get("frende"),
                    "sastart": p.get("sastart"),
                    "saende": p.get("saende"),
                    "sostart": p.get("sostart"),
                    "soende": p.get("soende")
                })

            offset += limit  # next block of registers

        except Exception as e:
            print(f"Error fetching data: {e}")
            break

    # Save raw data
    print(len(raw_records))
    save_json(raw_records, "dortmund_parkings_raw.json")

    # Save parkign houses with addresses
    save_json(all_records, "dortmund_parkings_with_address.json")

    return all_records


# -------------------------------
# Geocoding user address
# -------------------------------
def geocode_address(address):
    address = address.replace('ß', 'ss')
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": address, "apiKey": GEOAPIFY_GEOCODE_KEY}
    try:
        resp = requests.get(url, params=params, timeout=5).json()
        features = resp.get("features", [])
        if features:
            lon, lat = features[0]["geometry"]["coordinates"]
            return lat, lon
    except Exception as e:
        print("Error geocoding user address:", e)
    return None, None

# -------------------------------
# Routing Geoapify
# -------------------------------
def geoapify_routing(origin_lat, origin_lon, dest_lat, dest_lon, mode="walk"):
    url = "https://api.geoapify.com/v1/routing"
    waypoints = f"{origin_lat},{origin_lon}|{dest_lat},{dest_lon}"
    params = {
        "waypoints": waypoints,
        "mode": mode,
        "apiKey": GEOAPIFY_ROUTING_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=5).json()
        features = resp.get("features", [])
        if features:
            props = features[0].get("properties", {})
            distance = props.get("distance")
            duration = props.get("time")
            return distance, duration
    except Exception as e:
        print(f"Error routing:", e)
    return None, None

# -------------------------------
# Endpoint: closest parking houses
# -------------------------------
from datetime import datetime, time

# -----------------------------------------
# Funtion that verifies availability
# -----------------------------------------
def parking_is_available(parking, start_dt, end_dt):
    # Day of the week: Monday=0 ... Sunday=6
    weekday = start_dt.weekday()

    # Select field based on the day
    day_map = {
        0: ("mostart", "moende", "sastart", "saende"),  # Monday
        1: ("distart", "diende", "sastart", "saende"),  # Tuesday
        2: ("mistart", "miende", "sastart", "saende"),  # Wednesday
        3: ("dostart", "doende", "sastart", "saende"),  # Thursday
        4: ("frstart", "frende", "sastart", "saende"),  # Friday
        5: ("sastart", "saende", "sastart", "saende"),  # Saturday
        6: ("sostart", "soende", "sastart", "saende"),  # Sunday 
    }

    start_field, end_field, sat_start_field, sat_end_field = day_map[weekday]
    start_str = parking.get(start_field)
    end_str = parking.get(end_field)

    # ----- Special cases -----

    # "-" means closed day
    if start_str == "-" or end_str == "-":
        return False

    # If sunday: soende = null → use saende
    if weekday == 6:
        if start_str in [None, "-"]:
            return False  # sunday does not open
        if end_str is None:
            # Use saende
            end_str = parking.get(sat_end_field)

    # If any field is None → closed
    if start_str is None or end_str is None:
        return False

    # -----------------------------------------
    # Convert "HH:MM" to datetime
    # -----------------------------------------
    try:
        open_t = datetime.strptime(start_str, "%H:%M").time()
        close_t = datetime.strptime(end_str, "%H:%M").time()
    except:
        return False

    parking_open_dt = datetime.combine(start_dt.date(), open_t)
    parking_close_dt = datetime.combine(start_dt.date(), close_t)

    # -----------------------------------------
    # Verify if user frame time is within
    # -----------------------------------------
    return parking_open_dt <= start_dt and end_dt <= parking_close_dt



# ---------------------------------------------------------
# EndPoint 
# ---------------------------------------------------------
@app.route("/api/v1/parkinghouses/walking", methods=["GET"])
def nearest_parking():
    address = request.args.get("address", type=str)
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)
    limit = request.args.get("limit", type=int)
    start_str = request.args.get("start_time")
    end_str = request.args.get("end_time")

    if not start_str or not end_str:
        return {"error": "start_time and end_time are required"}, 400

    start_dt = datetime.fromisoformat(start_str.replace("Z", ""))
    end_dt = datetime.fromisoformat(end_str.replace("Z", ""))

    if address and (user_lat is None or user_lon is None):
        user_lat, user_lon = geocode_address(address)

    if user_lat is None or user_lon is None:
        return {"error": "You should send coordinates or a valid address"}, 400

    parkings = load_json("dortmund_parkings_with_address.json")
    if not parkings:
        parkings = fetch_and_save_parking_data()

    available = []
    for p in parkings:

        if not p.get("free_spots") or p["free_spots"] <= 0:
            continue

        if not parking_is_available(p, start_dt, end_dt):
            continue

        d_km = haversine(user_lat, user_lon, p["lat"], p["lon"])


        filtered = {
            "id": p.get("id"),
            "name": p.get("name"),
            "fullAddress": p.get("full_address"),
            "latitude": p.get("lat"),
            "longitude": p.get("lon"),
            "capacity": p.get("free_spots", 0),  # Available spots
            "distance_haversine_km": round(d_km, 3),
            "evCharging": False,  # Default to False, can be enhanced with real data
            "priceTotal": 0.0,  # Default price, can be calculated based on duration,
            "walkingTimeMinutes": None,
            "walkingDistanceInKm": None

        }

        available.append(filtered)

    # available.sort(key=lambda x: x["distance_haversine_km"])
    nearest_5 = available[:limit]
    for p in nearest_5:
        p.pop("id", None)
        p.pop("distance_haversine_km", None)

   
    for p in nearest_5:
        distance, duration = geoapify_routing(user_lat, user_lon, p["latitude"], p["longitude"], mode="walk")

        p["walkingDistanceInKm"] = round(distance / 1000, 3) if distance else None
        p["walkingTimeMinutes"] = round(duration / 60, 2) if duration else None
   

    save_json(nearest_5, "nearest_output.json")
    return jsonify(nearest_5)


@app.route("/")
def home():
    return "Backend is running"

if __name__ == "__main__":
    # Create JSON of parking houses once when it starts
    if not os.path.exists(os.path.join(DATA_DIR, "dortmund_parkings_with_address.json")):
        fetch_and_save_parking_data()
    # Only enable debug mode if DEBUG environment variable is set
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=8000, debug=debug_mode)

