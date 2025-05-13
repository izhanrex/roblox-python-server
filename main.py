from flask import Flask, request, jsonify, render_template_string, redirect
from datetime import datetime
import os

app = Flask(__name__)
messages = {}  # player name → list of messages

# HTML template: no username field
html_form = """
<!DOCTYPE html>
<html>
<head>
    <title>Broadcast to All Roblox Players</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f4f4; padding: 20px; }
        form { background: white; padding: 20px; max-width: 400px; margin: auto; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        textarea, button { width: 100%; margin-top: 10px; padding: 10px; font-size: 16px; }
        button { background: #007bff; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <form method="POST">
        <h2>Broadcast Message to All Players</h2>
        <textarea name="text" placeholder="Type your message here..." required></textarea>
        <button type="submit">Send</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return "Server is up and running!"

@app.route("/", methods=["POST"])
def message():
    data = request.json
    command = data.get("command", "")
    player = data.get("player", "")
    payload = data.get("payload", {})

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
        # Get player-specific messages
        player_msgs = messages.get(player, [])
        messages[player] = []

        # Get broadcast messages
        broadcast_msgs = messages.get("__broadcast__", [])
        messages["__broadcast__"] = []

        reply = broadcast_msgs + player_msgs
    else:
        reply = f"Unknown command: {command}"

    return jsonify({"reply": reply})

@app.route("/send", methods=["GET"])
def show_send_form():
    return render_template_string(html_form)

@app.route("/send", methods=["POST"])
def handle_send_form():
    text = request.form.get("text")
    if text:
        messages.setdefault("__broadcast__", []).append(text)
        print(f"📢 Broadcast message: {text}")
        return redirect("/send")
    return "Missing message!", 400

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
