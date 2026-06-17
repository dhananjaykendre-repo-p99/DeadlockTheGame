from fastapi import APIRouter
import pandas as pd
import io
from api import store
from api.models import SubmitScoresRequest, SubmitScoresResponse, ResetResponse
from core import data_loader

router = APIRouter()

@router.post("/submit-scores", response_model=SubmitScoresResponse)
def submit_scores(request: SubmitScoresRequest):
    """
    Submits score records to the store, aggregates player profiles, 
    and updates player profiles in the shared state.
    """
    new_records = [record.model_dump() for record in request.records]
    store.match_records.extend(new_records)
    

    df = pd.DataFrame(store.match_records)
    if "match_duration" in df.columns:
        df = df.rename(columns={"match_duration": "match_duration_seconds"})
        
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    csv_buf.seek(0)
    
    profiles = data_loader.load_data(csv_buf)
    
    store.player_profiles.clear()
    store.player_profiles.extend(profiles)
    
    records_received = len(request.records)
    players_processed = len(profiles)
    flagged_players = sum(1 for p in profiles if p.get("is_suspicious", False))
    
    return SubmitScoresResponse(
        message="Scores submitted and processed successfully.",
        records_received=records_received,
        players_processed=players_processed,
        flagged_players=flagged_players
    )

@router.delete("/reset", response_model=ResetResponse)
def reset():
    """
    Resets the in-memory store, clearing match records and player profiles.
    """
    store.reset_store()
    return ResetResponse(message="Store state reset successfully.")
