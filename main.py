from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Shared server-wide message (global)
latest_message = None

@app.route("/", methods=["GET"])
def index():
    return "Server is up and running!"

@app.route("/broadcast", methods=["POST"])
def broadcast():
    global latest_message
    data = request.json
    message = data.get("message", "").strip()

    if message:
        latest_message = message
        print(f"[Broadcast] New message: {latest_message}")
        return jsonify({"status": "ok", "message": latest_message})
    else:
        return jsonify({"status": "error", "message": "Empty message"}), 400

@app.route("/get_broadcast", methods=["POST"])
def get_broadcast():
    global latest_message
    if latest_message:
        msg = latest_message
        latest_message = None  # clear after sending once
        return jsonify({"message": msg})
    else:
        return jsonify({"message": None})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
