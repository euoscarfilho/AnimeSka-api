from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

def inspect_search():
    url = "https://animesdigital.org/?s=One+Piece"
    print(f"Navigating to {url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        Stealth().apply_stealth_sync(page)
        
        page.goto(url, wait_until="domcontentloaded")
        print("Page loaded.")
        time.sleep(3)
        
        # Check articles
        articles = page.locator('div.result-item, article, .items article')
        count = articles.count()
        print(f"Articles found: {count}")
        
        if count == 0:
             print(f"Page content dump:")
             print(page.content()[:2000])
        
        browser.close()

if __name__ == "__main__":
    inspect_search()
