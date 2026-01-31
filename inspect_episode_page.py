from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def inspect_episode():
    url = "https://animeshd.to/episodios/naruto-shippuden-dublado-episodio-196/"
    print(f"Navigating to {url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        Stealth().apply_stealth_sync(page)
        
        page.goto(url, wait_until="domcontentloaded")
        print("Page loaded.")
        
        # Dump iframes
        frames = page.frames
        print(f"Total Frames: {len(frames)}")
        for f in frames:
            print(f"Frame: {f.name} - {f.url}")
            
        # Dump iframes via locator
        iframes = page.locator("iframe")
        count = iframes.count()
        print(f"Iframes found via locator: {count}")
        for i in range(count):
            print(f"Iframe {i}: src={iframes.nth(i).get_attribute('src')} class={iframes.nth(i).get_attribute('class')}")
            
        # Save HTML
        with open("episode_dump.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("Saved HTML to episode_dump.html")

if __name__ == "__main__":
    inspect_episode()
