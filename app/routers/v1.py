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
