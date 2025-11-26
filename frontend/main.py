from flask import Flask, render_template, request, jsonify, session
import requests

GEOAPIFY_API_KEY = "e2a0ea3f5d5e4efd819ad7345c90e18b"

PARKHOUSES = [
    {"name": "Parkhaus A", "lat": 51.513, "lon": 7.465, "ev_charging": True},
    {"name": "Parkhaus B", "lat": 51.515, "lon": 7.468, "ev_charging": False},
    {"name": "Parkhaus C", "lat": 51.516, "lon": 7.462, "ev_charging": True},
]

ev_filter = False

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

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
    global ev_filter
    ev_filter = request.args.get("ev_charging") == "true"

    results = PARKHOUSES
    if ev_filter:
        results = [p for p in results if p["ev_charging"]]

    return results

@app.route("/api/search")
def api_search():
    results = PARKHOUSES
    if ev_filter:
        results = [p for p in results if p["ev_charging"]]
    return results

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
