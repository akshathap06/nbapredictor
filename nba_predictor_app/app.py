import streamlit as st
import requests
import pandas as pd
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# Load environment variables
load_dotenv()

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

def search_player(first_name: str, last_name: str) -> Dict[str, Any]:
    """Search for an NBA player by name."""
    # Get all players
    all_players = players.get_players()
    
    # Filter for the specific player (case-insensitive)
    player = next(
        (p for p in all_players 
         if p['first_name'].lower() == first_name.lower() 
         and p['last_name'].lower() == last_name.lower()),
        None
    )
    
    if player:
        return {
            "success": True,
            "player": player
        }
    else:
        return {
            "success": False,
            "message": f"Player {first_name} {last_name} not found"
        }

def get_player_stats(player_id: int, season: str = "2023-24") -> Dict[str, Any]:
    """Get player statistics for a given season."""
    try:
        # Get career stats which includes season-by-season breakdown
        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
        
        # Convert to pandas DataFrame
        season_stats = career_stats.get_data_frames()[0]
        
        # Filter for the requested season
        season_data = season_stats[season_stats['SEASON_ID'] == season].to_dict('records')
        
        if season_data:
            stats = season_data[0]
            games_played = stats['GP']
            
            # Calculate per-game averages
            if games_played > 0:
                stats['PTS'] = stats['PTS'] / games_played
                stats['REB'] = stats['REB'] / games_played
                stats['AST'] = stats['AST'] / games_played
                stats['STL'] = stats['STL'] / games_played
                stats['BLK'] = stats['BLK'] / games_played
                stats['MIN'] = stats['MIN'] / games_played
            
            return {
                "success": True,
                "stats": stats
            }
        else:
            return {
                "success": False,
                "message": f"No stats found for season {season}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

def get_available_seasons(player_id: int) -> Dict[str, Any]:
    """Get all available seasons for a player."""
    try:
        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
        seasons_df = career_stats.get_data_frames()[0]
        available_seasons = seasons_df['SEASON_ID'].tolist()
        
        return {
            "success": True,
            "seasons": available_seasons
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

def ask_gpt(question: str, context: Dict[str, Any]) -> str:
    """Ask ChatGPT a question about the player statistics"""
    try:
        # Format the context and question
        prompt = f"""Here are the NBA player statistics:
{json.dumps(context, indent=2)}

Question: {question}

Please analyze these statistics and answer the question."""

        # Call ChatGPT API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a knowledgeable NBA analyst who can analyze player statistics and provide insights."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error calling ChatGPT API: {str(e)}"

def display_stat_with_progress(label: str, value: float, max_value: float, format_str: str = "{:.1f}"):
    """Display a statistic with a progress bar"""
    st.write(f"**{label}:** {format_str.format(value)}")
    st.progress(min(value / max_value, 1.0))

# Set up the page
st.set_page_config(
    page_title="NBA Player Stats",
    page_icon="🏀",
    layout="wide"
)

st.title("NBA Player Statistics 🏀")

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    first_name = st.text_input("Player's First Name")
with col2:
    last_name = st.text_input("Player's Last Name")

# Store the current player's stats in session state
if "current_stats" not in st.session_state:
    st.session_state.current_stats = None

# Search button
if st.button("Search Player"):
    if first_name and last_name:
        with st.spinner("Searching for player..."):
            # Search for player
            result = search_player(first_name=first_name, last_name=last_name)
            
            if result["success"]:
                player = result["player"]
                st.success(f"Found player: {player['first_name']} {player['last_name']}")
                
                # Display player info
                st.subheader("Player Information")
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.write(f"Player ID: {player['id']}")
                    st.write(f"Active: {'Yes' if player['is_active'] else 'No'}")
                
                with st.spinner("Loading available seasons..."):
                    # Get available seasons
                    seasons_result = get_available_seasons(player_id=player['id'])
                    
                    if seasons_result["success"]:
                        # Sort seasons in descending order (most recent first)
                        seasons = sorted(seasons_result["seasons"], reverse=True)
                        
                        # Create season selector
                        season = st.selectbox(
                            "Select Season",
                            options=seasons,
                            index=0 if "2023-24" not in seasons else seasons.index("2023-24")
                        )
                        
                        with st.spinner("Loading player statistics..."):
                            # Get stats for selected season
                            stats_result = get_player_stats(player_id=player['id'], season=season)
                            
                            if stats_result["success"]:
                                # Store the current stats in session state
                                st.session_state.current_stats = {
                                    "player": player,
                                    "season": season,
                                    "stats": stats_result["stats"]
                                }
            else:
                st.error(f"Error: {result['message']}")
    else:
        st.warning("Please enter both first and last name.")

# Display player statistics if available
if st.session_state.current_stats is not None:
    stats = st.session_state.current_stats["stats"]
    season = st.session_state.current_stats["season"]
    
    st.subheader(f"Statistics for {season} Season")
    
    # Create three columns for stats display
    stats_cols = st.columns(3)
    
    # Scoring stats
    with stats_cols[0]:
        st.markdown("**Scoring**")
        display_stat_with_progress("Points Per Game", stats['PTS'], 40)  # 40 points is exceptional
        display_stat_with_progress("Field Goal %", stats['FG_PCT'] * 100, 100, "{:.1f}%")
        display_stat_with_progress("3-Point %", stats['FG3_PCT'] * 100, 100, "{:.1f}%")
        display_stat_with_progress("Free Throw %", stats['FT_PCT'] * 100, 100, "{:.1f}%")
    
    # Other key stats
    with stats_cols[1]:
        st.markdown("**Other Stats**")
        display_stat_with_progress("Rebounds Per Game", stats['REB'], 15)  # 15 rebounds is exceptional
        display_stat_with_progress("Assists Per Game", stats['AST'], 12)   # 12 assists is exceptional
        display_stat_with_progress("Steals Per Game", stats['STL'], 3)     # 3 steals is exceptional
        display_stat_with_progress("Blocks Per Game", stats['BLK'], 3)     # 3 blocks is exceptional
    
    # Playing time
    with stats_cols[2]:
        st.markdown("**Playing Time**")
        st.metric("Games Played", int(stats['GP']))
        st.metric("Games Started", int(stats['GS']))
        display_stat_with_progress("Minutes Per Game", stats['MIN'], 48)  # 48 minutes is max possible
    
    # Show detailed stats in an expander
    with st.expander("View Detailed Statistics"):
        # Select relevant columns and rename them for better display
        display_cols = {
            'SEASON_ID': 'Season',
            'TEAM_ABBREVIATION': 'Team',
            'GP': 'Games Played',
            'GS': 'Games Started',
            'MIN': 'Minutes',
            'FGM': 'FG Made',
            'FGA': 'FG Attempts',
            'FG_PCT': 'FG%',
            'FG3M': '3P Made',
            'FG3A': '3P Attempts',
            'FG3_PCT': '3P%',
            'FTM': 'FT Made',
            'FTA': 'FT Attempts',
            'FT_PCT': 'FT%',
            'REB': 'Rebounds',
            'AST': 'Assists',
            'STL': 'Steals',
            'BLK': 'Blocks',
            'TOV': 'Turnovers',
            'PTS': 'Points'
        }
        
        detailed_stats = pd.DataFrame([stats])[display_cols.keys()].rename(columns=display_cols)
        st.dataframe(detailed_stats, use_container_width=True)
    
    # Add a section for asking questions about the player
    st.divider()
    st.subheader("Ask Questions About the Player")
    
    question = st.text_input("Enter your question about the player's statistics:")
    
    if question:
        with st.spinner("Analyzing statistics and generating response..."):
            response = ask_gpt(question, st.session_state.current_stats)
            st.write(response)
else:
    st.info("Search for a player to view their statistics and ask questions.") 