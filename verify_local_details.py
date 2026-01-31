import requests
import json

def verify():
    base_url = "http://localhost:8001/api/v1"
    
    # 1. Search for a popular anime
    print("Searching...")
    try:
        resp = requests.get(f"{base_url}/search?q=Naruto&source=animes_hd")
        results = resp.json()
        if not results:
            print("No results")
            return
            
        first = results[0]
        print(f"Checking details for: {first['title']}")
        
        # 2. details
        resp = requests.get(f"{base_url}/anime/details", params={"url": first['url'], "source": "AnimesHD"})
        details = resp.json()
        
        print(json.dumps(details, indent=2, ensure_ascii=False))
        
        if details.get('description'):
            print("SUCCESS: Description found")
        else:
            print("FAIL: Description missing")
            
        if details.get('genres'):
            print(f"SUCCESS: Genres found ({len(details['genres'])})")
        else:
            print("FAIL: Genres missing")

    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    verify()
