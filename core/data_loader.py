import pandas as pd
from collections import Counter

try:
    from core import detector
except ImportError:
    import detector

SEEKER_MAX_EXCLUSIVE = 5000
ORACLE_MAX_INCLUSIVE = 15000

def load_data(file) -> list[dict]:
    """
    Loads data from the uploaded file-like object or file path, cleans it,
    aggregates it into PlayerProfile dicts, runs detector checks,
    and returns a list of profiles.
    """
    try:
        df = pd.read_csv(file)
    except Exception:
        return []
    
    required_cols = [
        "player_id", "match_id", "region", "device", 
        "ping", "score", "kills", "deaths", "match_duration_seconds"
    ]
    
    if not all(col in df.columns for col in required_cols):
        return []
        
    df = df.dropna(subset=required_cols)
    
    numeric_cols = ["ping", "score", "kills", "deaths", "match_duration_seconds"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    df = df.dropna(subset=numeric_cols)
    
    df["ping"] = df["ping"].astype(int)
    df["score"] = df["score"].astype(int)
    df["kills"] = df["kills"].astype(int)
    df["deaths"] = df["deaths"].astype(int)
    df["match_duration_seconds"] = df["match_duration_seconds"].astype(int)
    
    grouped = df.groupby("player_id")
    player_profiles = []
    
    for player_id, group in grouped:
        match_records = []
        for _, row in group.iterrows():
            match_records.append({
                "player_id": str(row["player_id"]),
                "match_id": str(row["match_id"]),
                "region": str(row["region"]),
                "device": str(row["device"]),
                "ping": int(row["ping"]),
                "score": int(row["score"]),
                "kills": int(row["kills"]),
                "deaths": int(row["deaths"]),
                "match_duration": int(row["match_duration_seconds"])
            })
            
        regions = [m["region"] for m in match_records if m["region"]]
        region = Counter(regions).most_common(1)[0][0] if regions else "Unknown"
        
        devices = [m["device"] for m in match_records if m["device"]]
        device = Counter(devices).most_common(1)[0][0] if devices else "Unknown"
        
        avg_ping = sum(m["ping"] for m in match_records) / len(match_records) if match_records else 0.0
        total_score = sum(m["score"] for m in match_records)
        total_kills = sum(m["kills"] for m in match_records)
        total_deaths = sum(m["deaths"] for m in match_records)
        matches_played = len(match_records)
        
        total_match_duration = sum(m["match_duration"] for m in match_records)
        avg_score_per_second = total_score / total_match_duration if total_match_duration > 0 else 0.0
        
        is_suspicious, suspicion_reasons = detector.detect(match_records)
        
        if total_score < SEEKER_MAX_EXCLUSIVE:
            skill_bracket = "Seeker"
        elif total_score <= ORACLE_MAX_INCLUSIVE:
            skill_bracket = "Oracle"
        else:
            skill_bracket = "Eternus"
            
        player_profiles.append({
            "player_id": str(player_id),
            "region": region,
            "device": device,
            "avg_ping": avg_ping,
            "total_score": total_score,
            "total_kills": total_kills,
            "total_deaths": total_deaths,
            "matches_played": matches_played,
            "avg_score_per_second": avg_score_per_second,
            "skill_bracket": skill_bracket,
            "is_suspicious": is_suspicious,
            "suspicion_reasons": suspicion_reasons
        })
        
    return player_profiles
