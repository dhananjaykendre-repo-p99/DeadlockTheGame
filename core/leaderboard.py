def build_leaderboard(players: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Builds global and region-wise leaderboards.
    Returns:
        (global_leaderboard, region_leaderboard)
    Rules:
        - Only include players where is_suspicious == False
        - Sort by: total_score DESC -> matches_played ASC -> total_deaths ASC
        - Assign global rank (Olympic style: same rank for ties, skip next rank)
        - For region leaderboard: same sorting logic but independently per region
        - Each row includes: rank, player_id, region, skill_bracket, total_score,
          total_kills, total_deaths, matches_played, global_rank, region_rank
    """
    clean_players = [p for p in players if not p.get("is_suspicious", False)]
    
    sorted_global_players = sorted(
        clean_players,
        key=lambda x: (-x["total_score"], x["matches_played"], x["total_deaths"])
    )
    
    prev_key = None
    rank_to_assign = 1
    for i, p in enumerate(sorted_global_players):
        curr_key = (p["total_score"], p["matches_played"], p["total_deaths"])
        if i > 0 and curr_key == prev_key:
            pass
        else:
            rank_to_assign = i + 1
        p["global_rank"] = rank_to_assign
        prev_key = curr_key
        
    region_groups = {}
    for p in clean_players:
        r = p["region"]
        if r not in region_groups:
            region_groups[r] = []
        region_groups[r].append(p)
        
    for region, r_players in region_groups.items():
        sorted_region_players = sorted(
            r_players,
            key=lambda x: (-x["total_score"], x["matches_played"], x["total_deaths"])
        )
        prev_key = None
        rank_to_assign = 1
        for i, p in enumerate(sorted_region_players):
            curr_key = (p["total_score"], p["matches_played"], p["total_deaths"])
            if i > 0 and curr_key == prev_key:
                pass
            else:
                rank_to_assign = i + 1
            p["region_rank"] = rank_to_assign
            prev_key = curr_key
            
    global_leaderboard = []
    for p in sorted_global_players:
        global_leaderboard.append({
            "rank": p["global_rank"],
            "player_id": p["player_id"],
            "region": p["region"],
            "skill_bracket": p["skill_bracket"],
            "total_score": p["total_score"],
            "total_kills": p["total_kills"],
            "total_deaths": p["total_deaths"],
            "matches_played": p["matches_played"],
            "global_rank": p["global_rank"],
            "region_rank": p.get("region_rank", 1)
        })
        
    sorted_region_all = sorted(
        clean_players,
        key=lambda x: (x["region"], x.get("region_rank", 1))
    )
    
    region_leaderboard = []
    for p in sorted_region_all:
        region_leaderboard.append({
            "rank": p.get("region_rank", 1),
            "player_id": p["player_id"],
            "region": p["region"],
            "skill_bracket": p["skill_bracket"],
            "total_score": p["total_score"],
            "total_kills": p["total_kills"],
            "total_deaths": p["total_deaths"],
            "matches_played": p["matches_played"],
            "global_rank": p["global_rank"],
            "region_rank": p.get("region_rank", 1)
        })
        
    return global_leaderboard, region_leaderboard
