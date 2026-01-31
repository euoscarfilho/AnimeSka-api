from typing import List
from app.scrapers.base import BaseScraper
from app.models import Anime, Episode, SearchResult
from playwright.async_api import async_playwright
import urllib.parse
import re
from playwright_stealth import Stealth

class AnimesHDScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://animeshd.to")

    async def _get_page(self, playwright):
        browser = await playwright.chromium.launch(headless=True)
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
                # Search URL: /?s=QUERY
                encoded_query = urllib.parse.quote(query)
                search_url = f"{self.base_url}/?s={encoded_query}" 
                await page.goto(search_url, wait_until="domcontentloaded")
                
                # Check for results
                # Common selectors: article.item, .result-item
                articles = page.locator('article.item, div.result-item, .animation-2 article') 
                count = await articles.count()
                
                print(f"AnimesHD: Found {count} results for {query}")

                for i in range(count):
                    article = articles.nth(i)
                    title_el = article.locator('h3 a, .title a, .poster a')
                    if await title_el.count() > 0:
                        first_title_el = title_el.first
                        title = await first_title_el.inner_text()
                        url = await first_title_el.get_attribute('href')
                        
                        img_el = article.locator('img')
                        cover = await img_el.first.get_attribute('src') if await img_el.count() > 0 else None
                        
                        slug = url.rstrip('/').split('/')[-1] if url else None

                        results.append(SearchResult(
                            slug=slug,
                            title=title.strip(),
                            url=url,
                            cover_image=cover,
                            source="AnimesHD"
                        ))
            except Exception as e:
                print(f"Error searching AnimesHD {query}: {e}")
            finally:
                await browser.close()
        return results

    async def get_details(self, anime_url: str) -> Anime:
        anime = None
        async with async_playwright() as p:
            browser = None
            try:
                page, browser = await self._get_page(p)
                
                await page.goto(anime_url, wait_until="domcontentloaded")
                
                title = "Unknown"
                h1 = page.locator('h1.entry-title, .data h1')
                if await h1.count() > 0:
                    title = await h1.first.inner_text()
                
                cover = None
                img = page.locator('.poster img, .sheader .poster img')
                if await img.count() > 0:
                    cover = await img.first.get_attribute('src')
                    
                # Initialize Anime object immediately
                # Extract slug
                slug = anime_url.rstrip('/').split('/')[-1]

                anime = Anime(
                    slug=slug,
                    title=title.strip(),
                    url=anime_url,
                    cover_image=cover,
                    episodes=[],
                    source="AnimesHD"
                )

                # Episodes list
                try:
                    # Wait for episodes to load
                    try:
                        await page.wait_for_selector('.episodios li a, .episodes-list li a', timeout=5000)
                    except:
                        print("Timeout waiting for episodes selector, trying to proceed anyway...")

                    ep_links = page.locator('.episodios li a, .episodes-list li a')
                    count = await ep_links.count()
                    
                    for i in range(count):
                        try:
                            link = ep_links.nth(i)
                            ep_url = await link.get_attribute('href')
                            text = await link.inner_text() 
                            
                            ep_num = text
                            match = re.search(r'\d+', text)
                            if match:
                                ep_num = match.group(0)
        
                            if ep_url:
                                anime.episodes.append(Episode(
                                    number=ep_num.strip(), 
                                    url=ep_url, 
                                    title=text.strip()
                                ))
                        except Exception as e_inner:
                            print(f"Error parsing episode {i} on AnimesHD: {e_inner}")
                except Exception as e_eps:
                    print(f"Error extracting episodes list on AnimesHD: {e_eps}")

                # Extra fields
                try:
                    # Description
                    desc_el = page.locator('.sinopse, .description, .content p, .entry-content p')
                    if await desc_el.count() > 0:
                         anime.description = await desc_el.first.inner_text()
                    
                    # Genres
                    genres_el = page.locator('.genres a, .sgeneros a, .generos a')
                    count_g = await genres_el.count()
                    for i in range(count_g):
                         anime.genres.append(await genres_el.nth(i).inner_text())

                    # Year
                    year_el = page.locator('.date, .year, .meta .date')
                    if await year_el.count() > 0:
                         anime.year = await year_el.first.inner_text()

                    # Status
                    status_el = page.locator('.status, .meta .status, .estado')
                    if await status_el.count() > 0:
                         anime.status = await status_el.first.inner_text()

                    # Season
                    anime.season = "Unknown"
                    season_match = re.search(r'(\d+)ª Temporada|Season (\d+)|(\d+) Temporada', title, re.IGNORECASE)
                    if season_match:
                        anime.season = season_match.group(1) or season_match.group(2) or season_match.group(3)
                    else: 
                         anime.season = "1"
                except Exception as e:
                    print(f"Error extracting extra fields for {anime_url} on AnimesHD: {e}")

            except Exception as e:
                print(f"Critical error getting details for {anime_url} on AnimesHD: {e}")
                import traceback
                traceback.print_exc()
            finally:
                if browser:
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
                
                # Wait a bit for requests
                try:
                    await page.wait_for_timeout(3000)
                except:
                    pass

                if found_videos:
                     video_link = found_videos[0]
                else:
                    # Fallback: Check iframe and navigate to it
                    iframe = page.locator('iframe.player, .video-content iframe, .embed-responsive iframe, iframe.metaframe')
                    if await iframe.count() > 0:
                        src = await iframe.first.get_attribute('src')
                        if src:
                            print(f"Navigating to iframe src: {src}")
                            # Reset found videos or keep appending?
                            # Navigate to iframe src to capture network there
                            await page.goto(src, wait_until="domcontentloaded")
                            await page.wait_for_timeout(5000)
                            if found_videos:
                                 video_link = found_videos[0]
                            else:
                                 # Fallback to src if no video found
                                 video_link = src
                    else:
                         # Try video tag
                         video = page.locator('video')
                         if await video.count() > 0:
                             video_link = await video.first.get_attribute('src')

            except Exception as e:
                 print(f"Error getting episode link {episode_url} on AnimesHD: {e}")
            finally:
                await browser.close()
    def get_anime_url(self, slug: str) -> str:
        return f"{self.base_url}/animes/{slug}/"
