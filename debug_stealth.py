import playwright_stealth
print(f"Package dir: {dir(playwright_stealth)}")

from playwright_stealth import stealth
print(f"Item 'stealth' type: {type(stealth)}")
print(f"Item 'stealth' dir: {dir(stealth)}")

try:
    from playwright_stealth import stealth_sync
    print("Found stealth_sync")
except ImportError:
    print("stealth_sync not found directly")

try:
    from playwright_stealth.stealth import stealth_sync
    print("Found stealth_sync in .stealth")
except ImportError:
    print("stealth_sync not found in .stealth")
