from flask import Flask, render_template, request, jsonify
import requests

GEOAPIFY_API_KEY = "e2a0ea3f5d5e4efd819ad7345c90e18b"

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
