from fastapi import FastAPI
from api.routes import scores, leaderboard, flagged, matchmaking
from api.store import get_store
from api.models import HealthResponse

app = FastAPI()

app.include_router(scores.router, tags=["Scores"])
app.include_router(leaderboard.router, tags=["Leaderboard"])
app.include_router(flagged.router, tags=["Flagged Players"])
app.include_router(matchmaking.router, tags=["Matchmaking"])

@app.get("/health", response_model=HealthResponse)
def health():
    """
    Checks the status and yields size of stored matches/profiles.
    """
    store_state = get_store()
    return {
        "status": "ok",
        "total_records": len(store_state["match_records"]),
        "total_players": len(store_state["player_profiles"])
    }
