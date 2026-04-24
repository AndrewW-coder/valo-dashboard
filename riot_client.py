import requests
import os
from dotenv import load_dotenv
from cache import cache_matches, get_cached_matches, is_match_cached

load_dotenv()

HENRIK_API_KEY = os.getenv("HENRIK_API_KEY")
HENRIK_BASE = "https://api.henrikdev.xyz"


def safe_request(url: str) -> dict:
    headers = {"Authorization": HENRIK_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        raise Exception("API key missing or invalid")
    if response.status_code == 404:
        raise Exception("Player not found, check name, tag, and capitalization")
    if response.status_code == 429:
        raise Exception("Rate limit hit")
    response.raise_for_status()
    return response.json()


def get_puuid(game_name: str, tag_line: str) -> str:
    url = f"{HENRIK_BASE}/valorant/v1/account/{game_name}/{tag_line}"
    response = safe_request(url)
    return response["data"]["puuid"]

def get_cache_key(game_name: str, tag_line: str) -> str:
    return f"{game_name.lower()}#{tag_line.lower()}"


def get_player_stats(game_name: str, tag_line: str, region: str = "na") -> dict:
    url = f"{HENRIK_BASE}/valorant/v1/mmr/{region}/{game_name}/{tag_line}"
    return safe_request(url)


def get_match_history(game_name: str, tag_line: str, region: str = "na", count: int = 10):
    count = min(count, 10)
    url = f"{HENRIK_BASE}/valorant/v3/matches/{region}/{game_name}/{tag_line}?size={count}&mode=competitive"
    return safe_request(url).get("data", [])


def get_match_history_cached(puuid: str, game_name: str, tag_line: str, count: int = 10) -> list[dict]:
    from data_processor import process_match_history

    cached = get_cached_matches(puuid)
    if cached:
        print(f"[CACHE HIT] Returning {len(cached)} matches from DynamoDB")
        return cached

    print(f"[CACHE MISS] Fetching from Henrik API...")
    matches = process_match_history(game_name, tag_line, count=count)
    cache_matches(puuid, matches)
    return matches