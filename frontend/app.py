from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('window1.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
