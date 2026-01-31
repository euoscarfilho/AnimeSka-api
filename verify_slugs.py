import requests
import json

base_url = "http://localhost:8001/api/v1"

def check_slugs():
    # 1. Search
    print("Searching for 'Naruto'...")
    try:
        resp = requests.get(f"{base_url}/search", params={"q": "Naruto", "source": "animes_hd"})
        results = resp.json()
        if results and len(results) > 0:
            first = results[0]
            print(f"First result: {first.get('title')}")
            print(f"Slug: {first.get('slug')}")
            
            if first.get('slug'):
                 print("SUCCESS: Search result has slug.")
                 
                 # 2. Details
                 print(f"Getting details for {first['url']}...")
                 resp_det = requests.get(f"{base_url}/anime/details", params={"url": first['url'], "source": "AnimesHD"})
                 details = resp_det.json()
                 print(f"Details Slug: {details.get('slug')}")
                 if details.get('slug'):
                      print("SUCCESS: Details has slug.")
                 else:
                      print("FAIL: Details missing slug.")
            else:
                 print("FAIL: Search result missing slug.")
        else:
            print("No results found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_slugs()
