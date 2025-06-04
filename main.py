from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Sample messages you can update dynamically
sample_messages = [
    "Welcome to the game, player!",
    "Double XP weekend is active!",
    "Don't forget to join our community group!"
]

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

    # Handle commands and update the messages
    if command == "greet":
        reply = f"Hello, {player}!"
    elif command == "getTime":
        reply = f"Current server time: {datetime.now().isoformat()}"
    elif command == "echo":
        reply = f"Echo: {payload.get('text', '')}"
    else:
        reply = f"Unknown command: {command}"

    # Example: sending a list of server messages to Roblox
    # You can modify these messages dynamically based on game events
    return jsonify(sample_messages)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
