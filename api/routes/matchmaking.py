from fastapi import APIRouter, Query
from api import store
from api.models import MatchmakingResponse, MatchGroup, WaitingEntry
from core import matchmaking

router = APIRouter()

@router.get("/matchmaking", response_model=MatchmakingResponse)
def get_matchmaking(
    region: str = Query(None, description="Optional region filter"),
    bracket: str = Query(None, description="Optional bracket filter")
):
    """
    Generates matchmaking groups and waiting pools, applying optional filters.
    """
    groups, waiting_pool = matchmaking.build_groups(store.player_profiles)
    

    if region:
        groups = [g for g in groups if g["region"].lower() == region.lower()]
        waiting_pool = [w for w in waiting_pool if w["region"].lower() == region.lower()]
        
    if bracket:
        groups = [g for g in groups if g["bracket"].lower() == bracket.lower()]
        waiting_pool = [w for w in waiting_pool if w["bracket"].lower() == bracket.lower()]
        

    match_groups = [
        MatchGroup(
            group_id=g["group_id"],
            region=g["region"],
            bracket=g["bracket"],
            ping_range=g["ping_range"],
            players=g["players"]
        ) for g in groups
    ]
    
    waiting_entries = [
        WaitingEntry(
            player_id=w["player_id"],
            region=w["region"],
            bracket=w["bracket"],
            reason=w["reason"]
        ) for w in waiting_pool
    ]
    
    return MatchmakingResponse(
        total_groups=len(match_groups),
        waiting_pool_count=len(waiting_entries),
        groups=match_groups,
        waiting_pool=waiting_entries
    )
