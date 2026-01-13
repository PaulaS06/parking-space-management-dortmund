from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime
import math

app = Flask(__name__)

@app.route("/api/v1/database/pricing-total", methods=["GET"])
def get_parking_info_bulk_get():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    ids_str = request.args.get("ids")

    # 1. Validate input
    if not start_time or not end_time or not ids_str:
        return {"error": "start_time, end_time and ids are required"}, 400

    try:
        ids = [int(i.strip()) for i in ids_str.split(",") if i.strip()]
    except ValueError:
        return {"error": "ids must be comma-separated integers"}, 400

    # 2. Parse datetime and calculate duration
    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
    except ValueError:
        return {"error": "Invalid datetime format. Use ISO-8601."}, 400

    if end_dt <= start_dt:
        return {"error": "end_time must be after start_time"}, 400

    duration_hours = math.ceil((end_dt - start_dt).total_seconds() / 3600)

    # 3. Select correct pricing column
    PRICE_COLUMNS = {
        1: "price_1h",
        2: "price_2h",
        3: "price_3h",
        4: "price_4h",
        5: "price_5h",
        6: "price_6h",
        7: "price_7h",
    }

    price_column = PRICE_COLUMNS.get(duration_hours, "max_daily_price")

    # 4. Database query
    conn = sqlite3.connect("parking_space_management.db")
    c = conn.cursor()

    placeholders = ",".join(["?"] * len(ids))

    query = f"""
        SELECT
            id,
            address,
            ev_charging,
            {price_column}
        FROM prices
        WHERE id IN ({placeholders})
    """

    c.execute(query, ids)
    items = c.fetchall()
    conn.close()

    # 5. Pack response data
    data = [
        {
            "id": str(item[0]),
            "fullAddress": item[1],
            "evCharging": bool(item[2]),
            "priceTotal": item[3]
        }
        for item in items
    ]

    # 6. Save JSON (unchanged behavior)
    with open("prices.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    return jsonify(data), 200

# --- NEW GET endpoint for second endpoint ---
@app.route("/api/v1/database/pricing-hour", methods=["GET"])
def get_parking_info_bulk_second():
    ids_str = request.args.get("ids")
    if not ids_str:
        return {"error": "ids parameter is required"}, 400

    # Keep same parsing style, but validate as ints for DB querying
    try:
        ids_list = [int(i.strip()) for i in ids_str.split(",") if i.strip()]
    except ValueError:
        return {"error": "ids must be comma-separated integers"}, 400

    if not ids_list:
        return {"error": "ids parameter is required"}, 400

    # Query DB for all ids at once
    conn = sqlite3.connect("parking_space_management.db")
    c = conn.cursor()

    placeholders = ",".join(["?"] * len(ids_list))
    query = f"""
        SELECT
            id,
            address,
            ev_charging,
            hourly_pricing
        FROM prices
        WHERE id IN ({placeholders})
    """

    c.execute(query, ids_list)
    rows = c.fetchall()
    conn.close()

    # Build a lookup so we can return "Parking not found" for missing ids
    row_by_id = {
        int(r[0]): {
            "id": str(r[0]),
            "fullAddress": r[1],
            "evCharging": bool(r[2]),
            "pricePerHour": r[3]
        }
        for r in rows
    }

    results = []
    for parking_id in ids_list:
        if parking_id not in row_by_id:
            results.append({"id": str(parking_id), "error": "Parking not found"})
            continue
        results.append(row_by_id[parking_id])

    # Save for debugging (keeps your shape, ids as strings like before)
    save_json(
        {"ids": [str(i) for i in ids_list], "results": results},
        "sent_from_backend_second_get.json"
    )

    return jsonify(results)