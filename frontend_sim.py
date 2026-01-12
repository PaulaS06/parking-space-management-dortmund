import requests

# -------------------------------
# URL endpoint
# -------------------------------
BASE_URL = "http://127.0.0.1:5000/api/nearest"

# -------------------------------
# Options: send address or coordenates
# -------------------------------

# Option A: send address as string
params_address = {
    "address": "Sonnenstrasse 96, Dortmund"
}

# Option B: send coordenates
params_coords = {
    "lat": 51.4883185,
    "lon": 7.424944206571428
}

# -------------------------------
# Make request GET
# -------------------------------

try:
    response = requests.get(BASE_URL, params=params_address)  # Change to params_coords 
    response.raise_for_status()  # error when the request fails
    data = response.json()

    # Show results
    print("Closest parking houses:")
    for p in data:
        print(f"{p['name']} - Dirección: {p['full_address']}")
        print(f"  Haversine (km): {p['distance_haversine_km']}")
        print(f"  Walking distance (m): {p['walking_distance_m']}")
        print(f"  Walking duration (s): {p['walking_duration_s']}\n")

except requests.exceptions.RequestException as e:
    print("Error calling endpoint:", e)
