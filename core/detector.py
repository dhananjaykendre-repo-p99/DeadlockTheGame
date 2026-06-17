MAX_SCORE_PER_SEC = 50
MAX_KILLS_PER_MIN = 30
MIN_KILLS_FOR_PERFECT_GAME = 10
HIGH_SCORE_THRESHOLD = 5000
MIN_KILLS_FOR_HIGH_SCORE = 3
MIN_MATCH_DURATION = 120
MAX_SCORE_SHORT_MATCH = 3000
MIN_PING = 5

def detect(match_records: list[dict]) -> tuple[bool, list[str]]:
    """
    Check every match record of a player against the detection rules.
    Returns:
        (is_suspicious, list of suspicion reasons)
    """
    is_suspicious = False
    reasons = []
    
    for record in match_records:
        match_id = record.get("match_id", "Unknown")
        ping = record.get("ping", 0)
        score = record.get("score", 0)
        kills = record.get("kills", 0)
        deaths = record.get("deaths", 0)
        match_duration = record.get("match_duration", 0)
        

        if match_duration > 0:
            score_rate = score / match_duration
            if score_rate > MAX_SCORE_PER_SEC:
                is_suspicious = True
                reasons.append(
                    f"{match_id}: Score rate {score_rate:.1f} pts/sec (threshold: {MAX_SCORE_PER_SEC})"
                )
        elif score > 0:
            is_suspicious = True
            reasons.append(
                f"{match_id}: Score rate infinite (score {score} in 0 seconds)"
            )
            

        if match_duration > 0:
            kill_rate = kills / (match_duration / 60.0)
            if kill_rate > MAX_KILLS_PER_MIN:
                is_suspicious = True
                reasons.append(
                    f"{match_id}: Kill rate {kill_rate:.1f} kills/min (threshold: {MAX_KILLS_PER_MIN})"
                )
        elif kills > 0:
            is_suspicious = True
            reasons.append(
                f"{match_id}: Kill rate infinite (kills {kills} in 0 seconds)"
            )
            

        if kills > MIN_KILLS_FOR_PERFECT_GAME and deaths == 0:
            is_suspicious = True
            reasons.append(
                f"{match_id}: Perfect game with {kills} kills and 0 deaths (threshold: >{MIN_KILLS_FOR_PERFECT_GAME} kills)"
            )
            

        if score > HIGH_SCORE_THRESHOLD and kills < MIN_KILLS_FOR_HIGH_SCORE:
            is_suspicious = True
            reasons.append(
                f"{match_id}: Score kill mismatch with score {score} and {kills} kills (threshold: score >{HIGH_SCORE_THRESHOLD} and kills <{MIN_KILLS_FOR_HIGH_SCORE})"
            )
            

        if match_duration < MIN_MATCH_DURATION and score > MAX_SCORE_SHORT_MATCH:
            is_suspicious = True
            reasons.append(
                f"{match_id}: Short match duration {match_duration}s with high score {score} (threshold: duration <{MIN_MATCH_DURATION}s and score >{MAX_SCORE_SHORT_MATCH})"
            )
            

        if ping < MIN_PING:
            is_suspicious = True
            reasons.append(
                f"{match_id}: Ping anomaly of {ping} ms (threshold: <{MIN_PING})"
            )
            
    return is_suspicious, reasons
