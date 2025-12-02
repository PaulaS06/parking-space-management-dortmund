from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route("/")
def home():
    try:
        response = requests.get("http://backend:8000/api/data")
        data = response.json()
        message = data.get("message")
    except Exception as e:
        message = f"Error: Backend is offline. ({e})"

    return f"<h1>Frontend UI</h1><p>Message from Backend: {message}</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
