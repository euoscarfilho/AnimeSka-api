import requests
import json
import sys

base_url = "http://localhost:8001/api/v1"

def test_frieren():
    query = "Frieren"
    # We do NOT specify a source here, so the API searches ALL sources
    print(f"--- 1. Searching for '{query}' across ALL sources... ---")
    
    try:
        resp = requests.get(f"{base_url}/search", params={"q": query})
        results = resp.json()
        
        if not results:
            print("FAIL: No results found.")
            return

        print(f"Found {len(results)} results.")
        for i, res in enumerate(results):
             print(f"   [{i}] {res['title']} (Source: {res['source']})")

        # Pick the first result that is "Sousou no Frieren" from AnimesHD for the demo
        selected_anime = next((r for r in results if "Sousou no Frieren" in r['title'] and r['source'] == 'AnimesHD'), results[0])
        
        print(f"\n--- 2. Selected Result ---")
        print(f"   Title: {selected_anime['title']}")
        print(f"   URL: {selected_anime['url']}")
        print(f"   Source Detected: {selected_anime['source']}")  # Highlighting this for the user

        # 3. Details using the DETECTED source
        print(f"\n--- 3. Getting Details (Using Source: {selected_anime['source']})... ---")
        resp_det = requests.get(f"{base_url}/anime/details", params={"url": selected_anime['url'], "source": selected_anime['source']})
        details = resp_det.json()
        
        episodes = details.get('episodes', [])
        print(f"   Found {len(episodes)} episodes.")
        
        if not episodes:
            print("FAIL: No episodes found.")
            return

        # 4. Video Link
        first_ep = episodes[0]
        print(f"\n--- 4. Getting Video Link (Using Source: {selected_anime['source']})... ---")
        print(f"   Episode: {first_ep['title']}")
        
        resp_video = requests.get(f"{base_url}/episode/link", params={"url": first_ep['url'], "source": selected_anime['source']})
        video_url = resp_video.json()
        
        print(f"   Video URL: {video_url}")
        
        if video_url:
             print("\n✅ SUCCESS: Flow confirmed! Search -> Source Detected -> Details -> Video Link")
        else:
             print("\n❌ FAIL: Video link not found.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_frieren()
