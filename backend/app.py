from flask import Flask, request, jsonify
import requests
import math
import json
import os
import traceback
from datetime import datetime, time
from collections import OrderedDict
app = Flask(__name__)

# -------------------------------
# URLs and API Keys
# -------------------------------
DORTMUND_URL = "https://open-data.dortmund.de/api/explore/v2.1/catalog/datasets/parkhauser/records"
GEOAPIFY_ROUTING_KEY = "9a49c37eba2c4a87ac26e3610becac2b"
DATABASE_SERVICE_URL = os.environ.get("DATABASE_SERVICE_URL", "http://localhost:5001")

#-------------------------------
# Function to get parking data
#-------------------------------
import os
import time

UPDATE_INTERVAL = 120  # segundos

def get_parking_data():
    filename = "dortmund_parkings_processed.json"
    filepath = os.path.join(DATA_DIR, filename)
    now = time.time()

    # If file dioes not exist, fetch data
    if not os.path.exists(filepath):
        print("Parking file does not exist. Fetching from API...")
        return fetch_and_save_parking_data()

    last_update = os.path.getmtime(filepath)
    if now - last_update > UPDATE_INTERVAL:
        print("Parking data is older than 2 minutes. Updating...")
        return fetch_and_save_parking_data()
    else:
        print("Using cached parking data...")
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
    #save_json(raw_records, "dortmund_parkings_raw.json")

    # Save parking houses processed
    save_json(all_records, "dortmund_parkings_processed.json")

    return all_records


import requests

def enrich_parking_info(parkings, start_time, end_time):
    """
    Receives list of parkings with id and send it to microservice to get
    ev_charging, Total_price y full_address. Then updates each parking
    of the list with that info.
    """
    url = f"{DATABASE_SERVICE_URL}/api/v1/database"  #URL DATABASE MICROSERVICE
    payload = [{"id": p["id"], "start_time": start_time, "end_time": end_time} for p in parkings]

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        db_data = resp.json()  # List of dicts with id, ev_charging, Total_price, full_address
        #save_json(db_data,"results_db")
        # Create a dict fast to look for id
        db_dict = {item["id"]: item for item in db_data}

        # Add microservice info to json file that already exists
        for p in parkings:
            info = db_dict.get(p["id"], {})
            p["evCharging"] = info.get("evCharging", False)
            p["priceTotal"] = info.get("priceTotal", 0.0)
            p["fullAddress"] = info.get("fullAddress", p.get("fullAddress"))

        return parkings

    except Exception as e:
        print("Error fetching parking info:", e)
        print(f"Traceback: {traceback.format_exc()}")
        # If it fails, returns original parkings with modification
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
    print("Sources:", body["sources"])
    print("Targets:", body["targets"])

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
    fetch_and_save_parking_data()
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)
    start_str = request.args.get("start_time")
    end_str = request.args.get("end_time")
    ev_charging = request.args.get("Ev_charging", type=bool)
    limit = request.args.get("limit", type=int, default=5)

    if not start_str or not end_str:
        return {"error": "start_time and end_time are required"}, 400

    start_dt = datetime.fromisoformat(start_str.replace("Z", ""))
    end_dt = datetime.fromisoformat(end_str.replace("Z", ""))


    if user_lat is None or user_lon is None:
        return {"error": "You should send coordinates or a valid address"}, 400

    if ev_charging is None:
        return {"error": "You should send a boolean value for Ev_charging"}, 400
    
    parkings = load_json("dortmund_parkings_processed.json")
    if not parkings:
        parkings = fetch_and_save_parking_data()

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
            routing_targets[i]["walkingDistanceInKm"] = round(distances[i] / 1000, 3)
            routing_targets[i]["walkingTimeMinutes"] = round(durations[i] / 60, 2)
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
    Receives list of parkings with id and send it to microservice to get
    ev_charging, Total_price y full_address. Then updates each parking
    of the list with that info.
    """
    url = f"{DATABASE_SERVICE_URL}/api/v1/database_second_endpoint"  #URL DATABASE MICROSERVICE
    payload = [{"id": p["id"]} for p in parkings]

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        db_data = resp.json()  # List of dicts with id, ev_charging, Total_price, full_address
        save_json(db_data,"results_db")
        # Create a dict fast to look for id
        db_dict = {item["id"]: item for item in db_data}

        # Add microservice info to json file that already exists
        for p in parkings:
            info = db_dict.get(p["id"], {})
            p["evCharging"] = info.get("evCharging", False)
            p["pricePerHour"] = info.get("pricePerHour", 0.0)
            p["fullAddress"] = info.get("fullAddress", p.get("fullAddress"))

        return parkings

    except Exception as e:
        print("Error fetching parking info:", e)
        print(f"Traceback: {traceback.format_exc()}")
        # If it fails, returns original parkings with modification
        return parkings
    
def geoapify_routing_matrix_second_endpoint(user_lat, user_lon, parkings, mode="drive"):
    url = "https://api.geoapify.com/v1/routematrix"
    headers = {"Content-Type": "application/json"}

    body = {
        "mode": mode,
        "sources": [{"location": [user_lon, user_lat]}],
        "targets": [{"location": [p["longitude"], p["latitude"]]} for p in parkings]
        

    }
    print("Sources:", body["sources"])
    print("Targets:", body["targets"])

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
def nearby_parking():
    #fetch_and_save_parking_data()
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)
    ev_charging = request.args.get("Ev_charging", type=bool)
    limit = request.args.get("limit",type=int, default=5)


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
            routing_targets[i]["drivingDistanceInKm"] = round(distances[i] / 1000, 3)
            routing_targets[i]["drivingTimeMinutes"] = round(durations[i] / 60, 2)

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

