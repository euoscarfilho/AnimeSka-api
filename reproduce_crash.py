import requests
import json

base_url = "http://localhost:8001/api/v1"
# Known failing URL
anime_url = "https://animeshd.to/animes/naruto-shippuden-dublado/"

print(f"Getting Details for {anime_url}...")
try:
    resp = requests.get(f"{base_url}/anime/details", params={"url": anime_url, "source": "AnimesHD"})
    if resp.status_code != 200:
         print(f"FAIL: {resp.status_code} {resp.text}")
    else:
         print("SUCCESS")
except Exception as e:
    print(e)
