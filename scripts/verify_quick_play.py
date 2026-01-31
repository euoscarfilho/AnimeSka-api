import requests

base_url = "http://localhost:8001/api/v1"

def test_quick_play():
    # Frieren Episódio 1 on AnimesHD
    slug = "sousou-no-frieren"
    source = "AnimesHD"
    number = "1"
    
    print(f"--- Testing Quick Play: {slug} Ep {number} ({source}) ---")
    
    try:
        url = f"{base_url}/anime/play"
        params = {"slug": slug, "source": source, "number": number}
        print(f"Calling: {url}")
        
        resp = requests.get(url, params=params)
        
        if resp.status_code == 200:
            video_link = resp.json()
            if video_link:
                print(f"SUCCESS: Received Video Link -> {video_link[:100]}...")
            else:
                print(f"OK: Endpoint returned successfully but no video link was extracted (None).")
        else:
            print(f"FAIL: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_quick_play()
