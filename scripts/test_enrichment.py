import asyncio
from app.services.discovery import discovery_service

async def test_enrichment():
    print("--- Testing Search Enrichment ---")
    query = "Jujutsu Kaisen"
    
    results = await discovery_service.search_all(query)
    
    print(f"Found {len(results)} results.")
    
    enriched_count = 0
    for res in results:
        is_enriched = res.description is not None or res.score is not None
        status_str = "[ENRICHED]" if is_enriched else "[RAW]"
        if is_enriched: enriched_count += 1
        
        print(f"{status_str} {res.title} ({res.source})")
        if is_enriched:
            print(f"    Score: {res.score}")
            print(f"    Status: {res.status}")
            print(f"    Desc: {res.description[:50]}..." if res.description else "    Desc: None")

    if enriched_count > 0:
        print(f"\nSUCCESS: {enriched_count} results were enriched with AniList metadata.")
    else:
        print("\nFAILURE: No results were enriched.")

if __name__ == "__main__":
    asyncio.run(test_enrichment())
