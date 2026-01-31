from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

def sniff_video():
    url = "https://animeshd.to/episodios/naruto-shippuden-dublado-episodio-196/" # Example url
    print(f"Navigating to {url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        stealth = Stealth()
        stealth.apply_stealth_sync(page)

        video_urls = []

        # Intercept requests
        def handle_request(route):
            req = route.request
            if ".mp4" in req.url or ".m3u8" in req.url or "videoplayback" in req.url:
                print(f"FOUND VIDEO URL: {req.url}")
                video_urls.append(req.url)
            route.continue_()

        page.route("**/*", handle_request)
        
        try:
             page.goto(url, wait_until="domcontentloaded")
             time.sleep(5) # Give time for player to load and make requests
             
             # Try to click on the player if needed?
             # Sometimes requests only trigger after click
             frames = page.frames
             print(f"Frames found: {len(frames)}")
             
             for frame in frames:
                 print(f"Frame URL: {frame.url}")
                 
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    sniff_video()
