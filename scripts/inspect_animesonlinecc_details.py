from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def inspect_details():
    # Use a known url that failed or just search URL result if persistent
    # verify_all_sources found dragon-ball-daima
    url = "https://animesonlinecc.to/anime/dragon-ball-daima/" 
    print(f"Navigating to {url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        Stealth().apply_stealth_sync(page)
        
        page.goto(url, wait_until="domcontentloaded")
        print("Page loaded.")
        
        # Check episodes selector
        # Current: div.episodios li a, ul.episodes li a
        eps = page.locator('div.episodios li a, ul.episodes li a')
        print(f"Episodes found (current selector): {eps.count()}")
        
        # Dump if 0
        if eps.count() == 0:
             print("Dumping HTML...")
             with open("onlinecc_dump.html", "w", encoding="utf-8") as f:
                 f.write(page.content())
        
        browser.close()

if __name__ == "__main__":
    inspect_details()
