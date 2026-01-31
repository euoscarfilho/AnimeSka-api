import requests
import json
import time

BASE_URL = "http://localhost:8001/api/v1"

def test_source(source_name, search_query):
    print(f"\n--- Testing Source: {source_name} ---")
    
    # 1. Search
    print(f"1. Searching for '{search_query}'...")
    try:
        resp = requests.get(f"{BASE_URL}/search", params={"q": search_query, "source": source_name})
        results = resp.json()
    except Exception as e:
        print(f"FAIL: Search exception: {e}")
        return

    if not results:
        print(f"FAIL: No results found for {search_query}")
        return
    
    print(f"SUCCESS: Found {len(results)} results")
    first = results[0]
    print(f"   Selected: {first['title']} ({first['url']})")

    # 2. Details
    print("2. Getting Details...")
    try:
        resp = requests.get(f"{BASE_URL}/anime/details", params={"url": first['url'], "source": first['source']})
        if resp.status_code != 200:
             print(f"FAIL: Details status {resp.status_code}: {resp.text}")
             return
        details = resp.json()
    except Exception as e:
        print(f"FAIL: Details exception: {e}")
        return

    # Check rich fields
    fields = ["description", "genres", "season", "year", "status"]
    for f in fields:
        val = details.get(f)
        if val:
             print(f"   [x] {f}: {str(val)[:50]}...")
        else:
             print(f"   [ ] {f} MISSING")

    # 3. Episode Link
    if details.get('episodes') and len(details['episodes']) > 0:
        ep = details['episodes'][0]
        print(f"3. Getting Video Link for episode: {ep['title']}...")
        try:
            # Note: Endpoint is /episode/link based on previous fix
            resp = requests.get(f"{BASE_URL}/episode/link", params={"url": ep['url'], "source": details['source']})
            if resp.status_code == 200:
                video_url = resp.json()
                if video_url:
                    print(f"   Video URL: {video_url}")
                    if ".mp4" in video_url or ".m3u8" in video_url or "blogger" in video_url:
                         print(f"SUCCESS: Valid video URL found.")
                    else:
                         print(f"WARNING: Video URL might be an iframe/page: {video_url}")
                else:
                    print("FAIL: Video URL is empty")
            else:
                 print(f"FAIL: Video link status {resp.status_code}")
        except Exception as e:
             print(f"FAIL: Video link exception: {e}")
    else:
        print("FAIL: No episodes found to test")

if __name__ == "__main__":
    # Test each source with a query likely to exist
    test_source("animes_hd", "Naruto")
    test_source("animes_digital", "One Piece")
    # animes_online_cc usually expects specific formatting or broad search
    test_source("animes_online_cc", "Dragon Ball")
