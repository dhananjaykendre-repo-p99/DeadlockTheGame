from fastapi import APIRouter, Query
from api import store
from api.models import LeaderboardResponse, LeaderboardEntry
from core import leaderboard

router = APIRouter()

@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    region: str = Query(None, description="Optional region filter"),
    leaderboard_type: str = Query("global", description="Type of leaderboard: 'global' or 'region'")
):
    """
    Retrieves global or regional standings for all clean players.
    """
    global_lead, region_lead = leaderboard.build_leaderboard(store.player_profiles)
    
    total_clean = sum(1 for p in store.player_profiles if not p.get("is_suspicious", False))
    total_flagged = sum(1 for p in store.player_profiles if p.get("is_suspicious", False))
    
    if region:
        leaderboard_type = "region"
        filtered_lead = [row for row in region_lead if row["region"].lower() == region.lower()]
    elif leaderboard_type == "region":
        filtered_lead = region_lead
    else:
        filtered_lead = global_lead
        

    entries = [
        LeaderboardEntry(
            rank=row["rank"],
            player_id=row["player_id"],
            region=row["region"],
            skill_bracket=row["skill_bracket"],
            total_score=row["total_score"],
            total_kills=row["total_kills"],
            total_deaths=row["total_deaths"],
            matches_played=row["matches_played"],
            global_rank=row["global_rank"],
            region_rank=row["region_rank"]
        ) for row in filtered_lead
    ]
    
    return LeaderboardResponse(
        total_clean_players=total_clean,
        total_flagged_players=total_flagged,
        region_filter=region,
        leaderboard=entries
    )
