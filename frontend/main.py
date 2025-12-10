from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from datetime import timedelta
import requests

GEOAPIFY_API_KEY = "e2a0ea3f5d5e4efd819ad7345c90e18b"

PARKHOUSES = [
    {"name": "Parkhaus A", "fullAddress":"fullAddressA", "lat": 51.513, "lon": 7.465, "capacity": 15, "priceTotal":15, "ev_charging": True, "walkingTimeMinutes":5, "walkingDistanceKm":0.3},
    {"name": "Parkhaus B", "fullAddress":"fullAddressB", "lat": 51.515, "lon": 7.468, "capacity": 415, "priceTotal":14, "ev_charging": False, "walkingTimeMinutes":10, "walkingDistanceKm":0.65},
    {"name": "Parkhaus C", "fullAddress":"fullAddressC", "lat": 51.516, "lon": 7.462, "capacity": 5, "priceTotal":16, "ev_charging": True, "walkingTimeMinutes":16, "walkingDistanceKm":1.1},
]

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False     # Sessions expire when the browser is closed
app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)

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
    session['ev_filter'] = request.args.get("ev_charging") == "true"
    ev_filter = session.get('ev_filter')

    results = PARKHOUSES
    if ev_filter:
        results = [p for p in results if p["ev_charging"]]

    return results

@app.route("/api/search")
def api_search():
    results = PARKHOUSES
    ev_filter = session.get('ev_filter')
    if ev_filter:
        results = [p for p in results if p["ev_charging"]]
    return results

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
