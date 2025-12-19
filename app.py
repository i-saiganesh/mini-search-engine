HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini-Google</title>
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

        .result-card:hover {
            transform: scale(1.02);
        }

        a { text-decoration: none; color: #2d3748; font-weight: 600; font-size: 18px; }
        a:hover { color: #764ba2; text-decoration: underline; }

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
            <input type="text" name="q" placeholder="Search the web..." required>
            <button type="submit">Search</button>
        </form>
        
        {% if query %}
            <p class="stats">🚀 Found {{ count }} results in {{ time }} ms</p>
            <div>
                {% for url in results %}
                    <div class="result-card">
                        <a href="{{ url }}" target="_blank">{{ url }}</a>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""