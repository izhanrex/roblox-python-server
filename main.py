from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)
messages = {}  # Temporary in-memory store

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
    elif command == "sendMessage":
        msg = payload.get("text", "")
        messages.setdefault(player, []).append(msg)
        reply = f"Message stored for {player}"
    elif command == "getMessages":
        player_msgs = messages.get(player, [])
        messages[player] = []  # Clear after sending
        reply = player_msgs
    else:
        reply = f"Unknown command: {command}"

    return jsonify({"reply": reply})

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
