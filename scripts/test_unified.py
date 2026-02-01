import asyncio
from app.services.discovery import discovery_service

async def test_unified_flow():
    # 1. Test Unified Search
    print("\n--- Testing Unified Search ---")
    query = "jujutsu kaisen"
    results = await discovery_service.search_all(query)
    print(f"Found {len(results)} matches for '{query}'")
    for res in results[:5]:
        print(f" - [{res.source}] {res.title} ({res.slug})")
    
    # 2. Test Smart Playback (No Source)
    print("\n--- Testing Smart Playback (No Source) ---")
    slug_query = "jujutsu kaisen"
    episode = "1"
    
    print(f"Attempting to play '{slug_query}' Episode {episode} without specifying source...")
    link = await discovery_service.get_episode_link_smart(slug_query, episode)
    
    if link:
        print(f"SUCCESS: Video Link Found: {link}")
    else:
        print("FAILURE: No video link found.")

    # 3. Test Fallback with imperfect query
    print("\n--- Testing Search Fallback (Imperfect Query) ---")
    query_imperfect = "jujutsu kaisen TV" 
    # Use logic directly
    best_match = await discovery_service.find_best_match(query_imperfect)
    if best_match:
         print(f"Best match for '{query_imperfect}': {best_match.title} from {best_match.source}")
    else:
        print(f"No match found for '{query_imperfect}'")

if __name__ == "__main__":
    asyncio.run(test_unified_flow())
