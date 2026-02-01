
import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000/api/v1"

async def search_and_test():
    query = "Frieren"
    print(f"Searching for '{query}'...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{BASE_URL}/search", params={"q": query})
            
        if resp.status_code != 200:
            print(f"Search failed: {resp.status_code}")
            return
        
        results = resp.json()
        print(f"Found {len(results)} results:")
        for r in results:
            print(f" - [{r.get('source')}] {r.get('title')} (Slug: {r.get('slug')})")

        # By inspection, we look for Season 2
        # Common naming conventions: "Sousou no Frieren 2nd Season", "Sousou no Frieren 2"
        
        target_slug = None
        target_source = None
        
        for r in results:
            title = r.get('title', '').lower()
            if 'frieren' in title and ('2' in title or 'season 2' in title or '2nd season' in title or 'ii' in title):
                 print(f"\nPotential Season 2 Candidate: {r.get('title')}")
                 target_slug = r.get('slug')
                 target_source = r.get('source')
                 break
        
        if not target_slug and results:
             print("\nNo explicit 'Season 2' title found. Checking the first result to see if it mistakenly contains S2 episodes or if we just test the main one.")
             target_slug = results[0].get('slug')
             target_source = results[0].get('source')

        if target_slug:
            print(f"\nFetching details for: {target_slug} on {target_source}")
            
            # Find the search result object again
            target_res = next((r for r in results if r['slug'] == target_slug and r['source'] == target_source), None)
            
            if target_res:
                details_url = f"{BASE_URL}/anime/details"
                params = {"source": target_source, "url": target_res['url']}
                
                resp = await client.get(details_url, params=params)
                details = resp.json()
                print(f"Title: {details.get('title')}")
                print(f"Season: {details.get('season')}")
                print(f"Episodes: {len(details.get('episodes'))}")
                
                if details.get('episodes'):
                    # Check if episodes look like season 2? Or just try ep 1.
                    # Usually if it's a separate entry, Ep 1 is Ep 1.
                    # If it's one huge entry, Ep 1 of S2 might be Ep 29.
                    
                    first_ep = details['episodes'][0]
                    print(f"First Episode: {first_ep}")
                    
                    # Try to play Episode 1
                    print(f"\nAttempting to get video link for Episode 1 (Number: 1)...")
                    play_url = f"{BASE_URL}/anime/play"
                    play_params = {"slug": target_slug, "source": target_source, "number": "1"}
                    
                    # Also try "29" just in case it's continuous
                    
                    play_resp = await client.get(play_url, params=play_params)
                    if play_resp.status_code == 200:
                        link = play_resp.json()
                        print(f"VIDEO LINK (Ep 1): {link}")
                    else:
                        print(f"Failed to get video link for Ep 1: {play_resp.status_code} {play_resp.text}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(search_and_test())
