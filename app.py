from flask import Flask, request, render_template_string
import json
import os
import time

app = Flask(__name__)

# --- CORE DSA: LOAD INVERTED INDEX ---
# We load the data structure into RAM once.
# This makes searching O(1) - Instant.
INDEX_FILE = "inverted_index.json"
inverted_index = {}

if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
    print(f"✅ Loaded {len(inverted_index)} keywords into Hash Map.")
else:
    print("⚠️ Index file missing. Search will be empty.")

# --- UI TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OnGo. | Internal Search</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root { --bg-body: #0D1B2A; --bg-card: rgba(27, 38, 59, 0.6); --text-main: #E0E1DD; --text-muted: #AAB3C0; --accent: #B3AF8F; --border: rgba(255, 255, 255, 0.05); --font: 'Quicksand', sans-serif; }
        * { box-sizing: border-box; }
        body { background-color: var(--bg-body); color: var(--text-main); font-family: var(--font); margin: 0; display: flex; flex-direction: column; align-items: center; padding-top: 60px; min-height: 100vh; }
        
        h1 { font-size: 3.5rem; margin: 0 0 30px 0; font-weight: 700; letter-spacing: -1px; }
        .logo-link { text-decoration: none; color: var(--text-main); }
        .logo-link span { color: var(--accent); }

        .container { width: 90%; max-width: 700px; display: flex; flex-direction: column; align-items: center; }
        .search-wrapper { background: rgba(255, 255, 255, 0.08); padding: 6px 15px 6px 6px; border-radius: 50px; display: flex; align-items: center; width: 100%; border: 1px solid var(--border); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        input { background: transparent; border: none; color: var(--text-main); font-size: 1.1rem; padding: 14px 15px; width: 100%; font-family: var(--font); font-weight: 500; outline: none; }
        .search-btn { background-color: var(--accent); color: #0D1B2A; border: none; border-radius: 40px; padding: 12px 28px; font-weight: 700; font-size: 1rem; cursor: pointer; transition: transform 0.2s; }
        .search-btn:hover { transform: scale(1.05); }

        .results-container { width: 100%; margin-top: 30px; text-align: left; }
        .stat-line { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        
        .card { background: var(--bg-card); padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid var(--border); transition: transform 0.2s; }
        .card:hover { transform: translateY(-3px); border-color: var(--accent); }
        .card a { color: var(--text-main); font-weight: 700; text-decoration: none; font-size: 1.2rem; display: block; margin-bottom: 5px; }
        .card .url { color: var(--accent); font-size: 0.85rem; font-family: monospace; opacity: 0.8; }

        .empty-state { text-align: center; margin-top: 50px; color: var(--text-muted); }
        .empty-state span { display: block; margin-top: 10px; color: var(--accent); }
    </style>
</head>
<body>
    <div class="container">
        <h1><a href="/" class="logo-link">On<span>Go.</span></a></h1>
        <form action="/search" method="get" style="width: 100%;">
            <div class="search-wrapper">
                <input type="text" name="q" placeholder="Search internal database..." required value="{{ query if query else '' }}" autocomplete="off">
                <button type="submit" class="search-btn">Search</button>
            </div>
        </form>

        <div class="results-container">
            {% if query %}
                <div class="stat-line">
                    {% if results %}
                        Found {{ results|length }} result(s) in {{ time }}ms
                    {% else %}
                        No results found in {{ time }}ms
                    {% endif %}
                </div>

                {% for url in results %}
                    <div class="card">
                        <a href="{{ url }}" target="_blank">{{ url }}</a>
                        <div class="url">INTERNAL DATABASE MATCH</div>
                    </div>
                {% endfor %}

                {% if not results %}
                    <div class="empty-state">
                        <p>No matches found for "<b>{{ query }}</b>" in your inverted index.</p>
                        <span>Try searching for: python, dsa, flask, ganesh</span>
                    </div>
                {% endif %}
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower().strip()
    start_time = time.time()
    
    # PURE DSA LOGIC: O(1) Lookup
    # No APIs. No requests. Just a dictionary check.
    results = inverted_index.get(query, [])
    
    duration = round((time.time() - start_time) * 1000, 4)
    return render_template_string(HTML_TEMPLATE, query=query, results=results, time=duration)

if __name__ == '__main__':
    app.run(debug=True)