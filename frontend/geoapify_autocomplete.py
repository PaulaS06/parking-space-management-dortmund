from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GEOAPIFY_API_KEY = "DEIN_API_KEY_HIER"



if __name__ == "__main__":
    app.run(debug=True)
