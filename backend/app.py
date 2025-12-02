from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/api/data")
def get_data():
    # This is where you would normally query the database
    return jsonify({"message": "Hello from the hidden Backend Service!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
