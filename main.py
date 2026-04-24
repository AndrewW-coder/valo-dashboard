from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from data_processor import process_match_history, compute_summary

# browser permissions

app = FastAPI(title="Valorant Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- json format responses ---

class MatchStats(BaseModel):
    match_id:  str | None
    map:       str | None
    mode:      str | None
    agent:     str | None
    kills:     int
    deaths:    int
    assists:   int
    kd_ratio:  float
    hs_pct:    float
    damage:    int
    won:       bool

class SummaryStats(BaseModel):
    total_matches:   int
    win_rate:        float
    avg_kd:          float
    avg_hs_pct:      float
    avg_damage:      float
    agent_win_rates: dict[str, float]
    map_win_rates:   dict[str, float]

class PlayerResponse(BaseModel):
    player:  str
    summary: SummaryStats
    matches: list[MatchStats]


# --- endpoints ---

@app.get("/")
def root():
    return {"message": "Valorant Dashboard API is running"}


@app.get("/player/{game_name}/{tag_line}", response_model=PlayerResponse)
def get_player(game_name: str, tag_line: str, count: int = 10):
    try:
        matches = process_match_history(game_name, tag_line, count=count)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="No competitive matches found for this player"
        )

    summary = compute_summary(matches)

    return PlayerResponse(
        player=f"{game_name}#{tag_line}",
        summary=SummaryStats(**summary),
        matches=[MatchStats(**m) for m in matches],
    )


@app.get("/player/{game_name}/{tag_line}/summary", response_model=SummaryStats)
def get_summary(game_name: str, tag_line: str, count: int = 10):
    try:
        matches = process_match_history(game_name, tag_line, count=count)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="No competitive matches found for this player"
        )

    return SummaryStats(**compute_summary(matches))


@app.get("/player/{game_name}/{tag_line}/matches", response_model=list[MatchStats])
def get_matches(game_name: str, tag_line: str, count: int = 10):
    try:
        matches = process_match_history(game_name, tag_line, count=count)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="No competitive matches found for this player"
        )

    return [MatchStats(**m) for m in matches]