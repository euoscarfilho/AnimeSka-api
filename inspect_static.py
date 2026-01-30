import httpx
from bs4 import BeautifulSoup
import asyncio

async def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = "https://betteranime.net"
    print(f"Fetching {url}...")
    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            resp = await client.get(url, timeout=10.0)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                with open("static_homepage.html", "w", encoding="utf-8") as f:
                    f.write(resp.text)
                soup = BeautifulSoup(resp.text, 'html.parser')
                print(f"Title: {soup.title.string if soup.title else 'No title'}")
                
                # Check for useful elements
                animes = soup.select('article.anime-item')
                print(f"Found {len(animes)} potential anime items")
                
            else:
                print("Failed to fetch page")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
