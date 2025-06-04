from flask import Flask, request, jsonify, render_template_string, redirect
from datetime import datetime
import os

app = Flask(__name__)
messages = {}  # Temporary store for each player

# HTML form template
html_form = """
<!DOCTYPE html>
<html>
<head>
    <title>Send Message to Roblox</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f4f4; padding: 20px; }
        form { background: white; padding: 20px; max-width: 400px; margin: auto; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input, textarea, button { width: 100%; margin-top: 10px; padding: 10px; font-size: 16px; }
        button { background: #007bff; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <form method="POST">
        <h2>Send Message to Roblox Player</h2>
        <input type="text" name="player" placeholder="Player Name" required>
        <textarea name="text" placeholder="Message..." required></textarea>
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
        player_msgs = messages.get(player, [])
        messages[player] = []  # Clear messages after sending
        reply = player_msgs
    else:
        reply = f"Unknown command: {command}"

    return jsonify({"reply": reply})

# Serve HTML form at /send
@app.route("/send", methods=["GET"])
def show_send_form():
    return render_template_string(html_form)

# Handle form submission
@app.route("/send", methods=["POST"])
def handle_send_form():
    player = request.form.get("player")
    text = request.form.get("text")

    if player and text:
        messages.setdefault(player, []).append(text)
        print(f"📨 Stored message for {player}: {text}")
        return redirect("/send")  # Redirect back to the form

    return "Missing player or message!", 400

# Start server
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
