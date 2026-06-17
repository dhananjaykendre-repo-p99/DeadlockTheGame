from pydantic import BaseModel

class MatchRecord(BaseModel):
    player_id: str
    match_id: str
    region: str
    device: str
    ping: int
    score: int
    kills: int
    deaths: int
    match_duration: int

class SubmitScoresRequest(BaseModel):
    records: list[MatchRecord]

class SubmitScoresResponse(BaseModel):
    message: str
    records_received: int
    players_processed: int
    flagged_players: int

class LeaderboardEntry(BaseModel):
    rank: int
    player_id: str
    region: str
    skill_bracket: str
    total_score: int
    total_kills: int
    total_deaths: int
    matches_played: int
    global_rank: int
    region_rank: int

class LeaderboardResponse(BaseModel):
    total_clean_players: int
    total_flagged_players: int
    region_filter: str | None
    leaderboard: list[LeaderboardEntry]

class FlaggedPlayer(BaseModel):
    player_id: str
    region: str
    matches_played: int
    suspicion_reasons: list[str]

class FlaggedPlayersResponse(BaseModel):
    total_flagged: int
    players: list[FlaggedPlayer]

class MatchGroup(BaseModel):
    group_id: str
    region: str
    bracket: str
    ping_range: str
    players: list[str]

class WaitingEntry(BaseModel):
    player_id: str
    region: str
    bracket: str
    reason: str

class MatchmakingResponse(BaseModel):
    total_groups: int
    waiting_pool_count: int
    groups: list[MatchGroup]
    waiting_pool: list[WaitingEntry]

class HealthResponse(BaseModel):
    status: str
    total_records: int
    total_players: int

class ResetResponse(BaseModel):
    message: str
