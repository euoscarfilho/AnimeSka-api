from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import SearchResult, Anime, Episode
from app.scrapers.animes_hd import AnimesHDScraper
from app.scrapers.animes_digital import AnimesDigitalScraper
from app.scrapers.animes_online_cc import AnimesOnlineCCScraper

router = APIRouter()

animes_hd = AnimesHDScraper()
animes_digital = AnimesDigitalScraper()
animes_online_cc = AnimesOnlineCCScraper()

@router.get("/search", response_model=List[SearchResult])
async def search_anime(q: str, source: Optional[str] = Query(None, description="Source to search from (animes_hd, animes_digital, animes_online_cc)")):
    results = []
    
    if source == "animes_hd" or not source:
        try:
            results.extend(await animes_hd.search(q))
        except Exception as e:
            print(f"Error searching AnimesHD: {e}")
            
    if source == "animes_digital" or not source:
         try:
            results.extend(await animes_digital.search(q))
         except Exception as e:
            print(f"Error searching AnimesDigital: {e}")

    if source == "animes_online_cc" or not source:
         try:
            results.extend(await animes_online_cc.search(q))
         except Exception as e:
            print(f"Error searching AnimesOnlineCC: {e}")

    return results

@router.get("/anime/details", response_model=Anime)
async def get_anime_details(url: str, source: str):
    if source == "AnimesHD":
        return await animes_hd.get_details(url)
    elif source == "AnimesDigital":
        return await animes_digital.get_details(url)
    elif source == "AnimesOnlineCC":
        return await animes_online_cc.get_details(url)
    else:
        raise HTTPException(status_code=400, detail="Invalid source")

@router.get("/episode/link", response_model=str)
async def get_episode_link(url: str, source: str):
    if source == "AnimesHD":
        return await animes_hd.get_episode_link(url)
    elif source == "AnimesDigital":
        return await animes_digital.get_episode_link(url)
    elif source == "AnimesOnlineCC":
        return await animes_online_cc.get_episode_link(url)
    else:
        raise HTTPException(status_code=400, detail="Invalid source")
@router.get("/anime/play", response_model=Optional[str])
async def quick_play(slug: str, source: str, number: str):
    """
    Simplified endpoint: Directly get video link from slug, source and episode number.
    Bypasses the need for client-side multi-step logic.
    """
    scraper = None
    if source == "AnimesHD":
        scraper = animes_hd
    elif source == "AnimesDigital":
        scraper = animes_digital
    elif source == "AnimesOnlineCC":
        scraper = animes_online_cc
    
    if not scraper:
        raise HTTPException(status_code=400, detail="Invalid source")

    # 1. Reconstruct anime URL
    anime_url = scraper.get_anime_url(slug)
    
    # 2. Get details to find the episode URL for the given number
    anime_details = await scraper.get_details(anime_url)
    if not anime_details or not anime_details.episodes:
        raise HTTPException(status_code=404, detail="Anime or episodes not found")
    
    # 3. Find specific episode
    episode = next((ep for ep in anime_details.episodes if ep.number == number), None)
    if not episode:
        # Try fuzzy match if exact fails (e.g. "01" vs "1")
        episode = next((ep for ep in anime_details.episodes if ep.number.lstrip('0') == number.lstrip('0')), None)
    
    if not episode:
        raise HTTPException(status_code=404, detail=f"Episode {number} not found")
    
    # 4. Get video link
    video_link = await scraper.get_episode_link(episode.url)
    return video_link
