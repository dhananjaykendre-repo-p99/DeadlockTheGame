from fastapi import APIRouter
from api import store
from api.models import FlaggedPlayersResponse, FlaggedPlayer

router = APIRouter()

@router.get("/flagged-players", response_model=FlaggedPlayersResponse)
def get_flagged_players():
    """
    Retrieves all flagged suspicious players and their detection reasons.
    """
    flagged_players = []
    
    for p in store.player_profiles:
        if p.get("is_suspicious", False):
            flagged_players.append(FlaggedPlayer(
                player_id=p["player_id"],
                region=p["region"],
                matches_played=p["matches_played"],
                suspicion_reasons=p["suspicion_reasons"]
            ))
            
    return FlaggedPlayersResponse(
        total_flagged=len(flagged_players),
        players=flagged_players
    )
