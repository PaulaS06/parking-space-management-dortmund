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
    session['ev_filter'] = bool(data['ev_charging'])
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

@app.route("/api/search")
def api_search():
    if "lat" not in session or "lon" not in session:
        return jsonify({"error": "location not set"}), 406

    ev_filter = session.get('ev_filter', False)
    lat = session.get('lat')
    lon = session.get('lon')
    start_time_str = session.get('start_time')
    end_time_str = session.get('end_time')

    # Convert ISO strings back to datetime objects
    start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
    end_time = datetime.fromisoformat(end_time_str) if end_time_str else None

    request_dto = ParkingRequestDto(
        latitude=lat,
        longitude=lon,
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
        app.logger.error(f"Unexpected error in /api/search: {str(e)}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

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
