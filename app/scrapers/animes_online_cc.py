from typing import List
from app.scrapers.base import BaseScraper
from app.models import Anime, Episode, SearchResult
from playwright.async_api import async_playwright
import urllib.parse
import re

class AnimesOnlineCCScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://animesonlinecc.to")

    async def _get_page(self, playwright):
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        return await context.new_page(), browser

    async def search(self, query: str) -> List[SearchResult]:
        results = []
        async with async_playwright() as p:
            page, browser = await self._get_page(p)
            try:
                encoded_query = urllib.parse.quote(query)
                search_url = f"{self.base_url}/?s={encoded_query}" 
                await page.goto(search_url, wait_until="domcontentloaded")
                
                # Check for results
                articles = page.locator('div.result-item, article') 
                count = await articles.count()
                
                print(f"AnimesOnlineCC: Found {count} results for {query}")

                for i in range(count):
                    article = articles.nth(i)
                    title_el = article.locator('.title a, h3 a')
                    if await title_el.count() > 0:
                        title = await title_el.first.inner_text()
                        url = await title_el.first.get_attribute('href')
                        
                        img_el = article.locator('img')
                        cover = await img_el.first.get_attribute('src') if await img_el.count() > 0 else None
                        
                        if url:
                            results.append(SearchResult(
                                title=title.strip(),
                                url=url,
                                cover_image=cover,
                                source="AnimesOnlineCC"
                            ))
            except Exception as e:
                print(f"Error searching AnimesOnlineCC {query}: {e}")
            finally:
                await browser.close()
        return results

    async def get_details(self, anime_url: str) -> Anime:
        anime = None
        async with async_playwright() as p:
            page, browser = await self._get_page(p)
            try:
                await page.goto(anime_url, wait_until="domcontentloaded")
                
                title = "Unknown"
                h1 = page.locator('div.data h1, h1.entry-title')
                if await h1.count() > 0:
                    title = await h1.first.inner_text()
                
                cover = None
                img = page.locator('div.poster img')
                if await img.count() > 0:
                    cover = await img.first.get_attribute('src')

                episodes = []
                # Episodes list often in a separate section or loaded dynamically
                # Try common selectors
                ep_links = page.locator('div.episodios li a, ul.episodes li a')
                count = await ep_links.count()
                
                for i in range(count):
                    link = ep_links.nth(i)
                    ep_url = await link.get_attribute('href')
                    text = await link.inner_text() 
                    
                    ep_num = text
                    match = re.search(r'\d+', text)
                    if match:
                        ep_num = match.group(0)

                    if ep_url:
                        episodes.append(Episode(
                            number=ep_num.strip(), 
                            url=ep_url, 
                            title=text.strip()
                        ))

                anime = Anime(
                    title=title.strip(),
                    url=anime_url,
                    cover_image=cover,
                    episodes=episodes
                )

            except Exception as e:
                print(f"Error getting details for {anime_url} on AnimesOnlineCC: {e}")
            finally:
                await browser.close()
        return anime

    async def get_episode_link(self, episode_url: str) -> str:
        video_link = ""
        async with async_playwright() as p:
            page, browser = await self._get_page(p)
            try:
                await page.goto(episode_url, wait_until="domcontentloaded")
                iframe = page.locator('iframe') # Simplify for now
                if await iframe.count() > 0:
                    # Sometimes there are multiple iframes (ads etc), need the player one
                    # Heuristic: largest size or specific class
                    for i in range(await iframe.count()):
                        src = await iframe.nth(i).get_attribute('src')
                        if src and ("player" in src or "video" in src or "embed" in src):
                            video_link = src
                            break
                    if not video_link and await iframe.count() > 0:
                         video_link = await iframe.first.get_attribute('src')

            except Exception as e:
                 print(f"Error getting episode link {episode_url} on AnimesOnlineCC: {e}")
            finally:
                await browser.close()
        return video_link
