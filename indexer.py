import json
import re

# SETTINGS
INPUT_FILE = "crawled_data.json"
INDEX_FILE = "inverted_index.json"

def create_index():
    print("🧠 Building Inverted Index...")
    
    # Load the crawled data
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        pages = json.load(f)
    
    # The Inverted Index: { "word": [url1, url2, ...] }
    inverted_index = {}
    
    for page in pages:
        url = page['url']
        content = page['content']
        
        # 1. Tokenize (Split text into words)
        # We use Regex to remove punctuation and make everything lowercase
        words = re.findall(r'\w+', content.lower())
        
        # 2. Add to Index
        # We use a set first to avoid duplicate URLs for the same word on the same page
        unique_words_on_page = set(words)
        
        for word in unique_words_on_page:
            if word not in inverted_index:
                inverted_index[word] = []
            inverted_index[word].append(url)
            
    # Save the index
    print(f"💾 Saving index with {len(inverted_index)} unique words...")
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f)
    print("Done!")

if __name__ == "__main__":
    create_index()