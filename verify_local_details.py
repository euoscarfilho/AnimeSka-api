import requests
import json

def verify():
    base_url = "http://localhost:8001/api/v1"
    
    # Hardcode for speed debugging
    ep_url = "https://animeshd.to/episodios/naruto-shippuden-dublado-episodio-196/"
    source = "AnimesHD"
    print(f"Checking episode link for: {ep_url}...")
    try:
        resp = requests.get(f"{base_url}/episode/link", params={"url": ep_url, "source": source})
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            video_url = resp.json()
            print(f"Video URL: {video_url}")
            if video_url and (".mp4" in video_url or ".m3u8" in video_url):
                 print(f"SUCCESS: Direct video URL found: {video_url}")
            else:
                 print(f"WARNING: Video URL found but not direct stream (fallback): {video_url}")
        else:
            print(f"Error Text: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    verify()
