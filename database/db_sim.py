from flask import Flask, request, jsonify
import random
from datetime import datetime
import json 
import os

app = Flask(__name__)

DATABASE = "database"
os.makedirs(DATABASE, exist_ok=True)

def save_json(data, filename):
    filepath = os.path.join(DATABASE, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"JSON saved: {filepath}")

# Sample parking data
PARKINGS = [
    {"id": "101067", "full_address": "Burgwall 4, 44135 Dortmund, Germany"},
    {"id": "553286", "full_address": "Auf dem Steine 33, 44143 Dortmund, Germany"},
    {"id": "101095", "full_address": "Steinstraße 44, 44147 Dortmund, Germany"},
    {"id": "101065", "full_address": "Hohe Luft 6, 44135 Dortmund, Germany"},
    {"id": "101052", "full_address": "Südwall 4, 44122 Dortmund, Germany"},
    {"id": "103824", "full_address": "Kuckelke 3, 44135 Dortmund, Germany"},
    {"id": "101057", "full_address": "Hansaplatz 1, 44137 Dortmund, Germany"},
    {"id": "107394", "full_address": "Johannesstraße 9-17, 44137 Dortmund, Germany"},
    {"id": "553203", "full_address": "Innsbruckstraße 7, 44339 Dortmund, Germany"},
    {"id": "553258", "full_address": "Joseph-Scherer-Straße 10, 44139 Dortmund, Germany"},
    {"id": "101070", "full_address": "Freistuhl 7, 44137 Dortmund, Germany"},
    {"id": "101073", "full_address": "Kampstraße 47, 44137 Dortmund, Germany"},
]



# --- NEW GET endpoint for first endpoint ---
@app.route("/api/v1/database/pricing-total", methods=["GET"])
def get_parking_info_bulk_get():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    ids_str = request.args.get("ids")

    if not start_time or not end_time or not ids_str:
        return {"error": "start_time, end_time and ids are required"}, 400

    ids_list = ids_str.split(",")
    results = []

    for parking_id in ids_list:
        parking = next((p for p in PARKINGS if p["id"] == parking_id.strip()), None)
        if not parking:
            results.append({"id": parking_id, "error": "Parking not found"})
            continue

        results.append({
            "id": parking_id,
            "fullAddress": parking["full_address"],
            "evCharging": random.choice([True, False]), 
            "priceTotal": 50
        })

    # Save for debugging
    save_json({"start_time": start_time, "end_time": end_time, "ids": ids_list, "results": results}, "sent_from_backend_get.json")

    return jsonify(results)



# --- NEW GET endpoint for second endpoint ---
@app.route("/api/v1/database/pricing-hour", methods=["GET"])
def get_parking_info_bulk_second():
    ids_str = request.args.get("ids")
    if not ids_str:
        return {"error": "ids parameter is required"}, 400

    ids_list = [i.strip() for i in ids_str.split(",")]
    results = []

    for parking_id in ids_list:
        parking = next((p for p in PARKINGS if p["id"] == parking_id), None)
        if not parking:
            results.append({"id": parking_id, "error": "Parking not found"})
            continue

        results.append({
            "id": parking_id,
            "fullAddress": parking["full_address"],
            "evCharging": True,  # or random.choice([True, False])
            "pricePerHour": 3
        })

    # Save for debugging
    save_json({"ids": ids_list, "results": results}, "sent_from_backend_second_get.json")

    return jsonify(results)



if __name__ == "__main__":
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=5001, debug=debug_mode)
