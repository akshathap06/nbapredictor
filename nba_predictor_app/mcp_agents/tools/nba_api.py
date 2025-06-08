import requests
from typing import Dict, Any, Optional

class NBAApiTool:
    def __init__(self):
        self.api_key = "6d1d85e587msh7b364bb697467a8p1e838ejsne267facd43ab"
        self.base_url = "https://api-nba-v1.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
        }

    def search_player(self, first_name: str, last_name: str) -> Dict[Any, Any]:
        """Search for a player by name."""
        url = f"{self.base_url}/players"
        params = {"search": f"{first_name} {last_name}"}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_player_stats(self, player_id: int, season: str = "2023") -> Dict[Any, Any]:
        """Get player statistics for a given season."""
        url = f"{self.base_url}/players/statistics"
        params = {
            "id": str(player_id),
            "season": season
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def calculate_season_averages(self, stats_data: Dict[Any, Any]) -> Optional[Dict[str, float]]:
        """Calculate season averages from player statistics."""
        if not stats_data or "response" not in stats_data or not stats_data["response"]:
            return None

        games = stats_data["response"]
        total_games = len(games)
        
        if total_games == 0:
            return None

        averages = {
            "ppg": sum(game.get("points", 0) for game in games) / total_games,
            "rpg": sum(game.get("totReb", 0) for game in games) / total_games,
            "apg": sum(game.get("assists", 0) for game in games) / total_games,
            "spg": sum(game.get("steals", 0) for game in games) / total_games,
            "bpg": sum(game.get("blocks", 0) for game in games) / total_games,
            "games_played": total_games
        }
        
        return averages 