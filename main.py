from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Server is up and running!"

@app.route("/", methods=["POST"])
def message():
    data = request.json

    command = data.get("command", "")
    player = data.get("player", "")
    payload = data.get("payload", {})

    print(f"[{player}] Command: {command} | Payload: {payload}")

    if command == "greet":
        reply = f"Hello, {player}!"
    elif command == "getTime":
        reply = f"Current server time: {datetime.now().isoformat()}"
    elif command == "echo":
        reply = f"Echo: {payload.get('text', '')}"
    else:
        reply = f"Unknown command: {command}"

    return jsonify({"reply": reply})
