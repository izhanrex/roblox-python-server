from flask import Flask, request, jsonify, render_template_string, redirect
from datetime import datetime
import threading
import requests
import time
import os

# === DISCORD CONFIG ===
USER_TOKEN = os.getenv("DISCORD_USER_TOKEN")  # Set in Railway env vars
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
POLL_INTERVAL = 0.1
HEADERS = {
    'Authorization': USER_TOKEN,
    'User-Agent': 'Mozilla/5.0',
}

# === FLASK SETUP ===
app = Flask(__name__)
messages = {}  # player name → list of messages

# === DISCORD POLLING ===
def get_latest_message_id(channel_id):
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=1'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        messages = response.json()
        if messages:
            return messages[0]['id']
    print(f"Failed to get latest message: {response.status_code} {response.text}")
    return None

def get_new_messages(channel_id, after_message_id):
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
    params = {'limit': 50, 'after': after_message_id}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json() if response.status_code == 200 else []

def discord_polling_loop():
    print("🟢 Discord polling started...")
    last_seen_id = get_latest_message_id(CHANNEL_ID)
    if not last_seen_id:
        print("⚠️ Failed to fetch starting message ID.")
        return
    while True:
        try:
            new_msgs = get_new_messages(CHANNEL_ID, last_seen_id)
            if new_msgs:
                for msg in reversed(new_msgs):
                    author = msg['author']['username']
                    content = msg['content']
                    full = f"{author}: {content}"
                    print("📩 New Discord message:", full)
                    messages.setdefault("__broadcast__", []).append(full)
                    last_seen_id = msg['id']
        except Exception as e:
            print("❌ Exception during Discord polling:", e)
        time.sleep(POLL_INTERVAL)

# === HTML FORM ===
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

# === FLASK ROUTES ===
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
        messages[player] = []

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

# === START SERVER AND THREAD ===
if __name__ == "__main__":
    threading.Thread(target=discord_polling_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
