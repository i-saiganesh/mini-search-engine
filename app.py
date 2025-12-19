from flask import Flask, request, render_template_string
import json
import time
import os
import requests  # We use this to talk to Wikipedia

app = Flask(__name__)

# 1. Load the Index (The "Fast" Memory)
INDEX_FILE = "inverted_index.json"
print("🚀 Loading Index...")
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
else:
    inverted_index = {}

# 2. The Modern UI (Purple Gradient & Glassmorphism)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini-Google</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        
        body { 
            font-family: 'Poppins', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #333;
        }

        h1 { 
            color: white; 
            font-size: 3rem; 
            margin-top: 60px; 
            text-shadow: 0 4px 6px rgba(0,0,0,0.1);
            letter-spacing: 1px;
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            width: 80%;
            max-width: 600px;
            text-align: center;
            animation: fadeIn 0.8s ease-out;
        }

        input { 
            padding: 15px; 
            width: 70%; 
            border-radius: 50px; 
            border: 2px solid #eee; 
            font-size: 16px;
            outline: none;
            transition: all 0.3s;
        }

        input:focus {
            border-color: #764ba2;
            box-shadow: 0 0 10px rgba(118, 75, 162, 0.2);
        }

        button { 
            padding: 15px 30px; 
            background: linear-gradient(to right, #667eea, #764ba2);
            color: white; 
            border: none; 
            border-radius: 50px; 
            font-size: 16px;
            font-weight: bold;
            cursor: pointer; 
            margin-left: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        .stats { color: #666; font-size: 14px; margin: 20px 0; font-style: italic; }

        .result-card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            text-align: left;
            border-left: 5px solid #764ba2;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }

        .wiki-card {
            background: #fdfdfd;
            border-left: 5px solid #ff9800; /* Orange for Wiki Results */
        }

        .result-card:hover {
            transform: scale(1.02);
        }

        a { text-decoration: none; color: #2d3748; font-weight: 600; font-size: 18px; }
        a:hover { color: #764ba2; text-decoration: underline; }
        
        p.snippet { color: #555; font-size: 14px; margin-top: 5px; line-height: 1.5; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <h1>🕷️ Mini-Google</h1>
    <div class="container">
        <form action="/search" method="get">
            <input type="text" name="q" placeholder="Search anything (e.g. 'Ferrari', 'Mars')..." required>
            <button type="submit">Search</button>
        </form>
        
        {% if query %}
            <p class="stats">🚀 Result for "<b>{{ query }}</b>" ({{ time }} ms)</p>
            
            <div class="results">
                {% for url in db_results %}
                    <div class="result-card">
                        <a href="{{ url }}" target="_blank">{{ url }}</a>
                        <p class="snippet">Source: Internal Index</p>
                    </div>
                {% endfor %}

                {% if wiki_title %}
                    <div class="result-card wiki-card">
                        <a href="{{ wiki_url }}" target="_blank">📖 {{ wiki_title }} (Wikipedia)</a>
                        <p class="snippet">{{ wiki_summary }}</p>
                    </div>
                {% endif %}

                {% if not db_results and not wiki_title %}
                    <p>No results found locally or on Wikipedia. Try searching for "Python", "Java", or a famous noun.</p>
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
    if not query:
        return render_template_string(HTML_TEMPLATE)
    
    start_time = time.time()
    
    # 1. Search Local Database (Exact Match)
    db_results = inverted_index.get(query, [])
    
    # 2. Search Wikipedia (Instant Answer)
    wiki_title = None
    wiki_summary = None
    wiki_url = None
    
    # If database has few/no results, ask Wikipedia
    if len(db_results) < 3:
        try:
            # We call the public Wikipedia API
            response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}")
            if response.status_code == 200:
                data = response.json()
                if "extract" in data:
                    wiki_title = data['title']
                    wiki_summary = data['extract']
                    wiki_url = data['content_urls']['desktop']['page']
        except Exception as e:
            print(f"Wiki Error: {e}")

    duration = round((time.time() - start_time) * 1000, 2)
    
    return render_template_string(
        HTML_TEMPLATE, 
        query=query, 
        db_results=db_results, 
        wiki_title=wiki_title,
        wiki_summary=wiki_summary,
        wiki_url=wiki_url,
        time=duration
    )

if __name__ == '__main__':
    app.run(debug=True)