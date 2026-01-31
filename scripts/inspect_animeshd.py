import requests
from bs4 import BeautifulSoup

def inspect():
    url = "https://animeshd.to"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    print(f"Fetching {url}...")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
        
        # Check for search form
        forms = soup.find_all('form')
        for form in forms:
            print(f"Form found: action={form.get('action')}, method={form.get('method')}")
        
        # Try a search request if possible
        search_params = {"s": "Naruto"}
        search_url = f"{url}/?s=Naruto"
        print(f"Searching: {search_url}")
        
        search_resp = requests.get(search_url, headers=headers)
        search_soup = BeautifulSoup(search_resp.text, 'html.parser')
        
        articles = search_soup.select('article h3 a, .title a, .poster a')
        print(f"Found {len(articles)} articles")
        for article in articles:
            print(f"Title: {article.text}, Href: {article.get('href')}")
        print(f"Found {len(items)} items on homepage")
        if items:
            item = items[0]
            print(f"Sample item HTML: {item.prettify()[:500]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
