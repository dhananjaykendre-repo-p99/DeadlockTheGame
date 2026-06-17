import streamlit as st
import pandas as pd
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Deadlock",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF4B4B, #FF8F00, #8A2BE2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #FF4B4B;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title"> Deadlock Matchmaking Dashboard</h1>', unsafe_allow_html=True)
st.markdown("Monitor player performance, track suspicious behavior, manage leaderboards, and coordinate fair matchmaking groups.")
st.markdown("---")

api_connected = False
api_health_data = {}

try:
    health_resp = requests.get(f"{API_BASE}/health", timeout=3)
    if health_resp.status_code == 200:
        api_connected = True
        api_health_data = health_resp.json()
except Exception:
    api_connected = False

st.sidebar.markdown("## upload the player data")

if not api_connected:
    st.sidebar.error("API Offline")
    st.error("FastAPI server is not running.")
    st.stop()

st.sidebar.success("API Connected")

uploaded_file = st.sidebar.file_uploader("Upload Multiplayer Match CSV", type=["csv"])

if st.sidebar.button("Reset Data"):
    try:
        requests.delete(f"{API_BASE}/reset")

        for key in list(st.session_state.keys()):
            if key.startswith("uploaded_"):
                del st.session_state[key]
        st.sidebar.success("Data reset successful!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error resetting data: {e}")

if api_health_data.get("total_records", 0) == 0 and not uploaded_file:

    st.info("Welcome! Please upload a multiplayer match CSV file in the sidebar to get started.")
    
    st.markdown("### Expected CSV File Format")
    st.markdown("Your CSV file must contain the following columns:")
    
    sample_data = {
        "player_id": ["P001", "P002", "P003"],
        "match_id": ["M001", "M001", "M002"],
        "region": ["North America", "Europe", "SEA"],
        "device": ["Android", "Android", "iOS"],
        "ping": [55, 70, 90],
        "score": [3200, 2800, 99000],
        "kills": [18, 14, 250],
        "deaths": [4, 5, 0],
        "match_duration_seconds": [420, 430, 60]
    }
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df, width="stretch")
    
    st.markdown("### Detection Rules Built-In")
    st.write("- **R1 Score Rate**: Score rate > 50 pts/sec")
    st.write("- **R2 Kill Rate**: Kill rate > 30 kills/min")
    st.write("- **R3 Perfect Game**: Kills > 10 and 0 deaths")
    st.write("- **R4 Score Kill Mismatch**: Score > 5000 and kills < 3")
    st.write("- **R5 Short Match**: Match duration < 120s and score > 3000")
    st.write("- **R6 Ping Anomaly**: Ping < 5 ms")

else:

    if uploaded_file:
        file_key = f"uploaded_{uploaded_file.name}_{uploaded_file.size}"
        if not st.session_state.get(file_key, False):
            try:
                with st.spinner("Processing and submitting CSV data to API..."):
                    df_upload = pd.read_csv(uploaded_file)

                    required_cols = [
                        "player_id", "match_id", "region", "device", 
                        "ping", "score", "kills", "deaths", "match_duration_seconds"
                    ]
                    df_upload = df_upload.dropna(subset=required_cols)
                    

                    df_upload = df_upload.rename(columns={"match_duration_seconds": "match_duration"})
                    

                    df_upload["ping"] = df_upload["ping"].astype(int)
                    df_upload["score"] = df_upload["score"].astype(int)
                    df_upload["kills"] = df_upload["kills"].astype(int)
                    df_upload["deaths"] = df_upload["deaths"].astype(int)
                    df_upload["match_duration"] = df_upload["match_duration"].astype(int)
                    

                    records = df_upload.to_dict(orient="records")
                    

                    post_resp = requests.post(f"{API_BASE}/submit-scores", json={"records": records})
                    if post_resp.status_code == 200:
                        st.session_state[file_key] = True
                        st.toast("Scores uploaded and processed successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to process scores. API Response: {post_resp.status_code} - {post_resp.text}")
            except Exception as e:
                st.error(f"Error reading and uploading CSV: {e}")

    with st.spinner("Fetching data from API..."):
        try:

            health_resp = requests.get(f"{API_BASE}/health")
            api_health_data = health_resp.json()
            total_players = api_health_data.get("total_players", 0)
            total_matches = api_health_data.get("total_records", 0)
            

            flagged_resp = requests.get(f"{API_BASE}/flagged-players").json()
            flagged_count = flagged_resp.get("total_flagged", 0)
            flagged_players_list = flagged_resp.get("players", [])
            

            mm_resp = requests.get(f"{API_BASE}/matchmaking").json()
            total_groups = mm_resp.get("total_groups", 0)
            

            lead_resp = requests.get(f"{API_BASE}/leaderboard").json()
            all_lead_entries = lead_resp.get("leaderboard", [])
            

            all_regions = sorted(list(set(row["region"] for row in all_lead_entries)))
            if not all_regions:

                all_regions = ["North America", "Europe", "SEA"]
                
        except Exception as e:
            st.error(f"Error connecting to backend API: {e}")
            st.stop()
            

    st.sidebar.markdown("### ── Event Summary ──")
    st.sidebar.metric("Total Players", total_players)
    st.sidebar.metric("Total Matches (Records)", total_matches)
    st.sidebar.metric("Flagged Players", flagged_count)
    st.sidebar.metric("Matchmaking Groups", total_groups)
    

    selected_regions = st.sidebar.multiselect(
        "Filter by Region",
        options=all_regions,
        default=all_regions,
        help="Filters leaderboard and matchmaking results."
    )
    

    tab1, tab2, tab3 = st.tabs([
        "Leaderboard", 
        "Flagged Players", 
        "Matchmaking"
    ])
    

    with tab1:
        st.subheader("Leaderboard")
        
        lead_type = st.radio(
            "Leaderboard Type",
            options=["Global Leaderboard", "Region-wise Leaderboard"],
            horizontal=True
        )
        
        if lead_type == "Global Leaderboard":
            st.markdown("#### Global Standings")
            with st.spinner("Loading global standings..."):
                try:
                    res = requests.get(f"{API_BASE}/leaderboard").json()
                    global_lead = res.get("leaderboard", [])
                    

                    filtered_global = [row for row in global_lead if row["region"] in selected_regions]
                    
                    if not filtered_global:
                        st.warning("No players matching the selected regions.")
                    else:
                        df_global = pd.DataFrame(filtered_global)
                        display_cols = {
                            "rank": "Rank",
                            "player_id": "Player ID",
                            "region": "Region",
                            "skill_bracket": "Bracket",
                            "total_score": "Total Score",
                            "total_kills": "Kills",
                            "total_deaths": "Deaths",
                            "matches_played": "Matches Played"
                        }
                        df_display = df_global[list(display_cols.keys())].rename(columns=display_cols)
                        st.dataframe(df_display, width="stretch", hide_index=True)
                except Exception as e:
                    st.error(f"Error fetching leaderboard: {e}")
        else:
            st.markdown("#### Region Standings")
            

            avail_regions = ["All"] + all_regions
            sel_lead_region = st.selectbox(
                "Select Region Filter",
                options=avail_regions,
                help="Filter the region standings to a specific region or show all."
            )
            
            if not selected_regions:
                st.warning("Please select at least one region in the sidebar filter.")
            else:
                with st.spinner("Loading regional standings..."):
                    try:
                        if sel_lead_region == "All":
                            res = requests.get(f"{API_BASE}/leaderboard?leaderboard_type=region").json()
                        else:
                            res = requests.get(f"{API_BASE}/leaderboard?region={sel_lead_region}").json()
                            
                        lead_entries = res.get("leaderboard", [])
                        

                        filtered_region_lead = [row for row in lead_entries if row["region"] in selected_regions]
                        
                        if not filtered_region_lead:
                            st.warning("No players found in selected regions matching the filters.")
                        else:
                            df_region = pd.DataFrame(filtered_region_lead)
                            display_cols = {
                                "rank": "Region Rank",
                                "player_id": "Player ID",
                                "region": "Region",
                                "skill_bracket": "Bracket",
                                "total_score": "Total Score",
                                "total_kills": "Kills",
                                "total_deaths": "Deaths",
                                "matches_played": "Matches Played",
                                "global_rank": "Global Rank"
                            }
                            df_display = df_region[list(display_cols.keys())].rename(columns=display_cols)
                            st.dataframe(df_display, width="stretch", hide_index=True)
                    except Exception as e:
                        st.error(f"Error fetching regional leaderboards: {e}")
                        
        st.caption(f"{flagged_count} players excluded due to suspicious activity")
        

    with tab2:
        st.subheader("Flagged Players")
        
        if flagged_count == 0:
            st.success("Excellent! No players flagged for suspicious behavior.")
        else:
            st.error(f"{flagged_count} player(s) flagged for suspicious activity.")
            

            flagged_summary_data = []
            for p in flagged_players_list:

                flagged_matches = set()
                for reason in p["suspicion_reasons"]:
                    if ":" in reason:
                        flagged_matches.add(reason.split(":")[0].strip())
                        
                flagged_summary_data.append({
                    "Player ID": p["player_id"],
                    "Region": p["region"],
                    "Matches Flagged": len(flagged_matches),
                    "Rules Triggered (count)": len(p["suspicion_reasons"]),
                    "reasons": p["suspicion_reasons"]
                })
                
            df_flagged = pd.DataFrame(flagged_summary_data)
            st.dataframe(
                df_flagged[["Player ID", "Region", "Matches Flagged", "Rules Triggered (count)"]],
                width="stretch",
                hide_index=True
            )
            
            st.markdown("### Detailed Investigation")
            for row in flagged_summary_data:
                with st.expander(f"Player {row['Player ID']} - {row['Region']} ({row['Rules Triggered (count)']} rule(s) triggered)"):
                    st.markdown("**Suspicion Log:**")
                    for reason in row["reasons"]:
                        st.write(f"- {reason}")
                        

    with tab3:
        st.subheader("Matchmaking Groups")
        

        st.markdown("#### Filter Groups & Waiting Pool")
        col_filter1, col_filter2 = st.columns(2)
        

        avail_regions = ["All"] + all_regions
        sel_tab_region = col_filter1.selectbox("Select Region Filter", options=avail_regions)
        
        sel_tab_bracket = col_filter2.selectbox("Select Bracket Filter", options=["All", "Seeker", "Oracle", "Eternus"])
        
        with st.spinner("Fetching matching groups..."):
            try:

                query_params = []
                if sel_tab_region != "All":
                    query_params.append(f"region={sel_tab_region}")
                if sel_tab_bracket != "All":
                    query_params.append(f"bracket={sel_tab_bracket}")
                    
                query_str = "?" + "&".join(query_params) if query_params else ""
                
                mm_data = requests.get(f"{API_BASE}/matchmaking{query_str}").json()
                groups_list = mm_data.get("groups", [])
                waiting_pool_list = mm_data.get("waiting_pool", [])
                

                groups_list = [g for g in groups_list if g["region"] in selected_regions]
                waiting_pool_list = [w for w in waiting_pool_list if w["region"] in selected_regions]
                

                col_m1, col_m2 = st.columns(2)
                col_m1.metric("Groups Formed", len(groups_list))
                col_m2.metric("Players in Waiting Pool", len(waiting_pool_list))
                
                st.markdown("---")
                
                st.markdown("#### Active Match Groups")
                if not groups_list:
                    st.info("No matchmaking groups formed matching the selected filters.")
                else:
                    groups_display_data = []
                    for g in groups_list:
                        groups_display_data.append({
                            "Group ID": g["group_id"],
                            "Region": g["region"],
                            "Bracket": g["bracket"],
                            "Ping Range": g["ping_range"],
                            "Players": ", ".join(g["players"])
                        })
                    df_groups = pd.DataFrame(groups_display_data)
                    st.dataframe(df_groups, width="stretch", hide_index=True)
                    
                st.markdown("---")
                st.markdown("#### Waiting Pool (Players awaiting additional matches)")
                if not waiting_pool_list:
                    st.success("Waiting pool is empty! All players successfully grouped.")
                else:
                    for w in waiting_pool_list:
                        st.warning(f"**Player {w['player_id']}** ({w['region']} - {w['bracket']}): {w['reason']}")
            except Exception as e:
                st.error(f"Error fetching matchmaking: {e}")
