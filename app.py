from flask import Flask, request, render_template_string
import json
import os

app = Flask(__name__)

# 1. Load Internal Index (Keeps your custom feature)
INDEX_FILE = "inverted_index.json"
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
else:
    inverted_index = {}

# 2. UI Template (Your Dark Mode Design + Google Widget)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OnGo. | Global Search</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root { --bg-body: #0D1B2A; --bg-card: rgba(27, 38, 59, 0.6); --text-main: #E0E1DD; --text-muted: #AAB3C0; --accent-sand: #B3AF8F; --border: rgba(255, 255, 255, 0.05); --font-main: 'Quicksand', sans-serif; }
        * { box-sizing: border-box; }
        body { background-color: var(--bg-body); color: var(--text-main); font-family: var(--font-main); min-height: 100vh; margin: 0; display: flex; flex-direction: column; align-items: center; padding-top: 40px; }
        
        /* LOGO */
        h1 { font-size: 3.5rem; margin: 0 0 30px 0; letter-spacing: -1px; font-weight: 700; }
        .logo-link { text-decoration: none; color: var(--text-main); }
        .logo-link span { color: var(--accent-sand); }

        /* SEARCH BAR */
        .container { width: 90%; max-width: 800px; display: flex; flex-direction: column; align-items: center; }
        .search-wrapper { background: rgba(255, 255, 255, 0.08); padding: 6px 15px 6px 6px; border-radius: 50px; display: flex; align-items: center; width: 100%; border: 1px solid var(--border); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        input { background: transparent; border: none; color: var(--text-main); font-size: 1.1rem; padding: 14px 15px; width: 100%; font-family: var(--font-main); font-weight: 500; outline: none; }
        .search-btn { background-color: var(--accent-sand); color: #0D1B2A; border: none; border-radius: 40px; padding: 12px 28px; font-weight: 700; font-size: 1rem; cursor: pointer; transition: transform 0.2s; }
        .search-btn:hover { transform: scale(1.05); }

        /* RESULTS AREA */
        .results-container { width: 100%; margin-top: 30px; min-height: 400px; text-align: left; }
        
        /* Custom Internal Results Card */
        .internal-card { background: var(--bg-card); padding: 15px 20px; border-radius: 12px; margin-bottom: 15px; border-left: 4px solid var(--accent-sand); border: 1px solid var(--border); }
        .internal-card a { color: var(--text-main); font-weight: 700; text-decoration: none; font-size: 1.2rem; display: block; margin-bottom: 5px; }
        .internal-card p { color: var(--text-muted); margin: 0; font-size: 0.9rem; }

        /* GOOGLE WIDGET CUSTOMIZATION (Force Dark Mode Integration) */
        .gsc-control-cse { background-color: transparent !important; border: none !important; padding: 0 !important; }
        .gsc-webResult.gsc-result { background-color: var(--bg-card) !important; border-radius: 12px; margin-bottom: 15px; padding: 20px !important; border: 1px solid var(--border) !important; box-shadow: none !important; }
        .gsc-webResult.gsc-result:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important; transition: transform 0.2s; }
        
        /* Title Styling */
        .gs-title { text-decoration: none !important; height: auto !important; }
        .gs-title a { color: var(--text-main) !important; font-family: var(--font-main) !important; font-size: 1.2rem !important; font-weight: 700 !important; text-decoration: none !important; }
        .gs-title b { color: var(--accent-sand) !important; }
        
        /* Snippet Styling */
        .gs-snippet { color: var(--text-muted) !important; font-family: var(--font-main) !important; font-size: 0.95rem !important; line-height: 1.5 !important; }
        
        /* Remove Google Junk */
        .gsc-url-top, .gsc-url-bottom { display: none !important; } 
        .gsc-adBlock { display: none !important; }
        
        /* Pagination */
        .gsc-cursor-box { margin-top: 20px; text-align: center; }
        .gsc-cursor-page { color: var(--text-main) !important; background: rgba(255,255,255,0.1); padding: 8px 12px; border-radius: 6px; margin: 0 5px; text-decoration: none !important; display: inline-block; }
        .gsc-cursor-current-page { background-color: var(--accent-sand) !important; color: #0D1B2A !important; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1><a href="/" class="logo-link">On<span>Go.</span></a></h1>
        
        <form action="/search" method="get" style="width: 100%;">
            <div class="search-wrapper">
                <input type="text" name="q" placeholder="Search the web..." required value="{{ query if query else '' }}">
                <button type="submit" class="search-btn">Search</button>
            </div>
        </form>

        <div class="results-container">
            {% if internal_results %}
                <div style="margin-bottom: 20px;">
                {% for res in internal_results %}
                    <div class="internal-card">
                        <a href="{{ res }}" target="_blank">{{ res }}</a>
                        <p>:: Internal Database Match</p>
                    </div>
                {% endfor %}
                </div>
            {% endif %}

            {% if query %}
                <script async src="https://cse.google.com/cse.js?cx=64411374afe3a4b42"></script>
                
                <div class="gcse-searchresults-only" 
                     data-queryParameterName="q" 
                     data-linkTarget="_blank">
                </div>
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
    query = request.args.get('q', '').strip()
    
    # Check Internal Index for matches
    internal_results = []
    if query and query.lower() in inverted_index:
        internal_results = inverted_index[query.lower()]

    # Render template (Google Script handles the rest)
    return render_template_string(HTML_TEMPLATE, query=query, internal_results=internal_results)

if __name__ == '__main__':
    app.run(debug=True)