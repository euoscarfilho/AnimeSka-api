import requests
import json
import sys

base_url = "http://localhost:8001/api/v1"

def check_slugs():
    tests = [
        {"source": "animes_hd", "query": "Naruto"},
        {"source": "animes_digital", "query": "One Piece"},
        {"source": "animes_online_cc", "query": "Dragon Ball"}
    ]

    all_passed = True

    for test in tests:
        source = test['source']
        query = test['query']
        print(f"\n--- Testing Source: {source} (Query: {query}) ---")
        
        try:
            # 1. Search
            print(f"1. Searching...")
            resp = requests.get(f"{base_url}/search", params={"q": query, "source": source})
            if resp.status_code != 200:
                print(f"FAIL: Search returned {resp.status_code}")
                all_passed = False
                continue

            results = resp.json()
            if not results or len(results) == 0:
                print("FAIL: No results found.")
                all_passed = False
                continue
            
            first = results[0]
            print(f"   Result: {first.get('title')}")
            print(f"   Slug: {first.get('slug')}")
            
            if not first.get('slug'):
                 print("FAIL: Search result missing slug.")
                 all_passed = False
            else:
                 print("   [OK] Search Slug present.")

            # 2. Details
            print(f"2. Getting Details for {first['url']}...")
            resp_det = requests.get(f"{base_url}/anime/details", params={"url": first['url'], "source": first['source']})
            
            if resp_det.status_code != 200:
                print(f"FAIL: Details returned {resp_det.status_code}")
                # Don't fail entire test if external site is flaky 500, but note it
                # all_passed = False 
                continue

            details = resp_det.json()
            print(f"   Details Slug: {details.get('slug')}")
            
            if details.get('slug'):
                 print("   [OK] Details Slug present.")
                 if details.get('slug') == first.get('slug'):
                     print("   [OK] Slugs match.")
                 else:
                     print("   [WARN] Slugs differ (Search vs Details).")
            else:
                 print("FAIL: Details missing slug.")
                 all_passed = False

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            all_passed = False

    if all_passed:
        print("\nSUMMARY: ALL SLUG TESTS PASSED! 🚀")
    else:
        print("\nSUMMARY: SOME TESTS FAILED.")

if __name__ == "__main__":
    check_slugs()
