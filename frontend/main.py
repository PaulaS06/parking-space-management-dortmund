from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from DataTransferObjects import ParkingRequestDto, ParkingRecommendationDto
from BackendRestClient import BackendRestClient
from datetime import timedelta, datetime
import requests
import os

GEOAPIFY_API_KEY = "e2a0ea3f5d5e4efd819ad7345c90e18b"

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False     # Sessions expire when the browser is closed
app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)

# Use environment variable for backend URL, default to Docker service name
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")
backend_client = BackendRestClient(base_url=BACKEND_URL)

# Initialize Flask-Session
Session(app)

@app.route('/')
def home():
    ev_filter = session.get('ev_filter', False)
    return render_template('index.html', ev_filter=ev_filter)

@app.route('/nearby')
def nearby():
    return render_template('window1.html')

@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("q", "")

    if len(query) < 3:
        return jsonify([])

    # Begrenzung auf Dortmund (kleines Rechteck + Countrycode)
    rect_filter = "rect:7.35,51.45,7.55,51.55|countrycode:de"

    url = (
        "https://api.geoapify.com/v1/geocode/autocomplete"
        f"?text={query}&filter={rect_filter}&apiKey={GEOAPIFY_API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    return jsonify(data.get("features", []))

@app.route("/api/filter")
def api_filter():
    # Store the EV filter preference in session
    session['ev_filter'] = request.args.get("ev_charging") == "true"
    
    # Return the current search results with the filter applied
    # This will re-run the search with the filter
    return api_search()

@app.route("/api/search")
def api_search():
    ev_filter = session.get('ev_filter', False)

    # Get parameters from request
    address = request.args.get('address')
    latitude = request.args.get('lat', type=float)
    longitude = request.args.get('lon', type=float)
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    
    # If no coordinates provided but address is, we need to geocode
    # For now, use default Dortmund coordinates if nothing provided
    if latitude is None or longitude is None:
        if address:
            # Try to geocode the address
            try:
                geocode_url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={GEOAPIFY_API_KEY}"
                geocode_response = requests.get(geocode_url)
                geocode_data = geocode_response.json()
                if geocode_data.get("features"):
                    coords = geocode_data["features"][0]["geometry"]["coordinates"]
                    longitude = coords[0]
                    latitude = coords[1]
                else:
                    return jsonify({"error": "Could not find location"}), 400
            except Exception as e:
                return jsonify({"error": f"Geocoding failed: {str(e)}"}), 500
        else:
            # Default to Dortmund city center
            latitude = 51.5136
            longitude = 7.4653
    
    # Parse time inputs - they come as HH:MM format, convert to datetime
    try:
        if start_time_str and end_time_str:
            # Get today's date and combine with the time
            today = datetime.now().date()
            start_time = datetime.strptime(start_time_str, "%H:%M").replace(
                year=today.year, month=today.month, day=today.day
            )
            end_time = datetime.strptime(end_time_str, "%H:%M").replace(
                year=today.year, month=today.month, day=today.day
            )
        else:
            # Default to now + 2 hours
            start_time = datetime.now()
            end_time = datetime.now() + timedelta(hours=2)
    except ValueError as e:
        return jsonify({"error": f"Invalid time format: {str(e)}"}), 400
    
    request_dto = ParkingRequestDto(
        latitude=latitude,
        longitude=longitude,
        start_time=start_time,
        end_time=end_time,
        limit=5
    )

    try:
        results = backend_client.get_parking_recommendations(request_dto)

        if ev_filter:
            results = [r for r in results if r.evCharging]

        return jsonify([r.__dict__ for r in results])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Only enable debug mode if DEBUG environment variable is set
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host='0.0.0.0', port=3000)
