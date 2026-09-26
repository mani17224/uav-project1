from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

from detector import detect
from live_detector import start_live_detector, get_state
import numpy as np

app = Flask(__name__)

PROCESSED_DIR = __import__("pathlib").Path(__file__).resolve().parent.parent / "processed_data"
CORS(app)

# Start PX4 live AI detector in background
start_live_detector()


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "status": "online",
        "model": "Transformer + Mahalanobis",
        "threshold": detect.__globals__["threshold"]
    })


@app.route("/api/live")
def live():
    return jsonify(get_state())


@app.route("/api/test-window")
def test_window():
    data = np.load(PROCESSED_DIR / "uav_windows_ml.npz")
    return jsonify({"window": data["X"][0].tolist()})


@app.route("/api/detect", methods=["POST"])
def api_detect():
    try:
        data = request.get_json()

        if not data or "window" not in data:
            return jsonify({
                "error": "Missing 'window' data"
            }), 400

        result = detect(data["window"])

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
