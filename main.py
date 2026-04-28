from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from data_processor import process_match_history, compute_summary
from riot_client import get_puuid, get_match_history_cached, get_cache_key
from mangum import Mangum 

# browser permissions

app = FastAPI(
    title="Valorant Dashboard API",
    version="1.0.0",
    root_path="/prod",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8050",
        "https://valorant-dashboard.onrender.com",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
class MatchStats(BaseModel):
    match_id: str | None
    map: str | None
    mode: str | None
    agent: str | None
    kills: int
    deaths: int
    assists: int
    kd_ratio: float
    hs_pct: float
    damage: int
    rounds_played:    int
    damage_per_round: float
    won:              bool

class SummaryStats(BaseModel):
    total_matches: int
    win_rate: float
    avg_kd: float
    avg_hs_pct: float
    avg_damage_per_round: float
    agent_win_rates: dict[str, float]
    map_win_rates: dict[str, float]

class PlayerResponse(BaseModel):
    player: str
    summary: SummaryStats
    matches: list[MatchStats]


# --- endpoints ---

@app.get("/")
def root():
    return {"message": "Valorant Dashboard API is running"}


def _fetch(game_name: str, tag_line: str, count: int) -> list[dict]:
    try:
        puuid = get_puuid(game_name, tag_line)
    except Exception:
        puuid = get_cache_key(game_name, tag_line)
    try:
        return get_match_history_cached(puuid, game_name, tag_line, count=count)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/player/{game_name}/{tag_line}", response_model=PlayerResponse)
def get_player(game_name: str, tag_line: str, count: int = 10):
    matches = _fetch(game_name, tag_line, count)
    if not matches:
        raise HTTPException(status_code=404, detail="No competitive matches found")
    return PlayerResponse(
        player=f"{game_name}#{tag_line}",
        summary=SummaryStats(**compute_summary(matches)),
        matches=[MatchStats(**m) for m in matches],
    )


@app.get("/player/{game_name}/{tag_line}/summary", response_model=SummaryStats)
def get_summary(game_name: str, tag_line: str, count: int = 10):
    matches = _fetch(game_name, tag_line, count)
    if not matches:
        raise HTTPException(status_code=404, detail="No competitive matches found")
    return SummaryStats(**compute_summary(matches))


@app.get("/player/{game_name}/{tag_line}/matches", response_model=list[MatchStats])
def get_matches(game_name: str, tag_line: str, count: int = 10):
    matches = _fetch(game_name, tag_line, count)
    if not matches:
        raise HTTPException(status_code=404, detail="No competitive matches found")
    return [MatchStats(**m) for m in matches]

handler = Mangum(app, lifespan="off")