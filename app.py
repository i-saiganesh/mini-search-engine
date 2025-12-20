from flask import Flask, request, render_template_string
import json
import os
import time

app = Flask(__name__)

# --- 1. INTERNAL DATABASE (Fast O(1) Lookup) ---
INDEX_FILE = "inverted_index.json"
inverted_index = {}

if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
else:
    # Backup data in case file is missing
    inverted_index = {
        "python": ["https://www.python.org/", "https://realpython.com/"],
        "dsa": ["https://www.geeksforgeeks.org/data-structures/"],
        "ongo": ["https://github.com/i-saiganesh/ongo-search-engine"]
    }

# --- 2. UI TEMPLATE (Dark Mode + Google Widget) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OnGo. | Hybrid Search</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root { --bg-body: #0D1B2A; --bg-card: rgba(27, 38, 59, 0.6); --text-main: #E0E1DD; --text-muted: #AAB3C0; --accent: #B3AF8F; --border: rgba(255, 255, 255, 0.05); --font: 'Quicksand', sans-serif; }
        * { box-sizing: border-box; }
        body { background-color: var(--bg-body); color: var(--text-main); font-family: var(--font); margin: 0; display: flex; flex-direction: column; align-items: center; padding-top: 40px; min-height: 100vh; }
        
        h1 { font-size: 3.5rem; margin: 0 0 30px 0; font-weight: 700; }
        .logo-link { text-decoration: none; color: var(--text-main); }
        .logo-link span { color: var(--accent); }

        .container { width: 90%; max-width: 800px; display: flex; flex-direction: column; align-items: center; }
        .search-wrapper { background: rgba(255, 255, 255, 0.08); padding: 6px 15px 6px 6px; border-radius: 50px; display: flex; align-items: center; width: 100%; border: 1px solid var(--border); }
        input { background: transparent; border: none; color: var(--text-main); font-size: 1.1rem; padding: 14px 15px; width: 100%; font-family: var(--font); font-weight: 500; outline: none; }
        .search-btn { background-color: var(--accent); color: #0D1B2A; border: none; border-radius: 40px; padding: 12px 28px; font-weight: 700; font-size: 1rem; cursor: pointer; }

        .results-container { width: 100%; margin-top: 30px; text-align: left; }
        .section-label { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); margin-bottom: 10px; border-bottom: 1px solid var(--border); padding-bottom: 5px; }
        
        /* Internal Card Style */
        .internal-card { background: var(--bg-card); padding: 15px 20px; border-radius: 12px; margin-bottom: 15px; border-left: 4px solid var(--accent); border: 1px solid var(--border); }
        .internal-card a { color: var(--text-main); font-weight: 700; text-decoration: none; font-size: 1.2rem; display: block; margin-bottom: 5px; }
        .badge { background: rgba(179, 175, 143, 0.2); color: var(--accent); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin-right: 8px; }

        /* Google Widget Overrides (Force Dark Mode) */
        .gsc-control-cse { background-color: transparent !important; border: none !important; padding: 0 !important; }
        .gsc-webResult.gsc-result { background-color: var(--bg-card) !important; border-radius: 12px; margin-bottom: 15px; padding: 20px !important; border: 1px solid var(--border) !important; box-shadow: none !important; }
        .gs-title a { color: var(--text-main) !important; text-decoration: none !important; font-size: 1.2rem !important; font-weight: 700 !important; }
        .gs-snippet { color: var(--text-muted) !important; font-size: 0.95rem !important; }
        .gsc-url-top, .gsc-url-bottom, .gsc-adBlock { display: none !important; } 
    </style>
</head>
<body>
    <div class="container">
        <h1><a href="/" class="logo-link">On<span>Go.</span></a></h1>
        <form action="/search" method="get" style="width: 100%;">
            <div class="search-wrapper">
                <input type="text" name="q" placeholder="Search..." required value="{{ query if query else '' }}">
                <button type="submit" class="search-btn">Search</button>
            </div>
        </form>

        <div class="results-container">
            {% if internal_results %}
                <div class="section-label">⚡ Internal Database ({{ time }}ms)</div>
                {% for res in internal_results %}
                    <div class="internal-card">
                        <a href="{{ res }}" target="_blank">{{ res }}</a>
                        <span class="badge">INTERNAL</span>
                    </div>
                {% endfor %}
                <br>
            {% endif %}

            {% if query %}
                <div class="section-label">🌍 Global Web Results</div>
                <script async src="https://cse.google.com/cse.js?cx=64411374afe3a4b42"></script>
                <div class="gcse-searchresults-only" data-queryParameterName="q" data-linkTarget="_blank"></div>
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
    
    # Internal Lookup
    internal_results = inverted_index.get(query, [])
    
    duration = round((time.time() - start_time) * 1000, 3)
    return render_template_string(HTML_TEMPLATE, query=query, internal_results=internal_results, time=duration)

if __name__ == '__main__':
    app.run(debug=True)