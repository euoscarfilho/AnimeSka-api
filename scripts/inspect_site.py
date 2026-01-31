import asyncio
from playwright.async_api import async_playwright
import sys

async def main():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        url = "https://betteranime.net"
        print(f"Navigating to {url}...")
        try:
            await page.goto(url, timeout=60000)
            print(f"Page Title: {await page.title()}")
            
            # Save homepage HTML
            with open("homepage.html", "w", encoding="utf-8") as f:
                f.write(await page.content())
            
            # Try to find search bar
            print("Looking for search input...")
            # Common selectors for search
            selectors = ['input[name="s"]', 'input[type="search"]', 'input.form-control']
            search_input = None
            for s in selectors:
                if await page.locator(s).count() > 0:
                    search_input = page.locator(s).first
                    print(f"Found search input with selector: {s}")
                    break
            
            if search_input:
                await search_input.fill("Naruto")
                await search_input.press("Enter")
                await page.wait_for_load_state("networkidle")
                print("Search submitted. Waiting for results...")
                
                # Save search results HTML
                with open("search_results.html", "w", encoding="utf-8") as f:
                    f.write(await page.content())
            else:
                print("Search input not found.")
                
        except Exception as e:
            print(f"Error accessing {url}: {e}")
            # Try capturing screenshot/content on error
            try:
                with open("error_page.html", "w", encoding="utf-8") as f:
                    f.write(await page.content())
            except:
                pass

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
