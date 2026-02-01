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
    result = None
    if source == "AnimesHD":
        result = await animes_hd.get_details(url)
    elif source == "AnimesDigital":
        result = await animes_digital.get_details(url)
    elif source == "AnimesOnlineCC":
        result = await animes_online_cc.get_details(url)
    else:
        raise HTTPException(status_code=400, detail="Invalid source")
    
    if not result:
        raise HTTPException(status_code=404, detail="Anime details not found or scraping failed")
    
    return result

from app.services.discovery import discovery_service

@router.get("/search", response_model=List[SearchResult])
async def search_anime(q: str, source: Optional[str] = Query(None, description="Source to search from (animes_hd, animes_digital, animes_online_cc)")):
    if source:
        # Specific source search
        # Map query param to scraper name if needed, or rely on service map
        # For backwards compatibility with "animes_hd" etc
        normalized_source = source
        if source == "animes_hd": normalized_source = "AnimesHD"
        if source == "animes_digital": normalized_source = "AnimesDigital"
        if source == "animes_online_cc": normalized_source = "AnimesOnlineCC"
        
        scraper = discovery_service.scrapers.get(normalized_source)
        if scraper:
            try:
                return await scraper.search(q)
            except Exception as e:
                print(f"Error searching {source}: {e}")
                return []
        else:
             # If passed lowercase/snake_case check manually
             pass

    # Unified search
    return await discovery_service.search_all(q)


@router.get("/episode/link", response_model=str)
async def get_episode_link(url: str, source: str):
    link = ""
    if source == "AnimesHD":
        link = await animes_hd.get_episode_link(url)
    elif source == "AnimesDigital":
        link = await animes_digital.get_episode_link(url)
    elif source == "AnimesOnlineCC":
        link = await animes_online_cc.get_episode_link(url)
    else:
        raise HTTPException(status_code=400, detail="Invalid source")
    
    if not link:
        raise HTTPException(status_code=404, detail="Episode link not found or extraction failed")
        
    return link
@router.get("/anime/play", response_model=Optional[str])
async def quick_play(slug: str, number: str, source: Optional[str] = None):
    """
    Simplified endpoint: Get video link from slug and episode number.
    Source is optional. If omitted, tries to find the anime across all sources.
    """
    video_link = await discovery_service.get_episode_link_smart(slug, number, source)
    
    if not video_link:
        raise HTTPException(status_code=404, detail="Episode or video not found")
        
    return video_link
