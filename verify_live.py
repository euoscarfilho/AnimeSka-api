import requests
import sys

API_URL = "https://animeska-api.onrender.com/api/v1"

def test_flow():
    sources = ["better_animes", "animes_digital", "animes_online_cc"]
    
    for source in sources:
        print(f"\nTesting source: {source}")
        print("Searching for 'Naruto'...")
        try:
            search_resp = requests.get(f"{API_URL}/search", params={"q": "Naruto", "source": source}, timeout=30)
            print(f"Status Code: {search_resp.status_code}")
            
            if search_resp.status_code != 200:
                print(f"Error: {search_resp.text}")
                continue
                
            search_results = search_resp.json()
            
            if not search_results:
                print("No search results found.")
                continue

            first_anime = search_results[0]
            print(f"Found anime: {first_anime['title']}")
            anime_url = first_anime['url']

            # 2. Details
            print(f"Fetching details for {anime_url}...")
            details_resp = requests.get(f"{API_URL}/anime/details", params={"url": anime_url, "source": first_anime['source']}, timeout=30)
            details = details_resp.json()
            
            if not details.get('episodes'):
                print("No episodes found in details.")
                continue

            first_episode = details['episodes'][0]
            print(f"Found episode: {first_episode['title']}")
            episode_url = first_episode['url']

            # 3. Episode Link
            print(f"Fetching link for {episode_url}...")
            link_resp = requests.get(f"{API_URL}/episode/link", params={"url": episode_url, "source": first_anime['source']}, timeout=30)
            video_link = link_resp.json()
            
            print(f"RESULT VIDEO LINK: {video_link}")
            break # Stop if successful

        except Exception as e:
            print(f"Error testing {source}: {e}")

if __name__ == "__main__":
    test_flow()
