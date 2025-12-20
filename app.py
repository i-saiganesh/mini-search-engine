from flask import Flask, request, render_template_string
import json
import os
import time

app = Flask(__name__)

# --- THE DATA STRUCTURE ---
# We load the Inverted Index into RAM when the server starts.
# This is a Hash Map where:
#   Key   = Keyword (e.g., "python")
#   Value = List of URLs (e.g., ["https://python.org", "https://realpython.com"])
INDEX_FILE = "inverted_index.json"
inverted_index = {}

if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
    print(f"✅ Loaded Index with {len(inverted_index)} keywords.")
else:
    print("⚠️ Warning: inverted_index.json not found. Search will be empty.")
    # Fallback dummy data so you can test it immediately
    inverted_index = {
        "python": ["https://www.python.org/", "https://realpython.com/"],
        "dsa": ["https://www.geeksforgeeks.org/data-structures/", "https://leetcode.com/"],
        "flask": ["https://flask.palletsprojects.com/", "https://blog.miguelgrinberg.com/"],
        "search": ["https://en.wikipedia.org/wiki/Search_engine", "https://www.google.com/"]
    }

# --- THE UI TEMPLATE ---
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
        body { background-color: var(--bg-body); color: var(--text-main); font-family: var(--font); margin: 0; display: flex; flex-direction: column; align-items: center; padding-top: 80px; min-height: 100vh; }
        
        h1 { font-size: 4rem; margin: 0 0 40px 0; font-weight: 700; letter-spacing: -2px; }
        h1 span { color: var(--accent); }
        a { text-decoration: none; color: inherit; }

        .search-container { width: 100%; max-width: 700px; position: relative; }
        input { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid var(--border); padding: 18px 25px; border-radius: 50px; color: #fff; font-size: 1.2rem; font-family: var(--font); outline: none; transition: all 0.3s; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
        input:focus { background: rgba(255,255,255,0.1); border-color: var(--accent); box-shadow: 0 0 0 4px rgba(179, 175, 143, 0.1); }
        
        .stats { margin: 20px 0 30px; color: var(--text-muted); font-size: 0.9rem; text-align: left; width: 100%; max-width: 700px; padding-left: 15px; }

        .results { width: 100%; max-width: 700px; display: flex; flex-direction: column; gap: 15px; }
        .card { background: var(--bg-card); padding: 20px 25px; border-radius: 16px; border: 1px solid var(--border); transition: transform 0.2s; }
        .card:hover { transform: translateY(-3px); border-color: var(--accent); }
        .card-title { color: var(--accent); font-size: 1.3rem; font-weight: 700; margin-bottom: 5px; display: block; }
        .card-link { color: var(--text-muted); font-size: 0.9rem; word-break: break-all; }
        
        .empty-state { text-align: center; color: var(--text-muted); margin-top: 50px; }
    </style>
</head>
<body>
    <h1><a href="/">On<span>Go.</span></a></h1>
    
    <div class="search-container">
        <form action="/search" method="get">
            <input type="text" name="q" placeholder="Search internal database..." value="{{ query if query else '' }}" autofocus autocomplete="off">
        </form>
    </div>

    {% if query %}
        <div class="stats">
            Found {{ results|length }} result(s) in {{ time }} ms
        </div>
        <div class="results">
            {% for url in results %}
                <div class="card">
                    <a href="{{ url }}" target="_blank" class="card-title">{{ url }}</a>
                    <div class="card-link">Internal Index Match</div>
                </div>
            {% endfor %}
            
            {% if not results %}
                <div class="empty-state">
                    <p>No matches found in the Inverted Index.</p>
                    <p style="font-size: 0.8rem; margin-top: 10px;">(Try searching for "python", "dsa", or run your crawler to populate the index)</p>
                </div>
            {% endif %}
        </div>
    {% endif %}
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
    results = []

    # --- CORE SEARCH LOGIC (O(1) Lookup) ---
    if query:
        # Direct Hash Map Lookup
        # This is the fastest possible search algorithm
        results = inverted_index.get(query, [])

    duration = round((time.time() - start_time) * 1000, 3) # Measured in microseconds
    return render_template_string(HTML_TEMPLATE, query=query, results=results, time=duration)

if __name__ == '__main__':
    app.run(debug=True)