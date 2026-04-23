import requests
import os
from dotenv import load_dotenv

load_dotenv()

HENRIK_API_KEY = os.getenv("HENRIK_API_KEY")
HENRIK_BASE = "https://api.henrikdev.xyz"

def safe_request(url: str) -> dict:
    headers = {
        "Authorization": HENRIK_API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        raise Exception("Henrik API key missing or invalid")
    if response.status_code == 404:
        raise Exception("Player not found — check name/tag/case")
    if response.status_code == 429:
        raise Exception("Rate limit hit — slow down")

    response.raise_for_status()
    return response.json()


def get_player_stats(game_name: str, tag_line: str, region: str = "na") -> dict:
    url = f"{HENRIK_BASE}/valorant/v1/mmr/{region}/{game_name}/{tag_line}"
    return safe_request(url)


def get_match_history(game_name: str, tag_line: str, region: str = "na", count: int = 10):
    count = min(count, 10)
    url = f"{HENRIK_BASE}/valorant/v3/matches/{region}/{game_name}/{tag_line}?size={count}&mode=competitive"
    return safe_request(url).get("data", [])

if __name__ == "__main__":
    game_name = input("Enter your Riot name (without #tag): ")
    tag_line  = input("Enter your tag (without #): ")

    print(f"\nLooking up {game_name}#{tag_line}...")
    stats = get_player_stats(game_name, tag_line)
    print(f"Stats: {stats}")

    print(f"\nFetching last 5 matches via Henrik API...")
    matches = get_match_history(game_name, tag_line, count=5)
    for i, match in enumerate(matches, 1):
        meta = match.get("metadata", {})
        print(f"  {i}. {meta.get('matchid', 'unknown')} — {meta.get('map', '?')} — {meta.get('mode', '?')}")

    print("\nSetup working correctly!")