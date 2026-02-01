from typing import List, Optional, Tuple
from app.scrapers.animes_hd import AnimesHDScraper
from app.scrapers.animes_digital import AnimesDigitalScraper
from app.scrapers.animes_online_cc import AnimesOnlineCCScraper
from app.services.anilist import anilist_service
from app.models import SearchResult, Anime, Episode

class DiscoveryService:
    def __init__(self):
        self.scrapers = {
            "AnimesHD": AnimesHDScraper(),
            "AnimesDigital": AnimesDigitalScraper(),
            "AnimesOnlineCC": AnimesOnlineCCScraper()
        }

    async def search_all(self, query: str) -> List[SearchResult]:
        """
        Search all providers and aggregate results.
        Also queries AniList for metadata enrichment.
        """
        results = []
        
        # Parallelize scraper searches
        import asyncio
        tasks = [scraper.search(query) for scraper in self.scrapers.values()]
        scraper_results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        for name, res_or_exc in zip(self.scrapers.keys(), scraper_results_list):
            if isinstance(res_or_exc, list):
                for res in res_or_exc:
                     if not res.source: res.source = name
                     results.extend(res_or_exc)
                     break # Only extend once per list
            else:
                print(f"Error searching {name}: {res_or_exc}")

        # Fetch AniList metadata
        # Clean query for better AniList matching (remove "Dublado", "Legendado", etc.)
        import re
        clean_query = re.sub(r'\b(dublado|legendado|filme|movie|tv|season|ova|special|especial)\b', '', query, flags=re.IGNORECASE).strip()
        # Also remove typical scraper prefixes/suffixes if present (though query usually comes from user)
        
        # If query becomes empty (e.g. user searched just "Dublado"), fallback to original
        if not clean_query:
            clean_query = query
            
        anilist_data = await anilist_service.search_anime(clean_query)
        
        # Enrich results if metadata found
        if anilist_data:
             romaji = anilist_data.get('title', {}).get('romaji', '')
             english = anilist_data.get('title', {}).get('english', '')
             description = anilist_data.get('description', '')
             score = anilist_data.get('averageScore')
             genres = anilist_data.get('genres', [])
             status = anilist_data.get('status')
             cover = anilist_data.get('coverImage', {}).get('large')
             
             # Enrich heuristic: if result title contains query or matches AniList title
             # (Naive matching for now, can be improved)
             for res in results:
                 # Clean descriptions often contain HTML breaks
                 clean_desc = description.replace('<br>', '\n') if description else None
                 
                 res.description = clean_desc
                 res.score = score
                 res.genres = genres
                 res.status = status
                 res.anilist_id = anilist_data.get('id')
                 if not res.cover_image and cover:
                     res.cover_image = cover
                     
        return results

    async def find_best_match(self, query: str) -> Optional[SearchResult]:
        """
        Finds the best matching anime across all sources.
        Simple heuristic: Priority to exact string match > partial match.
        Prioritizes AnimesDigital > AnimesHD > AnimesOnlineCC.
        """
        results = await self.search_all(query)
        if not results:
            return None

        # Sort results by source priority: AnimesDigital first
        # We can use a custom key
        def source_priority(res: SearchResult) -> int:
            if res.source == "AnimesDigital": return 0
            if res.source == "AnimesHD": return 1
            if res.source == "AnimesOnlineCC": return 2
            return 3
        
        results.sort(key=source_priority)
            
        # 1. Exact match (case insensitive)
        for res in results:
            if res.title.lower() == query.lower():
                return res
        
        # 2. Contains match (prioritize shorter titles as likely main series)
        # Filter where query is substring
        candidates = [r for r in results if query.lower() in r.title.lower()]
        if candidates:
            # Sort by title length (shortest title often matches "Jujutsu Kaisen" vs "Jujutsu Kaisen 2")
            # But keep stable sort regarding source priority (since we sorted results above, 
            # and Python sort is stable, if lengths are equal, source priority is preserved)
            candidates.sort(key=lambda x: len(x.title))
            return candidates[0]
            
        # 3. Fallback: First result (which is now best source)
        return results[0]

    async def get_episode_link_smart(self, slug_or_query: str, episode_number: str, source: Optional[str] = None) -> Optional[str]:
        """
        Smart playback finder.
        If source is provided, uses it directly.
        If not, searches for the anime, picks best match, and tries to find episode.
        """
        target_scraper = None
        anime_url = ""
        
        if source and source in self.scrapers:
            target_scraper = self.scrapers[source]
            # Assume slug is correct for that source
            anime_url = target_scraper.get_anime_url(slug_or_query)
        else:
            # Discovery mode
            best_match = await self.find_best_match(slug_or_query)
            if not best_match:
                print(f"No anime found for query: {slug_or_query}")
                return None
            
            print(f"Discovery found: {best_match.title} from {best_match.source}")
            target_scraper = self.scrapers.get(best_match.source)
            anime_url = best_match.url

        if not target_scraper:
            return None

        try:
            details = await target_scraper.get_details(anime_url)
            if not details or not details.episodes:
                return None

            # Find episode
            episode = next((ep for ep in details.episodes if ep.number == episode_number), None)
            if not episode:
                # Fuzzy match for numbers like "01" vs "1"
                episode = next((ep for ep in details.episodes if ep.number.lstrip('0') == episode_number.lstrip('0')), None)
            
            if episode:
                print(f"Found episode {episode.number}: {episode.url}")
                return await target_scraper.get_episode_link(episode.url)
            else:
                print(f"Episode {episode_number} not found in {details.title}")
                return None

        except Exception as e:
            print(f"Error in smart link retrieval: {e}")
            return None

discovery_service = DiscoveryService()
