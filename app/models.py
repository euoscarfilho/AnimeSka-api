from pydantic import BaseModel
from typing import List, Optional

class Episode(BaseModel):
    number: str
    url: str
    title: Optional[str] = None

class Anime(BaseModel):
    title: str
    url: str
    cover_image: Optional[str] = None
    episodes: List[Episode] = []

class SearchResult(BaseModel):
    title: str
    url: str
    cover_image: Optional[str] = None
    source: str
