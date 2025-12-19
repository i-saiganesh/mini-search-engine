import json
import time

INDEX_FILE = "inverted_index.json"

def load_index():
    print("🚀 Loading Search Engine...")
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def search(index):
    print("\n🔎 Mini-Google is Ready! (Type 'exit' to stop)")
    
    while True:
        query = input("\nEnter search term: ").lower().strip()
        
        if query == 'exit':
            break
            
        start_time = time.time()
        
        # O(1) Lookup
        results = index.get(query)
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # ms
        
        if results:
            print(f"\nFound {len(results)} results for '{query}' in {duration:.4f} ms:")
            for i, url in enumerate(results[:5], 1):  # Show top 5
                print(f"{i}. {url}")
        else:
            print("No results found.")

if __name__ == "__main__":
    index = load_index()
    search(index)