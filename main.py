from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "RailwayRedditReader/1.1 by OpenAI"
}

def search_subreddits(query):
    url = f"https://www.reddit.com/subreddits/search.json?q={query}&limit=10"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        children = response.json()["data"]["children"]
        # Extract minimal info for Roblox
        return [{
            "name": c["data"]["display_name"],
            "title": c["data"].get("title", ""),
            "subscribers": c["data"].get("subscribers", 0)
        } for c in children]
    except Exception as e:
        print(f"[!] Failed to search subreddits: {e}")
        return []

def fetch_subreddit_posts(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=15"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        children = response.json()["data"]["children"]
        # Extract minimal info for Roblox
        return [{
            "title": c["data"]["title"],
            "score": c["data"]["score"],
            "permalink": c["data"]["permalink"]
        } for c in children]
    except Exception as e:
        print(f"[!] Failed to fetch subreddit posts: {e}")
        return []

def fetch_post_comments(permalink):
    url = f"https://www.reddit.com{permalink}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        # Extract top comments excluding AutoModerator
        comments_raw = json_data[1]["data"]["children"]
        comments = []
        for c in comments_raw:
            if c["kind"] == "t1":
                data = c["data"]
                if data.get("author") != "AutoModerator" and data.get("body"):
                    comments.append({
                        "author": data.get("author"),
                        "body": data.get("body")
                    })
                    if len(comments) >= 10:
                        break
        return comments
    except Exception as e:
        print(f"[!] Failed to fetch comments: {e}")
        return []

@app.route("/", methods=["POST"])
def handle_command():
    try:
        data = request.get_json(force=True)
        command = data.get("command")
        payload = data.get("payload", {})

        if command == "redditSearch":
            query = payload.get("query", "")
            if not query:
                return jsonify({"error": "No query provided"}), 400
            result = search_subreddits(query)
            return jsonify({"reply": result})

        elif command == "redditPosts":
            subreddit = payload.get("subreddit", "")
            if not subreddit:
                return jsonify({"error": "No subreddit provided"}), 400
            result = fetch_subreddit_posts(subreddit)
            return jsonify({"reply": result})

        elif command == "redditComments":
            permalink = payload.get("permalink", "")
            if not permalink:
                return jsonify({"error": "No permalink provided"}), 400
            result = fetch_post_comments(permalink)
            return jsonify({"reply": result})

        else:
            return jsonify({"error": "Unknown command"}), 400

    except Exception as e:
        print(f"[!] Exception in handle_command: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
