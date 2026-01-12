# standardized Python DBI API used to integrate the SQLite database
from flask import Flask, request, jsonify
import sqlite3
import json

@app.route("/api/v1/database/pricing-total", methods=["GET"])
def get_parking_info_bulk_get():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    ids_str = request.args.get("ids")

    # 1. Validate input
    if not start_time or not end_time or not ids_str:
        return {"error": "start_time, end_time and ids are required"}, 400

    ids = [int(i.strip()) for i in ids_str.split(",")]

    #conn = sqlite3.connect(':memory:') # for a temporary db
    conn = sqlite3.connect('parking_space_management')

    #Create a cursor
    c = conn.cursor()

    #ids_to_query = (103824, 107380, 107394, 49249524, 553203)  # example IDs

    placeholders = ",".join(["?"] * len(ids))

    query = f"""
        SELECT
            id,
            address,
            ev_charging,
            hourly_pricing
        FROM prices
        WHERE id IN ({placeholders})
    """

    #c.fetchone()
    #c.fetchmany(3)
    #print(c.fetchall)

    c.execute(query, ids)
    items = c.fetchall()

    # Pack data into a list (API-compatible structure)
    data = []

    for item in items:
        data.append({
            "id": str(item[0]),
            "fullAddress": item[1],
            "evCharging": bool(item[2]),
            "priceTotal": item[3]
        })

    # Save JSON
    with open("prices.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    #commit commands
    conn.commit()

    # close connection
    conn.close()
    return jsonify(data), 200