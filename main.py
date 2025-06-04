from flask import Flask, request, jsonify, render_template_string, redirect
from datetime import datetime
import os
import requests

app = Flask(__name__)
messages = {}  # player name → list of messages

RAILWAY_URL = "https://web-production-5c44.up.railway.app"  # Change this!

# HTML template for /send form (unchanged)
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

def send_message_to_send_endpoint(text):
    try:
        resp = requests.post(f"{RAILWAY_URL}/send", json={"text": text})
        resp.raise_for_status()
        print(f"✅ Sent message to /send: {text[:60]}{'...' if len(text) > 60 else ''}")
    except Exception as e:
        print(f"❌ Failed to send message to /send: {e}")

# --- Reddit functions here ---
# Put your Reddit scraping helper functions here or import them as needed
# For brevity, minimal example stubs here:

def search_subreddits(query):
    # Your real scraping logic goes here
    # Return list of dicts with 'name' and 'subscribers' keys
    # For example purposes, dummy data:
    return [
        {"name": "python", "subscribers": 1000000},
        {"name": "learnpython", "subscribers": 500000},
    ]

def fetch_subreddit_posts(subreddit):
    # Return list of posts with 'title', 'score', 'permalink'
    return [
        {"title": f"Example Post 1 from r/{subreddit}", "score": 123, "permalink": "/r/python/post1"},
        {"title": f"Example Post 2 from r/{subreddit}", "score": 456, "permalink": "/r/python/post2"},
    ]

def fetch_post_comments(permalink):
    # Return list of comments with 'author' and 'body'
    return [
        {"author": "user1", "body": "Great post!"},
        {"author": "user2", "body": "Thanks for sharing."},
    ]

@app.route("/", methods=["GET"])
def index():
    return "Server is up and running!"

@app.route("/", methods=["POST"])
def message():
    try:
        data = request.json
        command = data.get("command", "")
        player = data.get("player", "")
        payload = data.get("payload", {})

        # Handle your commands here
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

        # --- Reddit Commands ---

        elif command == "redditSearch":
            query = payload.get("query", "").strip()
            if not query:
                return jsonify({"reply": "Query is empty."})
            results = search_subreddits(query)
            if not results:
                reply = ["No subreddits found."]
            else:
                reply = [{"name": r["name"], "subscribers": r["subscribers"]} for r in results]

            # Send message to /send endpoint for debugging
            msg_text = f"🔍 Subreddit search for '{query}':\n"
            for r in results:
                msg_text += f"- r/{r['name']} ({r['subscribers']} subs)\n"
            send_message_to_send_endpoint(msg_text)

        elif command == "redditPosts":
            subreddit = payload.get("subreddit", "").strip()
            if not subreddit:
                return jsonify({"reply": "Subreddit is empty."})
            posts = fetch_subreddit_posts(subreddit)
            if not posts:
                reply = ["No posts found."]
            else:
                reply = [{"title": p["title"], "score": p["score"], "permalink": p["permalink"]} for p in posts]

            # Send message to /send endpoint for debugging
            msg_text = f"🔥 Posts from r/{subreddit}:\n"
            for p in posts:
                msg_text += f"- {p['title']} [{p['score']} pts]\n"
            send_message_to_send_endpoint(msg_text)

        elif command == "redditComments":
            permalink = payload.get("permalink", "").strip()
            if not permalink:
                return jsonify({"reply": "Permalink is empty."})
            comments = fetch_post_comments(permalink)
            if not comments:
                reply = ["No comments found."]
            else:
                reply = [{"author": c["author"], "body": c["body"]} for c in comments]

            # Send message to /send endpoint for debugging
            msg_text = f"💬 Comments for {permalink}:\n"
            for c in comments:
                msg_text += f"- u/{c['author']}: {c['body']}\n"
            send_message_to_send_endpoint(msg_text)

        else:
            reply = f"Unknown command: {command}"

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"❌ Exception in / POST: {e}")
        return jsonify({"reply": f"Server error: {str(e)}"}), 500

@app.route("/send", methods=["GET"])
def show_send_form():
    return render_template_string(html_form)

@app.route("/send", methods=["POST"])
def handle_send_form():
    # Supports both form POST and JSON POST for /send
    if request.is_json:
        data = request.get_json()
        text = data.get("text", "")
    else:
        text = request.form.get("text", "")

    if text:
        messages.setdefault("__broadcast__", []).append(text)
        print(f"📢 Broadcast message: {text}")
        return jsonify({"status": "ok", "message": "Broadcast stored."})
    else:
        return jsonify({"status": "error", "message": "Missing message text."}), 400

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
