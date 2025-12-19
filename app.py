from flask import Flask, request, render_template_string
import json
import time
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 1. Load Internal Index
INDEX_FILE = "inverted_index.json"
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
else:
    inverted_index = {}

# 2. The "Dune / High-End" UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mini-Google</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=BBH+Bartle&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">

    <style>
        :root {
            /* Your Custom Palette */
            --bg-dark: #0D1B2A;       /* Black/Navy */
            --bg-card: #1B263B;       /* Dark Blue */
            --text-main: #E0E1DD;     /* Bone White */
            --accent-sand: #B3AF8F;   /* Sand/Gold */
            --accent-blue: #415A77;   /* Muted Blue */
            
            --font-display: 'BBH Bartle', serif; /* The Crazy Font */
            --font-body: 'Inter', sans-serif;    /* Readable Font */
        }
        
        body { 
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: var(--font-body);
            min-height: 100vh;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center; /* Center vertically like the login page */
        }

        /* The Logo - Using the Crazy Font */
        h1 { 
            font-family: var(--font-display);
            font-size: 5rem; 
            margin: 0 0 40px 0;
            letter-spacing: -2px;
            text-transform: uppercase;
            color: var(--text-main);
            text-align: center;
            line-height: 0.9;
        }
        
        h1 span {
            color: var(--accent-sand);
        }

        .container {
            width: 90%;
            max-width: 800px;
            text-align: center;
        }

        /* The Search Box Area */
        .search-wrapper {
            background: var(--bg-card);
            padding: 10px;
            border-radius: 12px;
            display: flex;
            gap: 10px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            border: 1px solid var(--accent-blue);
            transition: transform 0.3s ease;
        }

        .search-wrapper:focus-within {
            transform: scale(1.02);
            border-color: var(--accent-sand);
        }

        input { 
            background: transparent;
            border: none;
            color: var(--text-main);
            font-size: 1.2rem;
            padding: 15px 20px;
            width: 100%;
            font-family: var(--font-body);
            outline: none;
        }

        input::placeholder {
            color: var(--accent-blue);
            opacity: 0.7;
        }

        button { 
            background-color: var(--accent-sand);
            color: var(--bg-dark);
            border: none;
            border-radius: 8px;
            padding: 0 30px;
            font-family: var(--font-display);
            font-size: 1.2rem;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.2s;
        }

        button:hover {
            background-color: var(--text-main);
            transform: translateY(-2px);
        }

        /* Results Area */
        .stats {
            margin-top: 20px;
            color: var(--accent-blue);
            font-size: 0.9rem;
            text-align: left;
            padding-left: 10px;
        }

        .results {
            margin-top: 30px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            text-align: left;
        }

        .result-card {
            background: var(--bg-card);
            padding: 25px;
            border-radius: 4px; /* Sharper edges for modern look */
            border-left: 4px solid var(--accent-blue);
            transition: all 0.2s ease;
        }
        
        .web-result {
            border-left-color: var(--accent-sand);
        }

        .result-card:hover {
            transform: translateX(10px);
            background: #23314A; /* Slightly lighter on hover */
        }

        a { 
            font-family: var(--font-display);
            font-size: 1.5rem;
            color: var(--text-main);
            text-decoration: none;
            display: block;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }
        
        a:hover {
            text-decoration: underline;
            text-decoration-color: var(--accent-sand);
        }

        p.snippet {
            color: #AAB3C0; /* Muted grey/blue */
            line-height: 1.6;
            font-size: 1rem;
            margin: 0;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-dark); }
        ::-webkit-scrollbar-thumb { background: var(--accent-blue); border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Mini<span>Google</span></h1>
        
        <form action="/search" method="get">
            <div class="search-wrapper">
                <input type="text" name="q" placeholder="Type to search..." required value="{{ query if query else '' }}">
                <button type="submit">GO</button>
            </div>
        </form>
        
        {% if query %}
            <p class="stats">:: Found results for "<b>{{ query }}</b>" in {{ time }} ms</p>
            
            <div class="results">
                {% for res in results %}
                    <div class="result-card {{ 'web-result' if res.type == 'web' else '' }}">
                        <a href="{{ res.link }}" target="_blank">{{ res.title }}</a>
                        <p class="snippet">{{ res.desc }}</p>
                    </div>
                {% endfor %}
                
                {% if not results %}
                    <p style="color: var(--accent-blue)">:: System returned 0 results.</p>
                {% endif %}
            </div>
        {% endif %}
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
    final_results = []

    if query:
        # 1. Internal DB
        if query in inverted_index:
            for url in inverted_index[query]:
                final_results.append({
                    "title": url, "link": url, 
                    "desc": ":: Internal Index Match", "type": "internal"
                })

        # 2. Web Search (Scraper)
        try:
            url = "https://html.duckduckgo.com/html/"
            payload = {'q': query}
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.post(url, data=payload, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            count = 0
            for result in soup.find_all('div', class_='result'):
                if count >= 6: break
                link_tag = result.find('a', class_='result__a')
                snippet_tag = result.find('a', class_='result__snippet')
                if link_tag:
                    final_results.append({
                        "title": link_tag.get_text(),
                        "link": link_tag['href'],
                        "desc": snippet_tag.get_text() if snippet_tag else "No data available.",
                        "type": "web"
                    })
                    count += 1
        except Exception as e:
            print(f"Error: {e}")

    duration = round((time.time() - start_time) * 1000, 2)
    return render_template_string(HTML_TEMPLATE, query=query, results=final_results, time=duration)

if __name__ == '__main__':
    app.run(debug=True)