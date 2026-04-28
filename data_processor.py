from riot_client import get_match_history, get_player_stats


def extract_player_match_stats(match: dict, game_name: str, tag_line: str) -> dict | None:
    players = match.get("players", {}).get("all_players", [])
    meta = match.get("metadata", {})

    player = next(
        (p for p in players
         if p.get("name", "").lower() == game_name.lower()
         and p.get("tag", "").lower() == tag_line.lower()),
        None
    )

    if not player:
        mode = meta.get("mode", "?")
        print(f"  [SKIP] Match {meta.get('matchid', '?')} — player not found. Mode: {mode}")
        return None

    stats = player.get("stats", {})
    team  = player.get("team", "").lower()

    won = match.get("teams", {}).get(team, {}).get("has_won", False)

    headshots = stats.get("headshots", 0)
    bodyshots = stats.get("bodyshots", 0)
    legshots = stats.get("legshots", 0)
    total_shots = headshots + bodyshots + legshots
    hs_pct = round((headshots / total_shots) * 100, 1) if total_shots > 0 else 0.0

    kills = stats.get("kills", 0)
    deaths = stats.get("deaths", 0)
    assists = stats.get("assists", 0)
    damage = player.get("damage_made", 0)

    # Rounds played — sum both teams' round wins
    teams = match.get("teams", {})
    red_rounds = teams.get("red",  {}).get("rounds_won", 0)
    blue_rounds = teams.get("blue", {}).get("rounds_won", 0)
    rounds = red_rounds + blue_rounds
    damage_per_round = round(damage / rounds, 1) if rounds > 0 else 0.0

    return {
        "match_id": meta.get("matchid"),
        "map": meta.get("map"),
        "mode": meta.get("mode"),
        "agent": player.get("character"),
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kd_ratio": round(kills / deaths, 2) if deaths > 0 else float(kills),
        "hs_pct": hs_pct,
        "damage": damage,
        "rounds_played": rounds,
        "damage_per_round": damage_per_round,
        "won": won,
    }

def process_match_history(game_name: str, tag_line: str, count: int = 10) -> list[dict]:
    # gets last n comp matches
    raw_matches = get_match_history(game_name, tag_line, count=count)
    processed = []

    for match in raw_matches:
        mode = match.get("metadata", {}).get("mode", "").lower()
        if mode != "competitive":
            print(f"  [SKIP] Skipping {mode} match")
            continue

        stats = extract_player_match_stats(match, game_name, tag_line)
        if stats:
            processed.append(stats)

    return processed

def compute_summary(matches: list[dict]) -> dict:
    if not matches:
        return {}

    total = len(matches)
    wins  = sum(1 for m in matches if m["won"])

    avg_kd             = round(sum(m["kd_ratio"] for m in matches) / total, 2)
    avg_hs             = round(sum(m["hs_pct"]   for m in matches) / total, 1)
    avg_damage_per_round = round(sum(m["damage_per_round"] for m in matches) / total, 1)
    win_rate           = round((wins / total) * 100, 1)

    agent_stats: dict[str, dict] = {}
    for m in matches:
        agent = m["agent"] or "Unknown"
        if agent not in agent_stats:
            agent_stats[agent] = {"wins": 0, "games": 0}
        agent_stats[agent]["games"] += 1
        if m["won"]:
            agent_stats[agent]["wins"] += 1

    agent_win_rates = {
        agent: round((d["wins"] / d["games"]) * 100, 1)
        for agent, d in agent_stats.items()
    }

    map_stats: dict[str, dict] = {}
    for m in matches:
        map_name = m["map"] or "Unknown"
        if map_name not in map_stats:
            map_stats[map_name] = {"wins": 0, "games": 0}
        map_stats[map_name]["games"] += 1
        if m["won"]:
            map_stats[map_name]["wins"] += 1

    map_win_rates = {
        map_name: round((d["wins"] / d["games"]) * 100, 1)
        for map_name, d in map_stats.items()
    }

    return {
        "total_matches": total,
        "win_rate": win_rate,
        "avg_kd": avg_kd,
        "avg_hs_pct": avg_hs,
        "avg_damage_per_round": avg_damage_per_round,
        "agent_win_rates": agent_win_rates,
        "map_win_rates": map_win_rates,
    }

if __name__ == "__main__":
    game_name = input("Enter your Riot name (without #tag): ")
    tag_line  = input("Enter your tag (without #): ")

    print(f"\nProcessing last 10 matches for {game_name}#{tag_line}...")
    matches = process_match_history(game_name, tag_line, count=20)

    print(f"Successfully processed {len(matches)} matches\n")

    print("--- Per-match breakdown ---")
    for m in matches:
        result = "WIN" if m["won"] else "LOSS"
        print(f"  [{result}] {m['map']} | {m['agent']} | "
              f"K/D: {m['kd_ratio']} | HS%: {m['hs_pct']}% | DMG: {m['damage']}")

    print("\n--- Summary stats ---")
    summary = compute_summary(matches)
    print(f"  Win rate:      {summary['win_rate']}%")
    print(f"  Avg K/D:       {summary['avg_kd']}")
    print(f"  Avg HS%:       {summary['avg_hs_pct']}%")
    print(f"  Avg damage:    {summary['avg_damage']}")
    print(f"\n  Agent win rates: {summary['agent_win_rates']}")
    print(f"  Map win rates:   {summary['map_win_rates']}")