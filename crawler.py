import requests
from bs4 import BeautifulSoup
from collections import deque
import json
import concurrent.futures
import time

# SETTINGS
MAX_PAGES = 50  # Keep it small for testing
SEED_URL = "https://en.wikipedia.org/wiki/Software_engineering"
DATA_FILE = "crawled_data.json"

# GLOBAL SETTINGS
visited_urls = set()
queue = deque([SEED_URL])
crawled_pages = []  # List to store our results

def get_page_content(url):
    """Fetches a URL and returns the text and new links."""
    try:
        # User-Agent makes us look like a real browser, not a bot
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Extract Title
        title = soup.title.string if soup.title else "No Title"
        
        # 2. Extract Text (simple version)
        text = soup.get_text(separator=' ', strip=True)
        
        # 3. Extract Links for the queue
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Only keep valid Wikipedia links to stay inside the "mini" web
            if href.startswith('/wiki/') and ':' not in href:
                full_url = "https://en.wikipedia.org" + href
                links.append(full_url)
        
        return {
            "url": url,
            "title": title,
            "content": text,
            "links": links
        }
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def crawl():
    print(f"🕷️ Starting crawl from: {SEED_URL}")
    
    # We use a ThreadPool to make it faster (Concurrency!)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        while len(crawled_pages) < MAX_PAGES and queue:
            
            # Get a batch of URLs to process
            current_batch = []
            while queue and len(current_batch) < 5:
                url = queue.popleft()
                if url not in visited_urls:
                    visited_urls.add(url)
                    current_batch.append(url)
            
            if not current_batch:
                break

            # Process the batch in parallel
            future_to_url = {executor.submit(get_page_content, url): url for url in current_batch}
            
            for future in concurrent.futures.as_completed(future_to_url):
                data = future.result()
                if data:
                    print(f"✅ Indexed: {data['title'][:30]}...")
                    # Add result to our "Database"
                    crawled_pages.append({
                        "url": data['url'],
                        "title": data['title'],
                        "content": data['content']
                    })
                    
                    # Add new links to queue
                    for link in data['links']:
                        if link not in visited_urls:
                            queue.append(link)
    
    # Save the data
    print(f"\n💾 Saving {len(crawled_pages)} pages to {DATA_FILE}...")
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(crawled_pages, f, indent=2)
    print("Done!")

if __name__ == "__main__":
    crawl()