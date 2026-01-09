from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from DataTransferObjects import ParkingRequestDto
from BackendRestClient import BackendRestClient
from datetime import timedelta, datetime, date
from Exceptions import BackendServerError, InvalidParameterError, NoResultsError, AuthFailedError
import requests
import os

GEOAPIFY_API_KEY = "e2a0ea3f5d5e4efd819ad7345c90e18b"

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False     # Sessions expire when the browser is closed
app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)

# Use environment variable for backend URL, default to Docker service name
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")
backend_client = BackendRestClient(base_url=BACKEND_URL, username="admin", password="admin")

# Initialize Flask-Session
Session(app)

@app.route('/')
def home():
    ev_filter = session.get('ev_filter', False)
    return render_template('index.html', ev_filter=ev_filter)

@app.route('/nearby')
def nearby():
    return render_template('nearby.html')

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

@app.route("/set_filter", methods=["POST"])
def set_filter():
    data = request.get_json()
    session['ev_filter'] = eval(data['ev_charging'])
    return {"status": "ok"}

@app.route("/set_location", methods=["POST"])
def set_location():
    data = request.get_json()

    session["lat"] = data["lat"]
    session["lon"] = data["lon"]

    return jsonify({"status": "ok"})

@app.route("/details")
def details():
    return render_template('details.html')

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

    # Get parameters from session first, then from request
    latitude = session.get('lat') or request.args.get('lat', type=float)
    longitude = session.get('lon') or request.args.get('lon', type=float)
    address = request.args.get('address')
    start_time_str = session.get('start_time') or request.args.get('start_time')
    end_time_str = session.get('end_time') or request.args.get('end_time')
    
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
    
    # Parse time inputs - they come as HH:MM format or ISO format from session, convert to datetime
    try:
        if start_time_str and end_time_str:
            # Check if it's already a datetime string (from session)
            if isinstance(start_time_str, str) and 'T' in start_time_str:
                # It's already ISO format from session
                start_time = datetime.fromisoformat(start_time_str)
                end_time = datetime.fromisoformat(end_time_str)
            else:
                # Get today's date and combine with the time (HH:MM format from request)
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
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid time format: {str(e)}"}), 400
    
    request_dto = ParkingRequestDto(
        latitude=latitude,
        longitude=longitude,
        start_time=start_time,
        end_time=end_time,
        ev_charging=ev_filter,
        limit=5
    )

    try:
        results = backend_client.get_parking_recommendations(request_dto)

        if ev_filter:
            results = [r for r in results if r.evCharging]

        return jsonify([r.__dict__ for r in results])

    except InvalidParameterError as e:
        return jsonify({"error": str(e)}), 400

    except AuthFailedError as e:
        return jsonify({"error": str(e)}), 401

    except NoResultsError as e:
        return jsonify({
            "error": str(e),
            "results": []
        }), 404

    except BackendServerError as e:
        return jsonify({"error": str(e)}), 502  # Bad Gateway

    except Exception as e:
        return jsonify({"error": "Unexpected error"}), 500

@app.route("/set_time", methods=["POST"])
def set_time():
    data = request.get_json()

    start_time_str = data["start_time"]
    end_time_str = data["end_time"]

    today = date.today()

    start_dt = datetime.combine(
        today,
        datetime.strptime(start_time_str, "%H:%M").time()
    )

    end_dt = datetime.combine(
        today,
        datetime.strptime(end_time_str, "%H:%M").time()
    )

    if end_dt <= start_dt:
        end_dt = end_dt.replace(day=end_dt.day + 1)

    session["start_time"] = start_dt.isoformat()
    session["end_time"] = end_dt.isoformat()

    return {"status": "ok"}

if __name__ == '__main__':
    # Only enable debug mode if DEBUG environment variable is set
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host='0.0.0.0', port=3000)
