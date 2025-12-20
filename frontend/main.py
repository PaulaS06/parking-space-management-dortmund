from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from DataTransferObjects import ParkingRequestDto, ParkingRecommendationDto
from BackendRestClient import BackendRestClient
from datetime import timedelta, datetime, date
import requests

GEOAPIFY_API_KEY = "e2a0ea3f5d5e4efd819ad7345c90e18b"

PARKHOUSES = [
    {"name": "Parkhaus A", "fullAddress":"fullAddressA", "lat": 51.513, "lon": 7.465, "capacity": 15, "priceTotal":15, "ev_charging": True, "walkingTimeMinutes":5, "walkingDistanceKm":0.3},
    {"name": "Parkhaus B", "fullAddress":"fullAddressB", "lat": 51.515, "lon": 7.468, "capacity": 415, "priceTotal":14, "ev_charging": False, "walkingTimeMinutes":10, "walkingDistanceKm":0.65},
    {"name": "Parkhaus C", "fullAddress":"fullAddressC", "lat": 51.516, "lon": 7.462, "capacity": 5, "priceTotal":16, "ev_charging": True, "walkingTimeMinutes":16, "walkingDistanceKm":1.1},
    {"name": "Parkhaus C", "fullAddress":"fullAddressC", "lat": 51.516, "lon": 7.462, "capacity": 5, "priceTotal":16, "ev_charging": True, "walkingTimeMinutes":16, "walkingDistanceKm":1.1},
    {"name": "Parkhaus C", "fullAddress":"fullAddressC", "lat": 51.516, "lon": 7.462, "capacity": 5, "priceTotal":16, "ev_charging": False, "walkingTimeMinutes":16, "walkingDistanceKm":1.1},
]

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False     # Sessions expire when the browser is closed
app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)

backend_client = BackendRestClient(base_url="http://127.0.0.1:8000", username="admin", password="admin")

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

@app.route("/api/search")
def api_search():
    #results = PARKHOUSES
    ev_filter = session.get('ev_filter', False)
    lat = session.get('lat')
    lon = session.get('lon')
    start_time = session.get('start_time')
    end_time = session.get('end_time')

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

        return jsonify([r.__dict__ for r in results])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    app.run(debug=True, host='0.0.0.0')
