match_records: list[dict] = []
player_profiles: list[dict] = []

def get_store() -> dict:
    """
    Returns current store state.
    """
    return {
        "match_records": match_records,
        "player_profiles": player_profiles
    }

def reset_store():
    """
    Clears both lists.
    """
    global match_records, player_profiles
    match_records.clear()
    player_profiles.clear()
