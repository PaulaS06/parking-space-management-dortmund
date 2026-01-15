from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime
import math
from typing import List, Dict, Any, Optional, Tuple
import os
from functools import wraps
from flask import Response
import base64


app = Flask(__name__)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "parking_space_management")

BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME")
BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD")

if not BASIC_AUTH_USERNAME or not BASIC_AUTH_PASSWORD:
    raise RuntimeError("BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD must be set")


def check_auth(auth_header: str) -> bool:
    if not auth_header or not auth_header.startswith("Basic "):
        return False

    try:
        encoded_credentials = auth_header.split(" ", 1)[1]
        decoded = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded.split(":", 1)
    except Exception:
        return False

    return (
        username == BASIC_AUTH_USERNAME
        and password == BASIC_AUTH_PASSWORD
    )


def require_basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not check_auth(auth_header):
            return Response(
                "Unauthorized",
                401,
                {"WWW-Authenticate": 'Basic realm="Login Required"'},
            )

        return f(*args, **kwargs)

    return decorated


#debug
#print("CWD:", os.getcwd())
#print("DB_PATH:", os.path.abspath(DB_PATH))
#print("DB exists:", os.path.exists(DB_PATH), "size:", os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else None)
#print("DB_PATH:", DB_PATH)
#print("DB exists:", os.path.exists(DB_PATH), "size:", os.path.getsize(DB_PATH))

#BASIC_AUTH_USERNAME = "admin"
#BASIC_AUTH_PASSWORD = "secret123"


PRICE_COLUMNS = {
    1: "price_1h",
    2: "price_2h",
    3: "price_3h",
    4: "price_4h",
    5: "price_5h",
    6: "price_6h",
    7: "price_7h",
}
DEFAULT_TOTAL_COLUMN = "max_daily_price"


# ----------------------------
# Shared helpers
# ----------------------------
def parse_ids_arg(ids_str: Optional[str]) -> Tuple[Optional[List[int]], Optional[Tuple[Dict[str, str], int]]]:
    """Parse 'ids' query param as comma-separated integers."""
    if not ids_str:
        return None, ({"error": "ids parameter is required"}, 400)

    try:
        ids_list = [int(i.strip()) for i in ids_str.split(",") if i.strip()]
    except ValueError:
        return None, ({"error": "ids must be comma-separated integers"}, 400)

    if not ids_list:
        return None, ({"error": "ids parameter is required"}, 400)

    return ids_list, None


def parse_iso_datetime(value: Optional[str], field_name: str) -> Tuple[Optional[datetime], Optional[Tuple[Dict[str, str], int]]]:
    if not value:
        return None, ({ "error": f"{field_name} is required" }, 400)
    try:
        return datetime.fromisoformat(value), None
    except ValueError:
        return None, ({"error": "Invalid datetime format. Use ISO-8601."}, 400)


def choose_total_price_column(start_dt: datetime, end_dt: datetime) -> Tuple[Optional[str], Optional[Tuple[Dict[str, str], int]]]:
    if end_dt <= start_dt:
        return None, ({"error": "end_time must be after start_time"}, 400)

    duration_hours = math.ceil((end_dt - start_dt).total_seconds() / 3600)
    return PRICE_COLUMNS.get(duration_hours, DEFAULT_TOTAL_COLUMN), None


def fetch_prices_by_ids(ids: List[int], price_column: str) -> Dict[int, Dict[str, Any]]:
    """
    Returns a dict keyed by id with common fields + the selected price column as 'price_value'.
    """
    placeholders = ",".join(["?"] * len(ids))
    query = f"""
        SELECT
            id,
            address,
            ev_charging,
            {price_column} AS price_value
        FROM prices
        WHERE id IN ({placeholders})
    """

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(query, ids)
        rows = c.fetchall()

    # Map to a stable internal shape; endpoints can rename price_value as needed.
    return {
        int(r[0]): {
            "id": str(r[0]),
            "fullAddress": r[1],
            "evCharging": bool(r[2]),
            "price_value": r[3],
        }
        for r in rows
    }


def save_json(payload: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)


# ----------------------------
# Endpoint 1: pricing-total
# ----------------------------
@app.route("/api/v1/database/pricing-total", methods=["GET"])
@require_basic_auth
def get_pricing_total():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    ids_str = request.args.get("ids")

    ids, err = parse_ids_arg(ids_str)
    if err:
        return err

    start_dt, err = parse_iso_datetime(start_time, "start_time")
    if err:
        return err
    end_dt, err = parse_iso_datetime(end_time, "end_time")
    if err:
        return err

    price_column, err = choose_total_price_column(start_dt, end_dt)
    if err:
        return err

    rows_by_id = fetch_prices_by_ids(ids, price_column)

    # You previously returned only found items (no "not found" placeholders) — keep that behavior.
    data = []
    for _id in ids:
        row = rows_by_id.get(_id)
        if not row:
            continue
        data.append({
            "id": row["id"],
            "fullAddress": row["fullAddress"],
            "evCharging": row["evCharging"],
            "priceTotal": row["price_value"],
        })

    # Keep your "write file" behavior
    save_json(data, "prices.json")

    return jsonify(data), 200


# ----------------------------
# Endpoint 2: pricing-hour
# ----------------------------
@app.route("/api/v1/database/pricing-hour", methods=["GET"])
@require_basic_auth
def get_pricing_hour():
    ids_str = request.args.get("ids")

    ids, err = parse_ids_arg(ids_str)
    if err:
        return err

    rows_by_id = fetch_prices_by_ids(ids, "hourly_pricing")

    # You want explicit "Parking not found" entries for missing IDs — keep that behavior.
    results = []
    for _id in ids:
        row = rows_by_id.get(_id)
        if not row:
            results.append({"id": str(_id), "error": "Parking not found"})
            continue

        results.append({
            "id": row["id"],
            "fullAddress": row["fullAddress"],
            "evCharging": row["evCharging"],
            "pricePerHour": row["price_value"],
        })

    # Keep your debug file behavior
    save_json(
        {"ids": [str(i) for i in ids], "results": results},
        "sent_from_backend_second_get.json",
    )

    return jsonify(results), 200

if __name__ == "__main__":
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=5001, debug=debug_mode)