from flask import Flask, request, jsonify
import requests
import logging
import math
import json
import os
import traceback
import time as time_module  
from datetime import datetime, time, timedelta

from collections import OrderedDict
app = Flask(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# -------------------------------
# URLs and API Keys
# -------------------------------
DORTMUND_URL = "https://open-data.dortmund.de/api/explore/v2.1/catalog/datasets/parkhauser/records"

BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME", "admin")
BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD", "lYbqZkYhlC2IJin7HcX5")

GEOAPIFY_ROUTING_KEY = os.environ.get("GEOAPIFY_ROUTING_KEY", "9a49c37eba2c4a87ac26e3610becac2b")
DATABASE_SERVICE_URL = os.environ.get("DATABASE_SERVICE_URL", "http://localhost:5001")
API_KEY = os.environ.get("API_KEY", "secure-api-key-123")

from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get("X-API-Key") == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return decorated_function

#-------------------------------
# Function to get parking data
#-------------------------------
import os
import time

UPDATE_INTERVAL = 120  # segundos

def get_parking_data():
    filename = "dortmund_parkings_processed.json"
    filepath = os.path.join(DATA_DIR, filename)
    now = time_module.time()

    # If file dioes not exist, fetch data
    if not os.path.exists(filepath):
        print("Parking file does not exist. Fetching from API...")
        app.logger.info("Parking file does not exist. Fetching from API...")
        return fetch_and_save_parking_data()

    last_update = os.path.getmtime(filepath)
    if now - last_update > UPDATE_INTERVAL:
        print("Parking data is older than 2 minutes. Updating...")
        app.logger.info("Parking data is older than 2 minutes. Updating...")
        return fetch_and_save_parking_data()
    else:
        print("Using cached parking data...")
        app.logger.info("Using cached parking data...")
        return load_json(filename)


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
# Obtain all parking houses and save json file processed
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

                

                all_records.append({
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "lat": lat,
                    "lon": lon,
                    "capacity": p.get("capacity"),
                    "free_spots": p.get("frei"),
                    #"full_address": full_address,
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
            print(f"Traceback: {traceback.format_exc()}")
            break

    # Save raw data
    print(len(raw_records))
    app.logger.info(f"received {len(raw_records)} from open data dortmund.")
    #save_json(raw_records, "dortmund_parkings_raw.json")

    # Save parking houses processed
    save_json(all_records, "dortmund_parkings_processed.json")

    return all_records


import requests

def enrich_parking_info(parkings, start_time, end_time):
    """
    GET request:
    - start_time and end_time sent once
    - ids sent as comma-separated list
    """
    url = f"{DATABASE_SERVICE_URL}/api/v1/database/pricing-total"

    ids = ",".join(str(p["id"]) for p in parkings)

    params = {
        "start_time": start_time,
        "end_time": end_time,
        "ids": ids
    }

    try:
        app.logger.info("query DB")
        resp = requests.get(url, params=params, timeout=10, auth=(BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD))
        resp.raise_for_status()
        db_data = resp.json()

        app.logger.info(f"received {len(db_data)} parkings from DB")
        db_dict = {item["id"]: item for item in db_data}

        for p in parkings:
            info = db_dict.get(p["id"], {})
            p["evCharging"] = info.get("evCharging", False)
            p["priceTotal"] = info.get("priceTotal", 0.0)
            p["fullAddress"] = info.get("fullAddress")

        return parkings

    except Exception as e:
        print("Error fetching parking info:", e)
        print(traceback.format_exc())
        return parkings




# -------------------------------
# Routing Geoapify
# -------------------------------
def geoapify_routing_matrix(user_lat, user_lon, parkings, mode="walk"):
    url = "https://api.geoapify.com/v1/routematrix"
    headers = {"Content-Type": "application/json"}

    body = {
        "mode": mode,
        "sources": [{"location": [user_lon, user_lat]}],
        "targets": [{"location": [p["longitude"], p["latitude"]]} for p in parkings]
        

    }
    #print("Sources:", body["sources"])
    #print("Targets:", body["targets"])

    params = {"apiKey": GEOAPIFY_ROUTING_KEY}

    try:
        resp = requests.post(url, json=body, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("sources_to_targets", [])
        if not results or not results[0]:
            print("Routing matrix returned no data")
            app.logger.info("Routing matrix returned no data")
            return None, None

        distances = [item["distance"] for item in results[0]]
        durations = [item["time"] for item in results[0]]

        return distances, durations

    except Exception as e:
        print("Routing matrix error:", e)
        print(f"Traceback: {traceback.format_exc()}")
        return None, None


# -----------------------------------------
# Funtion that verifies availability
# -----------------------------------------


def parking_is_available(parking, start_dt, end_dt):
    # 1. Basic validations
    if not parking or not start_dt or not end_dt:
        return False

    # If end data is earlier or equal to the start date, it's an error
    if start_dt >= end_dt:
        return False 
    current_check = start_dt

    # Map to know what fields to read based on the day of the week (0=Monday, 6=Sunday)
    day_map = {
        0: ("mostart", "moende"), 
        1: ("distart", "diende"),
        2: ("mistart", "miende"), 
        3: ("dostart", "doende"),
        4: ("frstart", "frende"), 
        5: ("sastart", "saende"),
        6: ("sostart", "soende"),
    }

    # Límite de seguridad para evitar bucles infinitos
    safety_loops = 0

    # 2. Loop: While we haven't covered all the requested time...
    while current_check < end_dt and safety_loops < 30:
        safety_loops += 1
        
        # Calculate when "this day" ends (the next midnight)
        # This is used to split the validation into daily segments
        # We use datetime.min.time() which gives us 00:00:00 without conflicts
        next_midnight = datetime.combine(current_check.date() + timedelta(days=1), datetime.min.time())
        
        # The limit of validation is: either the end of the reservation, or midnight (whichever comes first)
        limit_for_this_segment = min(end_dt, next_midnight)
        
        # Get the opening and closing times for the day we are checking
        weekday = current_check.weekday()
        start_key, end_key = day_map[weekday]
        
        s_str = parking.get(start_key)
        e_str = parking.get(end_key)
        
        # Special logic for Sunday: If empty, use Saturday's schedule
        if weekday == 6:
            if s_str in [None, "-"]: return False
            if e_str is None: e_str = parking.get("saende")

        # If no schedule, it's closed
        if s_str in [None, "-"] or e_str in [None, "-"]:
            return False 

        try:
            # Parse the hours from the JSON
            open_t = datetime.strptime(s_str, "%H:%M").time()
            close_t = datetime.strptime(e_str, "%H:%M").time()
            
            # Convert to datetime complete for comparison
            day_open_dt = datetime.combine(current_check.date(), open_t)
            
            # Key correction for closing time at 23:59
            # If the parking closes at 23:59, mathematically convert it 
            # to 00:00 of the next day so there's no 1-minute gap.
            if close_t.hour == 23 and close_t.minute == 59:
                day_close_dt = datetime.combine(current_check.date() + timedelta(days=1), datetime.min.time())
            else:
                day_close_dt = datetime.combine(current_check.date(), close_t)
                
        except ValueError:
            # If the time format is invalid, assume closed
            return False

        # 3. Comparisons
        # A) The user wants to enter before it opens?
        if current_check < day_open_dt:
            return False
            
        # B) The user wants to stay after it closes?
        # Compare the end of this segment with the closing time
        if limit_for_this_segment > day_close_dt:
            return False

        # If it passes all validations, advance the check time to the end of this segment
        current_check = limit_for_this_segment

    # If the loop ends successfully, it means it covered the entire range
    return True
# ---------------------------------------------------------
# EndPoint 
# ---------------------------------------------------------
@app.route("/api/v1/parkinghouses/walking", methods=["GET"])
@require_api_key
def nearest_parking():
    #fetch_and_save_parking_data()
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)
    start_str = request.args.get("start_time")
    end_str = request.args.get("end_time")
    limit = request.args.get("limit", type=int, default=5)
    ev_charging_str = request.args.get("Ev_charging")
    if not ev_charging_str:
        return {"error": "You should send a value for Ev_charging"}, 400
    ev_charging_str = ev_charging_str.lower()
    if ev_charging_str == "true":
        ev_charging = True
    elif ev_charging_str == "false":
        ev_charging = False
    else:
        return {"error": "Ev_charging must be 'true' or 'false'"}, 400

    if not start_str or not end_str:
        return {"error": "start_time and end_time are required"}, 400

    start_dt = datetime.fromisoformat(start_str.replace("Z", ""))
    end_dt = datetime.fromisoformat(end_str.replace("Z", ""))


    if user_lat is None or user_lon is None:
        return {"error": "You should send coordinates or a valid address"}, 400


    
    parkings = get_parking_data()
    

    available = []
    for p in parkings:
        if not p.get("free_spots") or p["free_spots"] <= 0:
            continue
        if not parking_is_available(p, start_dt, end_dt):
            continue
        available.append({
            "id":p.get("id"),
            "name": p.get("name"),
            "lat": p.get("lat"),
            "lon": p.get("lon"),
            "free_spots": p.get("free_spots")
            
        })
    if not available:
        return {"error": "No parking available"}, 404               

    save_json(available,"available_spots")
    available = enrich_parking_info(available, start_str, end_str)
    save_json(available, "available_db")
    if ev_charging is True:
        available = [p for p in available if p.get("evCharging")]
    

    for p in available:
        p["distance_haversine_km"] = round(haversine(user_lat, user_lon, p["lat"], p["lon"]), 3)

    available.sort(key=lambda x: x["distance_haversine_km"])
    candidates_first_endpoint = available[:limit*3]

    routing_targets = []

    for p in candidates_first_endpoint:
                          
        routing_targets.append({
            
            "name": p.get("name"),
            "fullAddress": p.get("fullAddress"),
            "latitude": p.get("lat"),
            "longitude": p.get("lon"),
            "capacity": p.get("free_spots", 0),
            "evCharging": p.get("evCharging"),
            "priceTotal": p.get("priceTotal"),
            "walkingTimeMinutes": None,
            "walkingDistanceInKm": None
        })


    distances, durations = geoapify_routing_matrix(
    user_lat,
    user_lon,
    routing_targets,
    mode="walk"
)

    if distances and durations:
        for i in range(min(len(routing_targets), len(distances))):
            routing_targets[i]["walkingDistanceInKm"] = round(distances[i] / 1000, 1)
            routing_targets[i]["walkingTimeMinutes"] = round(durations[i] / 60, 0)
    routing_targets = [
        p for p in routing_targets
        if p["walkingDistanceInKm"] is not None
    ]

    routing_targets.sort(key=lambda x: x["walkingDistanceInKm"])
    result_first_endpoint = routing_targets[:limit]

    save_json(result_first_endpoint, "nearest_output_first_endpoint.json")

    return jsonify(result_first_endpoint)

####################################################################################
#Functions Second Endpoint
def enrich_parking_info_second_endpoint(parkings):
    """
    GET request with ids only
    """
    url = f"{DATABASE_SERVICE_URL}/api/v1/database/pricing-hour"

    ids = ",".join(str(p["id"]) for p in parkings)
    params = {"ids": ids}

    try:
        resp = requests.get(url, params=params, timeout=10, auth=(BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD))
        resp.raise_for_status()
        db_data = resp.json()

        db_dict = {item["id"]: item for item in db_data}

        for p in parkings:
            info = db_dict.get(p["id"], {})
            p["evCharging"] = info.get("evCharging", False)
            p["pricePerHour"] = info.get("pricePerHour", 0.0)
            p["fullAddress"] = info.get("fullAddress")

        return parkings

    except Exception as e:
        print("Error fetching parking info:", e)
        print(traceback.format_exc())
        return parkings

    
def geoapify_routing_matrix_second_endpoint(user_lat, user_lon, parkings, mode="drive"):
    url = "https://api.geoapify.com/v1/routematrix"
    headers = {"Content-Type": "application/json"}

    body = {
        "mode": mode,
        "sources": [{"location": [user_lon, user_lat]}],
        "targets": [{"location": [p["longitude"], p["latitude"]]} for p in parkings]
        

    }
    #print("Sources:", body["sources"])
    #print("Targets:", body["targets"])

    params = {"apiKey": GEOAPIFY_ROUTING_KEY}

    try:
        resp = requests.post(url, json=body, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("sources_to_targets", [])
        if not results or not results[0]:
            print("Routing matrix returned no data")
            return None, None

        distances = [item["distance"] for item in results[0]]
        durations = [item["time"] for item in results[0]]

        return distances, durations

    except Exception as e:
        print("Routing matrix error:", e)
        print(f"Traceback: {traceback.format_exc()}")
        return None, None

############################
#define a second endpoint for Frontend
@app.route("/api/v1/parkinghouses/nearby", methods = ['GET'])
@require_api_key
def nearby_parking():
    #fetch_and_save_parking_data()
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)
    limit = request.args.get("limit",type=int, default=5)
    ev_charging_str = request.args.get("Ev_charging")
    if not ev_charging_str:
        return {"error": "You should send a value for Ev_charging"}, 400
    ev_charging_str = ev_charging_str.lower()
    if ev_charging_str == "true":
        ev_charging = True
    elif ev_charging_str == "false":
        ev_charging = False
    else:
        return {"error": "Ev_charging must be 'true' or 'false'"}, 400


    if user_lat is None or user_lon is None:
        return {"error": "You should send coordinates or a valid address"}, 400

    if ev_charging is None:
        return {"error": "You should send a valid Ev_charging parameter"}, 400

    parkings = get_parking_data()   #fetch_and_save_parking_data()
    


    available = []
    for p in parkings:
        if not p.get("free_spots") or p["free_spots"] <= 0:
            continue

        available.append({
            "id":p.get("id"),
            "name": p.get("name"),
            "lat": p.get("lat"),
            "lon": p.get("lon"),
            "free_spots": p.get("free_spots") 
        })
    save_json(available,"available_spots_second_endpoint")
    if not available:
        return {"error": "No parking available"}, 404
                    
    #save_json(available,"available_spots")
    available = enrich_parking_info_second_endpoint(available)
    save_json(available, "available_db")
    if ev_charging:
        available = [p for p in available if p.get("evCharging")]

    for p in available:
        p["distance_haversine_km"] = round(haversine(user_lat, user_lon, p["lat"], p["lon"]), 3)

    available.sort(key=lambda x: x["distance_haversine_km"])
    candidates = available[:limit*3]

    routing_targets = []

    for p in candidates:
                          
        routing_targets.append({
            
            "name": p.get("name"),
            "fullAddress": p.get("fullAddress"),
            "latitude": p.get("lat"),
            "longitude": p.get("lon"),
            "capacity": p.get("free_spots", 0),
            "evCharging": p.get("evCharging"),
            "pricePerHour": p.get("pricePerHour"),
            "drivingTimeMinutes": None,
            "drivingDistanceInKm": None
        })


    distances, durations = geoapify_routing_matrix_second_endpoint(
    user_lat,
    user_lon,
    routing_targets,
    mode="drive"
)

    if distances and durations:
        for i in range(min(len(routing_targets), len(distances))):
            routing_targets[i]["drivingDistanceInKm"] = round(distances[i] / 1000, 1)
            routing_targets[i]["drivingTimeMinutes"] = round(durations[i] / 60, 0)

    routing_targets = [
        p for p in routing_targets
        if p["drivingDistanceInKm"] is not None
    ]
    routing_targets.sort(key=lambda x: x["drivingDistanceInKm"])

    result_second_endpoint = routing_targets[:limit]

    save_json(result_second_endpoint, "nearest_output_drive.json")
    return jsonify(result_second_endpoint)

########################

@app.route("/")
def home():
    return "Backend is running"

if __name__ == "__main__":
    # Create JSON of parking houses once when it starts
    #if not os.path.exists(os.path.join(DATA_DIR, "dortmund_parkings_processed.json")):
        #fetch_and_save_parking_data()

    # Only enable debug mode if DEBUG environment variable is set
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=8000, debug=debug_mode)

