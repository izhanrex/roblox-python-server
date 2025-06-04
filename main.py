from flask import Flask, request, render_template_string, redirect, url_for
import requests
import textwrap

app = Flask(__name__)

WRAP_WIDTH = 80
MAX_COMMENTS = 5

HEADERS = {
    "User-Agent": "RailwayRedditReader/1.1 by OpenAI"
}

def wrap(text):
    return "<br>".join(textwrap.wrap(text, WRAP_WIDTH))

def search_subreddits(query):
    url = f"https://www.reddit.com/subreddits/search.json?q={query}&limit=10"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()["data"]["children"]
    except Exception as e:
        print(f"[!] Failed to search subreddits: {e}")
        return []

def fetch_subreddit_posts(subreddit, sort="hot"):
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit=15"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()["data"]["children"]
    except Exception as e:
        print(f"[!] Failed to fetch subreddit posts: {e}")
        return []

def fetch_post_json(permalink):
    url = f"https://www.reddit.com{permalink}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[!] Failed to load post: {e}")
        return None

@app.route("/send", methods=["GET", "POST"])
def send():
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if not query:
            return render_template_string(SEND_FORM, error="Please enter a search query.")
        return redirect(url_for("subreddits", query=query))
    return render_template_string(SEND_FORM)

@app.route("/subreddits")
def subreddits():
    query = request.args.get("query", "")
    results = search_subreddits(query)
    return render_template_string(SUBREDDITS_PAGE, query=query, results=results)

@app.route("/posts/<subreddit>")
def posts(subreddit):
    posts = fetch_subreddit_posts(subreddit)
    return render_template_string(POSTS_PAGE, subreddit=subreddit, posts=posts)

@app.route("/comments/<path:permalink>")
def comments(permalink):
    # permalink comes URL-encoded, decode it
    import urllib.parse
    permalink = "/" + urllib.parse.unquote(permalink)
    post_json = fetch_post_json(permalink)
    if not post_json:
        return "Failed to load post.", 500
    return render_template_string(COMMENTS_PAGE, post_json=post_json, max_comments=MAX_COMMENTS)

SEND_FORM = """
<!doctype html>
<title>Reddit Search</title>
<h1>Search Subreddits</h1>
<form method="post">
  <input type="text" name="query" placeholder="Enter subreddit search query" size="40" autofocus>
  <input type="submit" value="Search">
</form>
{% if error %}
<p style="color:red;">{{ error }}</p>
{% endif %}
"""

SUBREDDITS_PAGE = """
<!doctype html>
<title>Subreddits for "{{ query }}"</title>
<h1>Subreddits matching '{{ query }}'</h1>
<ul>
  {% for item in results %}
    <li><a href="{{ url_for('posts', subreddit=item['data']['display_name']) }}">r/{{ item['data']['display_name'] }}</a>
        ({{ item['data'].get('subscribers',0) }} subs) - {{ item['data'].get('title','') }}</li>
  {% else %}
    <li>No results found.</li>
  {% endfor %}
</ul>
<p><a href="{{ url_for('send') }}">Back to Search</a></p>
"""

POSTS_PAGE = """
<!doctype html>
<title>Posts in r/{{ subreddit }}</title>
<h1>Posts in r/{{ subreddit }}</h1>
<ul>
  {% for post in posts %}
    <li><a href="{{ url_for('comments', permalink=post['data']['permalink'].lstrip('/')) }}">{{ post['data']['title'] }}</a> [{{ post['data']['score'] }} pts]</li>
  {% else %}
    <li>No posts found.</li>
  {% endfor %}
</ul>
<p><a href="{{ url_for('subreddits', query=subreddit) }}">Back to Subreddits</a></p>
<p><a href="{{ url_for('send') }}">Back to Search</a></p>
"""

COMMENTS_PAGE = """
<!doctype html>
<title>Comments</title>
<h1>{{ post_json[0]['data']['children'][0]['data']['title'] }}</h1>
<p>
  {% if post_json[0]['data']['children'][0]['data'].get('selftext') %}
    {{ post_json[0]['data']['children'][0]['data']['selftext'] | nl2br }}
  {% else %}
    <a href="{{ post_json[0]['data']['children'][0]['data']['url'] }}">{{ post_json[0]['data']['children'][0]['data']['url'] }}</a>
  {% endif %}
</p>
<h2>Top Comments (excluding AutoModerator):</h2>
<ul>
  {% set count = 0 %}
  {% for comment in post_json[1]['data']['children'] %}
    {% if count >= max_comments %}
      {% break %}
    {% endif %}
    {% if comment['kind'] == 't1' and comment['data']['author'] != 'AutoModerator' and comment['data'].get('body') %}
      <li><strong>u/{{ comment['data']['author'] }}</strong>:<br>{{ comment['data']['body'] | nl2br }}</li>
      {% set count = count + 1 %}
    {% endif %}
  {% endfor %}
  {% if count == 0 %}
    <li>No valid comments found.</li>
  {% endif %}
</ul>
<p><a href="{{ url_for('posts', subreddit=post_json[0]['data']['children'][0]['data']['subreddit']) }}">Back to Posts</a></p>
<p><a href="{{ url_for('send') }}">Back to Search</a></p>
"""

# Jinja filter for nl2br
@app.template_filter('nl2br')
def nl2br_filter(s):
    return s.replace('\n', '<br>\n')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
