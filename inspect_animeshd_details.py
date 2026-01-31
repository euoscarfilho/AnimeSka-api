import requests
from bs4 import BeautifulSoup

def inspect_details():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Search first
    search_url = "https://animeshd.to/?s=Naruto"
    print(f"Searching: {search_url}")
    try:
        resp = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Get first result
        link = soup.select_one('article h3 a, .title a, .poster a')
        if not link:
            print("No results found")
            return
            
        url = link.get('href')
        print(f"Inspecting detail page: {url}")
        
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
        
        # Description
        desc = soup.select_one('.sinopse, .description, .content p, .entry-content p, .info-content .desc')
        if desc:
            print(f"Description found: {desc.text.strip()[:100]}...")
        else:
            print("Description NOT found")

        # Genres
        genres = soup.select('.genres a, .sgeneros a, .generos a')
        print(f"Genres found: {[g.text for g in genres]}")

        # Year
        year = soup.select_one('.date, .year, .meta .date')
        if year:
            print(f"Year found: {year.text.strip()}")

        # Status (Ongoing/Completed)
        status = soup.select_one('.status, .meta .status, .estado, .info-content .status')
        if status:
            print(f"Status found: {status.text.strip()}")
            
        # Image
        img = soup.select_one('.poster img, .sheader .poster img')
        if img:
             print(f"Image found: {img.get('src')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_details()
