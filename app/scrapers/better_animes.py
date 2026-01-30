from typing import List
from app.scrapers.base import BaseScraper
from app.models import Anime, Episode, SearchResult
from playwright.async_api import async_playwright
import urllib.parse

class BetterAnimesScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://betteranime.net")

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
                # Search URL might be different, need to verify
                # Usually /pesquisa?q=... or similar
                encoded_query = urllib.parse.quote(query)
                search_url = f"{self.base_url}/?s={encoded_query}" 
                await page.goto(search_url, wait_until="domcontentloaded")
                
                # Check if results exist
                # Try multiple common selectors for anime results
                articles = page.locator('article.anime-item, div.item, div.result-item') 
                count = await articles.count()
                
                print(f"Found {count} results for {query}")

                for i in range(count):
                    article = articles.nth(i)
                    title_el = article.locator('h3 a, .title a, h2 a')
                    if await title_el.count() > 0:
                        title = await title_el.first.inner_text()
                        url = await title_el.first.get_attribute('href')
                        img_el = article.locator('img')
                        cover = await img_el.first.get_attribute('src') if await img_el.count() > 0 else None
                        
                        results.append(SearchResult(
                            title=title.strip(),
                            url=url,
                            cover_image=cover,
                            source="BetterAnimes"
                        ))
            except Exception as e:
                print(f"Error searching {query}: {e}")
            finally:
                await browser.close()
        return results

    async def get_details(self, anime_url: str) -> Anime:
        anime = None
        async with async_playwright() as p:
            page, browser = await self._get_page(p)
            try:
                await page.goto(anime_url)
                
                # TODO: Update selectors
                title = await page.title() # Placeholder
                # Usually h1
                h1 = page.locator('div.infos h1')
                if await h1.count() > 0:
                    title = await h1.inner_text()
                
                cover = None
                img = page.locator('div.poster img')
                if await img.count() > 0:
                    cover = await img.get_attribute('src')

                episodes = []
                # Episodes list
                # Usually ul#episodes-list li a
                ep_links = page.locator('ul#episodes-list li a')
                count = await ep_links.count()
                
                for i in range(count):
                    link = ep_links.nth(i)
                    ep_url = await link.get_attribute('href')
                    ep_num = await link.inner_text() 
                    episodes.append(Episode(
                        number=ep_num.strip(), 
                        url=ep_url, 
                        title=f"Episode {ep_num}"
                    ))

                anime = Anime(
                    title=title.strip(),
                    url=anime_url,
                    cover_image=cover,
                    episodes=episodes
                )

            except Exception as e:
                print(f"Error getting details for {anime_url}: {e}")
            finally:
                await browser.close()
        return anime

    async def get_episode_link(self, episode_url: str) -> str:
        video_link = ""
        async with async_playwright() as p:
            page, browser = await self._get_page(p)
            try:
                await page.goto(episode_url)
                # Ensure player loads
                # TODO: This is tricky, usually an iframe
                iframe = page.locator('iframe')
                if await iframe.count() > 0:
                    video_link = await iframe.first.get_attribute('src')
            except Exception as e:
                 print(f"Error getting episode link {episode_url}: {e}")
            finally:
                await browser.close()
        return video_link
