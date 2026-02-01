from typing import List
from app.scrapers.base import BaseScraper
from app.models import Anime, Episode, SearchResult
from playwright.async_api import async_playwright
import urllib.parse
import re
from playwright_stealth import Stealth

class AnimesDigitalScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://animesdigital.org")

    async def _get_page(self, playwright):
        browser = await playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        return page, browser

    async def search(self, query: str) -> List[SearchResult]:
        results = []
        async with async_playwright() as p:
            page, browser = await self._get_page(p)
            try:
                # Search URL pattern
                encoded_query = urllib.parse.quote(query)
                search_url = f"{self.base_url}/?s={encoded_query}" 
                await page.goto(search_url, wait_until="domcontentloaded")
                
                # Check if redirected to a specific anime page
                current_url = page.url
                if "/anime/" in current_url:
                     # Parse as single result
                     print(f"AnimesDigital: Redirected to {current_url}")
                     # Extract details for result
                     title_el = page.locator('div.data h1')
                     title = await title_el.first.inner_text() if await title_el.count() > 0 else "Unknown"
                     img_el = page.locator('div.poster img')
                     cover = await img_el.first.get_attribute('src') if await img_el.count() > 0 else None
                     
                     results.append(SearchResult(
                        slug=current_url.rstrip('/').split('/')[-1],
                        title=title.strip(),
                        url=current_url,
                        cover_image=cover,
                        source="AnimesDigital"
                     ))
                else:
                    # Check for results list
                    # Updated selectors based on debug dump: .itemA
                    articles = page.locator('div.itemA, div.result-item, article, .items article') 
                    count = await articles.count()
                    
                    print(f"AnimesDigital: Found {count} results for {query}")
    
                    for i in range(count):
                        article = articles.nth(i)
                        # Updated title/link selectors
                        # Structure: .itemA > a (href) ... .title > .title_anime (text)
                        
                        # Try finding the anchor tag directly if it wraps the whole item
                        link_el = article.locator('a').first
                        if await link_el.count() > 0:
                            url = await link_el.get_attribute('href')
                            
                            # Title: try .title_anime or fallback
                            title_el = article.locator('.title_anime, .title, h3')
                            if await title_el.count() > 0:
                                title = await title_el.first.inner_text()
                            else:
                                title = "Unknown"
                            
                            img_el = article.locator('img')
                            cover = await img_el.first.get_attribute('src') if await img_el.count() > 0 else None
                            
                            if url:
                                results.append(SearchResult(
                                    slug=url.rstrip('/').split('/')[-1],
                                    title=title.strip(),
                                    url=url,
                                    cover_image=cover,
                                    source="AnimesDigital"
                                ))
            except Exception as e:
                print(f"Error searching AnimesDigital {query}: {e}")
            finally:
                await browser.close()
        return results

    async def get_details(self, anime_url: str) -> Anime:
        anime = None
        async with async_playwright() as p:
            page, browser = await self._get_page(p)
            try:
                await page.goto(anime_url, wait_until="domcontentloaded")
                
                # Title
                title = "Unknown"
                h1 = page.locator('h1.entry-title, h1.title, .infos h1')
                if await h1.count() > 0:
                    title = await h1.first.inner_text()
                
                # Cover
                cover = None
                img = page.locator('.poster img, .thumb img')
                if await img.count() > 0:
                    cover = await img.first.get_attribute('src')

                episodes = []
                # Episodes list
                # Wait for episodes to load (dynamic)
                try:
                    await page.wait_for_selector('.item_ep', timeout=5000)
                except:
                    print(f"Timeout waiting for episodes on {anime_url}")

                ep_elements = page.locator('.lista_episodes .item_ep')
                count = await ep_elements.count()
                
                for i in range(count):
                    el = ep_elements.nth(i)
                    link_el = el.locator('a').first
                    ep_url = await link_el.get_attribute('href')
                    
                    # Extract number from title_anime div
                    title_el = el.locator('.title_anime')
                    if await title_el.count() > 0:
                        text = await title_el.inner_text()
                    else:
                        text = await link_el.inner_text() # Fallback

                    # "Jujutsu Kaisen 2 Episódio 23" -> 23
                    ep_num = "1"
                    match = re.search(r'Episódio\s+(\d+)', text, re.IGNORECASE)
                    if not match:
                         match = re.search(r'\d+', text)
                    
                    if match:
                        ep_num = match.group(1) if len(match.groups()) > 0 else match.group(0)

                    if ep_url:
                        episodes.append(Episode(
                            number=ep_num.strip(), 
                            url=ep_url, 
                            title=text.strip()
                        ))

                anime = Anime(
                    slug=anime_url.rstrip('/').split('/')[-1],
                    title=title.strip(),
                    url=anime_url,
                    cover_image=cover,
                    episodes=episodes
                )
                
                # Extra fields
                # Description
                desc_el = page.locator('.sinopse, .description, .content p')
                if await desc_el.count() > 0:
                     anime.description = await desc_el.first.inner_text()
                
                # Genres
                genres_el = page.locator('.genres a, .sgeneros a')
                count_g = await genres_el.count()
                for i in range(count_g):
                     anime.genres.append(await genres_el.nth(i).inner_text())

                # Year
                year_el = page.locator('.date, .year, .meta .date')
                if await year_el.count() > 0:
                     anime.year = await year_el.first.inner_text()

                # Status
                status_el = page.locator('.status, .meta .status')
                if await status_el.count() > 0:
                     anime.status = await status_el.first.inner_text()

                # Season
                anime.season = "Unknown"
                season_match = re.search(r'(\d+)ª Temporada|Season (\d+)|(\d+) Temporada', title, re.IGNORECASE)
                if season_match:
                    anime.season = season_match.group(1) or season_match.group(2) or season_match.group(3)
                else:
                    anime.season = "1"
                
                anime.source = "AnimesDigital"

            except Exception as e:
                print(f"Error getting details for {anime_url} on AnimesDigital: {e}")
            finally:
                await browser.close()
        return anime

    async def get_episode_link(self, episode_url: str) -> str:
        video_link = ""
        async with async_playwright() as p:
            page, browser = await self._get_page(p)
            try:
                # Setup network sniffing
                found_videos = []
                async def handle_request(route):
                    req = route.request
                    url = req.url
                    if ".mp4" in url or ".m3u8" in url or "videoplayback" in url:
                        found_videos.append(url)
                    await route.continue_()

                await page.route("**/*", handle_request)

                await page.goto(episode_url, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)

                if found_videos:
                     video_link = found_videos[0]
                else:
                    # Fallback: iframe
                    iframe = page.locator('iframe.player, .video-content iframe, #player iframe')
                    if await iframe.count() > 0:
                        src = await iframe.first.get_attribute('src')
                        if src:
                            print(f"Navigating to iframe src: {src}")
                            await page.goto(src, wait_until="domcontentloaded")
                            await page.wait_for_timeout(5000)
                            if found_videos:
                                 video_link = found_videos[0]
                            else:
                                 video_link = src
                    else:
                         video = page.locator('video')
                         if await video.count() > 0:
                             video_link = await video.first.get_attribute('src')

            except Exception as e:
                 print(f"Error getting episode link {episode_url} on AnimesDigital: {e}")
            finally:
                await browser.close()
        return video_link
    def get_anime_url(self, slug: str) -> str:
        return f"{self.base_url}/anime/{slug}/"
