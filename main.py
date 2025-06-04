from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Configure logging to console with timestamp
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/', methods=['POST'])
def handle_request():
    data = request.get_json()
    app.logger.debug(f"Received request data: {data}")

    command = data.get("command")
    payload = data.get("payload", {})

    try:
        if command == "redditSearch":
            query = payload.get("query", "")
            app.logger.debug(f"Searching subreddits for: {query}")
            # Call your existing Reddit scraping function here, e.g. search_subreddits(query)
            results = search_subreddits(query)
            app.logger.debug(f"Search results: {results}")
            return jsonify({"reply": results})

        elif command == "redditPosts":
            subreddit = payload.get("subreddit", "")
            app.logger.debug(f"Fetching posts for subreddit: {subreddit}")
            results = fetch_subreddit_posts(subreddit)
            app.logger.debug(f"Posts fetched: {results}")
            return jsonify({"reply": results})

        elif command == "redditComments":
            permalink = payload.get("permalink", "")
            app.logger.debug(f"Fetching comments for permalink: {permalink}")
            results = fetch_post_comments(permalink)
            app.logger.debug(f"Comments fetched: {results}")
            return jsonify({"reply": results})

        else:
            app.logger.warning(f"Unknown command received: {command}")
            return jsonify({"reply": "Unknown command"}), 400
    except Exception as e:
        app.logger.error(f"Exception during handling command {command}: {e}")
        return jsonify({"reply": f"Error: {str(e)}"}), 500

# Example placeholder functions (replace with your actual scraping implementations)
def search_subreddits(query):
    # Your scraping logic here
    return [{"name": "exampleSubreddit", "subscribers": 12345}]

def fetch_subreddit_posts(subreddit):
    # Your scraping logic here
    return [{"title": "Example Post", "score": 100, "permalink": "/r/example/comments/1"}]

def fetch_post_comments(permalink):
    # Your scraping logic here
    return [{"author": "user123", "body": "Example comment"}]

if __name__ == '__main__':
    app.run()
