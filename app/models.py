from pydantic import BaseModel
from typing import List, Optional

class Episode(BaseModel):
    number: str
    url: str
    title: Optional[str] = None
    image: Optional[str] = None

class Anime(BaseModel):
    slug: Optional[str] = None
    title: str
    url: str
    cover_image: Optional[str] = None
    description: Optional[str] = None
    genres: List[str] = []
    year: Optional[str] = None
    status: Optional[str] = None
    season: Optional[str] = None
    source: Optional[str] = None
    episodes: List[Episode] = []
    anilist_id: Optional[int] = None

class SearchResult(BaseModel):
    slug: Optional[str] = None
    title: str
    url: str
    cover_image: Optional[str] = None
    source: str
    year: Optional[str] = None
    # Enrichment fields
    description: Optional[str] = None
    score: Optional[int] = None
    genres: List[str] = []
    status: Optional[str] = None
    anilist_id: Optional[int] = None
