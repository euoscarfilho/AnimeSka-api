from abc import ABC, abstractmethod
from typing import List, Optional
from app.models import Anime, Episode, SearchResult

class BaseScraper(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url

    @abstractmethod
    async def search(self, query: str) -> List[SearchResult]:
        """Search for an anime."""
        pass

    @abstractmethod
    async def get_details(self, anime_url: str) -> Anime:
        """Get details of a specific anime."""
        pass
    
    @abstractmethod
    async def get_episode_link(self, episode_url: str) -> str:
        """Get the direct video link or embed for an episode."""
        pass

    @abstractmethod
    def get_anime_url(self, slug: str) -> str:
        """Reconstruct the anime URL from a slug."""
        pass
