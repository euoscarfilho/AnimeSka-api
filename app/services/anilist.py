import aiohttp
from typing import Optional, Dict, Any

class AniListService:
    def __init__(self):
        self.url = "https://graphql.anilist.co"

    async def search_anime(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Search for an anime by title on AniList.
        Returns the first match with details.
        """
        query_gql = """
        query ($search: String) {
          Media (search: $search, type: ANIME) {
            id
            title {
              romaji
              english
              native
            }
            description
            coverImage {
              large
              medium
            }
            averageScore
            genres
            status
            season
            seasonYear
            episodes
          }
        }
        """
        
        variables = {
            'search': query
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.url, json={'query': query_gql, 'variables': variables}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('data', {}).get('Media')
                    else:
                        print(f"AniList API Error: {resp.status}")
                        return None
            except Exception as e:
                print(f"Error querying AniList: {e}")
                return None

    async def get_anime_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        query_gql = """
        query ($id: Int) {
          Media (id: $id, type: ANIME) {
            id
            title {
              romaji
              english
              native
            }
            description
            coverImage {
              large
            }
            averageScore
            genres
          }
        }
        """
        variables = {'id': id}
        async with aiohttp.ClientSession() as session:
             try:
                async with session.post(self.url, json={'query': query_gql, 'variables': variables}) as resp:
                    if resp.status == 200:
                         data = await resp.json()
                         return data.get('data', {}).get('Media')
                    return None
             except Exception:
                 return None

anilist_service = AniListService()
