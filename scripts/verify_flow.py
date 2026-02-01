import asyncio
from app.services.discovery import discovery_service

async def verify_flow():
    print(f"\n{'='*50}")
    print(f"STARTING END-TO-END FLOW VERIFICATION")
    print(f"{'='*50}\n")
    
    query = "Jujutsu Kaisen"
    
    # 1. SEARCH & ENRICHMENT
    print(f"[1] Searching for '{query}'...")
    results = await discovery_service.search_all(query)
    
    if not results:
        print("❌ FAILURE: No results found.")
        return

    # Check Enrichment
    # Actually search_all implementation does NOT sort by priority, find_best_match does. 
    # But let's check if the generic search results contain metadata.
    
    enriched_count = sum(1 for r in results if r.description and r.score)
    print(f"[OK] Found {len(results)} results.")
    print(f"[OK] Enriched {enriched_count}/{len(results)} results with Metadata.")
    
    if enriched_count > 0:
        first_enriched = next((r for r in results if r.description and r.score), None)
        if first_enriched:
             print(f"   Example Metadata: Score={first_enriched.score}, Status={first_enriched.status}")
    else:
        print("[WARN] Metadata enrichment might have failed.")

    # 2. PRIORITY CHECK
    print(f"\n[2] Checking Priority (Smart Selection)...")
    best_match = await discovery_service.find_best_match(query)
    
    if best_match:
        print(f"[OK] Best Match Selected: '{best_match.title}'")
        print(f"[OK] Source: {best_match.source}")
        
        if best_match.source == "AnimesDigital":
            print("[SUCCESS] AnimesDigital was correctly prioritized!")
        else:
            print(f"[NOTE] Selected source is {best_match.source} (AnimesDigital might not be available or ranked lower for some reason).")
    else:
        print("[FAIL] No best match found.")
        return

    # 3. SMART PLAYBACK
    print(f"\n[3] Testing Smart Playback (Episode 1)...")
    episode_num = "1"
    # We use the implicit discovery inside get_episode_link_smart
    link = await discovery_service.get_episode_link_smart(query, episode_num)
    
    if link:
        print(f"[OK] Video Link Retrieved Successfully!")
        print(f"   URL: {link}")
    else:
        print("[FAIL] Could not retrieve video link.")

    print(f"\n{'='*50}")
    print(f"FLOW VERIFICATION COMPLETE")
    print(f"{'='*50}")

if __name__ == "__main__":
    asyncio.run(verify_flow())
