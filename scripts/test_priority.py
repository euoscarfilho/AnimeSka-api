import asyncio
from app.services.discovery import discovery_service

async def test_priority():
    print("--- Testing Source Priority ---")
    query = "Jujutsu Kaisen"
    
    # 1. Search and inspect order
    results = await discovery_service.search_all(query)
    best_match = await discovery_service.find_best_match(query)
    
    print(f"Total results: {len(results)}")
    
    if best_match:
        print(f"Best Match Source: {best_match.source}")
        print(f"Best Match Title: {best_match.title}")
        
        if best_match.source == "AnimesDigital":
            print("SUCCESS: AnimesDigital was prioritized.")
        else:
            print(f"FAILURE: Expected AnimesDigital but got {best_match.source}")
    else:
        print("FAILURE: No match found.")

if __name__ == "__main__":
    asyncio.run(test_priority())
