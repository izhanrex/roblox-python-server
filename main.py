from flask import Flask, request, jsonify
from datetime import datetime
import requests
import textwrap
import os

app = Flask(__name__)
messages = {}  # player name → list of messages

WRAP_WIDTH = 80
MAX_COMMENTS = 5
HEADERS = {
    "User-Agent": "TerminalRedditReader/1.1 by OpenAI"
}

def wrap(text):
    return "\n".join(textwrap.wrap(text, WRAP_WIDTH))

def search_subreddits(query):
    url = f"https://www.reddit.com/subreddits/search.json?q={query}&limit=10"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return [f"r/{item['data']['display_name']}: {item['data'].get('title', '')}" for item in response.json()["data"]["children"]]
    except Exception as e:
        return [f"[Reddit search error] {e}"]

def fetch_subreddit_posts(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=5"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        posts = response.json()["data"]["children"]
        return [f"{p['data']['title']} ({p['data']['score']} pts)" for p in posts]
    except Exception as e:
        return [f"[Failed to fetch posts] {e}"]

def fetch_post_comments(permalink):
    url = f"https://www.reddit.com{permalink}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()[1]["data"]["children"]
        comments = []
        for c in data:
            if c["kind"] != "t1":
                continue
            author = c["data"].get("author")
            body = c["data"].get("body")
            if author and body:
                comments.append(f"u/{author}: {wrap(body)}")
            if len(comments) >= MAX_COMMENTS:
                break
        return comments if comments else ["[No valid comments found]"]
    except Exception as e:
        return [f"[Failed to load comments] {e}"]

@app.route("/", methods=["POST"])
def message():
    data = request.json
    command = data.get("command", "")
    player = data.get("player", "")
    payload = data.get("payload", {})

    if command == "redditSearch":
        query = payload.get("query", "")
        result = search_subreddits(query)
    elif command == "redditPosts":
        subreddit = payload.get("subreddit", "")
        result = fetch_subreddit_posts(subreddit)
    elif command == "redditComments":
        permalink = payload.get("permalink", "")
        result = fetch_post_comments(permalink)
    else:
        result = [f"Unknown command: {command}"]

    messages.setdefault(player, []).extend(result)
    return jsonify({"reply": result})

@app.route("/", methods=["GET"])
def health():
    return "Server running"

@app.route("/getMessages", methods=["POST"])
def get_messages():
    data = request.json
    player = data.get("player", "")
    player_msgs = messages.get(player, [])
    messages[player] = []
    return jsonify({"messages": player_msgs})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
