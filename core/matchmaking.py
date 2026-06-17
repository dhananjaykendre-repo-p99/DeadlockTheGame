SEEKER_MAX = 5000
ORACLE_MAX = 15000
PING_THRESHOLD = 80
MAX_PING_VARIANCE = 100
GROUP_SIZE = 4

def build_groups(players: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Groups clean players into matchmaking teams of size 4 based on region,
    bracket, and ping variance checks. Returns (groups, waiting_pool).
    """
    clean_players = [p for p in players if not p.get("is_suspicious", False)]
    
    region_groups = {}
    for p in clean_players:
        reg = p["region"]
        if reg not in region_groups:
            region_groups[reg] = []
        region_groups[reg].append(p)
        
    groups = []
    waiting_pool = []
    group_counter = 1
    
    for region in sorted(region_groups.keys()):
        r_players = region_groups[region]
        
        bracket_groups = {"Seeker": [], "Oracle": [], "Eternus": []}
        for p in r_players:
            br = p["skill_bracket"]
            if br in bracket_groups:
                bracket_groups[br].append(p)
                
        for bracket in ["Seeker", "Oracle", "Eternus"]:
            b_players = bracket_groups[bracket]
            if not b_players:
                continue
                
            pings = [p["avg_ping"] for p in b_players]
            max_ping = max(pings)
            min_ping = min(pings)
            
            subgroups = []
            if max_ping - min_ping > MAX_PING_VARIANCE:
                low_ping_sub = [p for p in b_players if p["avg_ping"] < PING_THRESHOLD]
                high_ping_sub = [p for p in b_players if p["avg_ping"] >= PING_THRESHOLD]
                if low_ping_sub:
                    subgroups.append((low_ping_sub, "low-ping"))
                if high_ping_sub:
                    subgroups.append((high_ping_sub, "high-ping"))
            else:
                subgroups.append((b_players, ""))
                
            for sub_players, ping_label in subgroups:
                sorted_sub_players = sorted(sub_players, key=lambda x: x["player_id"])
                
                num_players = len(sorted_sub_players)
                num_groups = num_players // GROUP_SIZE
                
                for g_idx in range(num_groups):
                    group_players = sorted_sub_players[g_idx * GROUP_SIZE : (g_idx + 1) * GROUP_SIZE]
                    group_pings = [p["avg_ping"] for p in group_players]
                    ping_range_str = f"{min(group_pings):.0f}ms - {max(group_pings):.0f}ms"
                    
                    group_id = f"G{group_counter:03d}"
                    group_counter += 1
                    
                    groups.append({
                        "group_id": group_id,
                        "region": region,
                        "bracket": bracket,
                        "ping_range": ping_range_str,
                        "players": [p["player_id"] for p in group_players]
                    })
                    
                remaining_players = sorted_sub_players[num_groups * GROUP_SIZE :]
                if remaining_players:
                    total_waiting = len(remaining_players)
                    for rp in remaining_players:
                        if ping_label:
                            reason = f"Only {total_waiting} {bracket} player(s) in {region} {ping_label} group"
                        else:
                            reason = f"Only {total_waiting} {bracket} player(s) in {region} group"
                            
                        waiting_pool.append({
                            "player_id": rp["player_id"],
                            "region": region,
                            "bracket": bracket,
                            "reason": reason
                        })
                        
    waiting_pool = sorted(waiting_pool, key=lambda x: x["player_id"])
    
    return groups, waiting_pool
