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
    {"id": "101092", "full_address": "Königswall, 44137 Dortmund, Germany"},
    {"id": "101059", "full_address": "Propsteihof 9, 44137 Dortmund, Germany"},
    {"id": "101061", "full_address": "Parkdeck Kaufhof, Westenhellweg 72-84, 44137 Dortmund, Germany"},
    {"id": "101099", "full_address": "Hohe Straße 33, 44139 Dortmund, Germany"},
    {"id": "107380", "full_address": "Opernhaus Dortmund, Platz der Alten Synagoge 1, 44137 Dortmund, Germany"},
    {"id": "49249524", "full_address": "NH Dortmund, Königswall 1, 44137 Dortmund, Germany"},
    {"id": "101088", "full_address": "Robert-Schuman-Berufskolleg, Emil-Moog-Platz 15, 44137 Dortmund, Germany"},
    {"id": "101063", "full_address": "zero, Westenhellweg 102-106, 44128 Dortmund, Germany"},
    {"id": "553319", "full_address": "Dr.-Safiye-Ali-Straße 13, 44147 Dortmund, Germany"},
    {"id": "101075", "full_address": "Schmiedingstraße 10, 44137 Dortmund, Germany"},
]

def calculate_price(start_time, end_time):
    try:
        start_time = start_time.replace("Z", "")
        end_time = end_time.replace("Z", "")
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        hours = (end_dt - start_dt).total_seconds() / 3600
        price = round(hours * random.uniform(1, 3), 2)
        return price
    except:
        return None

@app.route("/api/v1/database", methods=["POST"])
def get_parking_info_bulk():
    data = request.json

    
    if not data or not isinstance(data, list):
        return {"error": "JSON body must be a list of objects"}, 400

    results = []
    for item in data:
        parking_id = item.get("id")
        start_time = item.get("start_time")
        end_time = item.get("end_time")

        if not parking_id or not start_time or not end_time:
            results.append({"id": parking_id, "error": "Missing start_time or end_time"})
            continue

        parking = next((p for p in PARKINGS if p["id"] == parking_id), None)
        if not parking:
            results.append({"id": parking_id, "error": "Parking not found"})
            continue

        results.append({
            "id": parking_id,
            "full_address": parking["full_address"],
            "ev_charging": random.choice([True, False]),
            "Total_price": calculate_price(start_time, end_time)
        })
    #save_json(data,"db_received")
    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
