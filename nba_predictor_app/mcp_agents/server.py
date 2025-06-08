from mcp.server.fastmcp import FastMCP
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
from typing import Dict, Any
import pandas as pd
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP server
mcp = FastMCP(
    "nba_predictor",
    transport="stdio"
)

# Pydantic models for request validation
class PlayerSearchRequest(BaseModel):
    first_name: str
    last_name: str

class PlayerStatsRequest(BaseModel):
    player_id: int
    season: str = "2023-24"

class PlayerSeasonsRequest(BaseModel):
    player_id: int

@app.post("/tools/search_player")
async def search_player_endpoint(request: PlayerSearchRequest):
    """
    Search for an NBA player by name.
    """
    # Get all players
    all_players = players.get_players()
    
    # Filter for the specific player (case-insensitive)
    player = next(
        (p for p in all_players 
         if p['first_name'].lower() == request.first_name.lower() 
         and p['last_name'].lower() == request.last_name.lower()),
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
            "message": f"Player {request.first_name} {request.last_name} not found"
        }

@app.post("/tools/get_player_stats")
async def get_player_stats_endpoint(request: PlayerStatsRequest):
    """
    Get player statistics for a given season.
    """
    try:
        # Get career stats which includes season-by-season breakdown
        career_stats = playercareerstats.PlayerCareerStats(player_id=request.player_id)
        
        # Convert to pandas DataFrame
        season_stats = career_stats.get_data_frames()[0]
        
        # Filter for the requested season
        season_data = season_stats[season_stats['SEASON_ID'] == request.season].to_dict('records')
        
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
                "message": f"No stats found for season {request.season}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.post("/tools/get_available_seasons")
async def get_available_seasons_endpoint(request: PlayerSeasonsRequest):
    """
    Get all available seasons for a player.
    """
    try:
        career_stats = playercareerstats.PlayerCareerStats(player_id=request.player_id)
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

if __name__ == "__main__":
    print("Starting server...")
    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=6274) 