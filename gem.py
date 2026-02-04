import os
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

load_dotenv()

# ------------------ CONFIGURATION ------------------

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("❌ Missing API_KEY in .env file.")

# Initialize the Gemini Client
client = genai.Client(api_key=API_KEY)

# Context: February 2026 - Super Bowl LX
CURRENT_DATE = "February 4, 2026"
SEASON_CONTEXT = (
    "You are an elite NFL analyst with deep knowledge of football history, statistics, and strategy. "
    f"The current date is {CURRENT_DATE}. The 2025 NFL season has concluded and we're in Super Bowl week. "
    "Super Bowl LX is scheduled for February 8, 2026 at Levi's Stadium. "
    "When users ask about current stats, recent games, or live information, use the provided tools to fetch real-time data. "
    "For predictions, use your analytical expertise combined with current season data. "
    "Be conversational, insightful, and enthusiastic about football. "
    "If asked about top lists (top 5, top 10, etc.), use the league leaders tool or provide analysis based on available data."
)

# ------------------ LIVE DATA TOOLS ------------------

def get_nfl_scoreboard() -> str:
    """
    Fetches the latest NFL scores and game schedules from ESPN API.
    Returns formatted string with game information including teams, scores, and status.
    """
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        events = data.get("events", [])
        if not events:
            return "No games scheduled or completed recently. The regular season has ended."
        
        results = []
        for event in events:
            game_name = event.get("name", "Unknown matchup")
            status_detail = event.get("status", {}).get("type", {}).get("detail", "Status unknown")
            
            competition = event.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])
            
            if len(competitors) >= 2:
                away_team = competitors[1].get("team", {}).get("displayName", "Team A")
                away_score = competitors[1].get("score", "0")
                home_team = competitors[0].get("team", {}).get("displayName", "Team B")
                home_score = competitors[0].get("score", "0")
                
                game_info = f"🏈 {away_team} {away_score} @ {home_team} {home_score} - {status_detail}"
                results.append(game_info)
            else:
                results.append(f"🏈 {game_name} - {status_detail}")
        
        return "\n".join(results)
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching scoreboard data: {str(e)}"
    except Exception as e:
        return f"Unexpected error processing scoreboard: {str(e)}"


def get_league_leaders(category: str, limit: int = 10) -> str:
    """
    Fetches top NFL statistical leaders for a specific category.
    
    Args:
        category: Statistical category to fetch. Supported values:
                 - 'passingYards', 'passingTouchdowns', 'passingRating'
                 - 'rushingYards', 'rushingTouchdowns'
                 - 'receivingYards', 'receivingTouchdowns', 'receptions'
                 - 'sacks', 'interceptions', 'tackles'
        limit: Number of leaders to return (default: 10, max: 25)
    
    Returns:
        Formatted string with player rankings, names, teams, and stat values.
    """
    # Normalize category names
    category_mapping = {
        "passing yards": "passingYards",
        "passing touchdowns": "passingTouchdowns",
        "passing tds": "passingTouchdowns",
        "passer rating": "passingRating",
        "qbr": "passingRating",
        "rushing yards": "rushingYards",
        "rushing touchdowns": "rushingTouchdowns",
        "rushing tds": "rushingTouchdowns",
        "receiving yards": "receivingYards",
        "receiving touchdowns": "receivingTouchdowns",
        "receiving tds": "receivingTouchdowns",
        "receptions": "receptions",
        "catches": "receptions",
        "picks": "interceptions",
        "ints": "interceptions",
        "sacks": "sacks",
        "tackles": "tackles"
    }
    
    normalized_category = category_mapping.get(category.lower(), category)
    limit = min(max(1, limit), 25)  # Ensure limit is between 1 and 25
    
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/leaders"
    params = {"limit": limit}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Find the matching category in the leaders data
        all_categories = data.get("leaders", [])
        target_leaders = None
        
        for cat_data in all_categories:
            if cat_data.get("name", "").lower().replace(" ", "") == normalized_category.lower():
                target_leaders = cat_data.get("leaders", [])
                break
        
        if not target_leaders:
            # Try to find by abbreviation or alternative matching
            for cat_data in all_categories:
                if normalized_category.lower() in cat_data.get("name", "").lower():
                    target_leaders = cat_data.get("leaders", [])
                    break
        
        if not target_leaders:
            available = [cat.get("displayName", "") for cat in all_categories]
            return (f"Could not find leaders for '{category}'. "
                   f"Try one of these: {', '.join(available[:5])}")
        
        results = []
        for i, leader in enumerate(target_leaders[:limit], 1):
            player_name = leader.get("athlete", {}).get("displayName", "Unknown Player")
            team_name = leader.get("team", {}).get("abbreviation", "N/A")
            stat_value = leader.get("displayValue", leader.get("value", "N/A"))
            results.append(f"{i}. {player_name} ({team_name}): {stat_value}")
        
        category_display = normalized_category.replace("passing", "Passing ").replace("rushing", "Rushing ").replace("receiving", "Receiving ")
        header = f"📊 Top {limit} NFL Leaders - {category_display}\n" + "="*50
        return header + "\n" + "\n".join(results)
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching league leaders: {str(e)}"
    except Exception as e:
        return f"Unexpected error processing leaders data: {str(e)}"


def get_team_stats(team_name: str) -> str:
    """
    Fetches current season statistics for a specific NFL team.
    
    Args:
        team_name: Name or abbreviation of the team (e.g., 'Patriots', 'NE', 'Seahawks', 'SEA')
    
    Returns:
        Formatted string with team record, standings, and key statistics.
    """
    # Try to get team info from ESPN API
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
        
        # Find matching team
        target_team = None
        search_term = team_name.lower()
        
        for team_obj in teams:
            team = team_obj.get("team", {})
            name = team.get("displayName", "").lower()
            abbr = team.get("abbreviation", "").lower()
            location = team.get("location", "").lower()
            
            if search_term in name or search_term == abbr or search_term in location:
                target_team = team
                break
        
        if not target_team:
            return f"Could not find team matching '{team_name}'. Please check the team name and try again."
        
        # Get detailed team info
        team_id = target_team.get("id")
        detail_url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}"
        
        detail_response = requests.get(detail_url, timeout=10)
        detail_data = detail_response.json()
        
        team_info = detail_data.get("team", {})
        team_display = team_info.get("displayName", team_name)
        
        # Extract record
        record = team_info.get("record", {}).get("items", [{}])[0]
        wins = record.get("stats", [{}])[0].get("value", 0)
        losses = record.get("stats", [{}])[1].get("value", 0) if len(record.get("stats", [])) > 1 else 0
        
        result = f"🏈 {team_display}\n" + "="*50 + "\n"
        result += f"Record: {int(wins)}-{int(losses)}\n"
        
        # Add more stats if available
        next_event = team_info.get("nextEvent")
        if next_event:
            result += f"\nNext Game: {next_event[0].get('name', 'TBD')}"
        
        return result
    
    except Exception as e:
        return f"Error fetching team stats for '{team_name}': {str(e)}"


def search_player_stats(player_name: str) -> str:
    """
    Searches for a specific player and returns their current season statistics.
    
    Args:
        player_name: Name of the player to search for
    
    Returns:
        Formatted string with player information and statistics.
    """
    # ESPN player search endpoint
    search_url = "https://site.api.espn.com/apis/common/v3/search"
    params = {
        "query": player_name,
        "limit": 5,
        "type": "player",
        "sport": "football",
        "league": "nfl"
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        if not results:
            return f"No player found matching '{player_name}'. Please check the spelling and try again."
        
        # Get the first matching player
        player = results[0]
        player_display = player.get("displayName", player_name)
        player_id = player.get("id")
        team = player.get("team", {}).get("abbreviation", "N/A")
        position = player.get("position", {}).get("abbreviation", "N/A")
        
        output = f"👤 {player_display}\n" + "="*50 + "\n"
        output += f"Team: {team} | Position: {position}\n"
        
        # Try to get detailed player stats
        if player_id:
            stats_url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/athletes/{player_id}"
            try:
                stats_response = requests.get(stats_url, timeout=10)
                stats_data = stats_response.json()
                
                # Extract season stats if available
                athlete_stats = stats_data.get("athlete", {}).get("statistics", [])
                if athlete_stats:
                    output += "\n2025 Season Stats:\n"
                    for stat in athlete_stats[:5]:  # Show top 5 stats
                        stat_name = stat.get("displayName", "")
                        stat_value = stat.get("displayValue", "")
                        if stat_name and stat_value:
                            output += f"  • {stat_name}: {stat_value}\n"
            except:
                pass  # Stats not critical, continue without them
        
        return output
    
    except Exception as e:
        return f"Error searching for player '{player_name}': {str(e)}"


# ------------------ CHAT IMPLEMENTATION ------------------

def run_nfl_chat():
    """Main chat loop for the NFL AI Analyst."""
    
    print("="*60)
    print("🏈 NFL AI ANALYST - Powered by Gemini")
    print("="*60)
    print(f"📅 {CURRENT_DATE}")
    print("\nI'm your AI football analyst! Ask me about:")
    print("  • Live scores and schedules")
    print("  • Statistical leaders and rankings")
    print("  • Game predictions and analysis")
    print("  • Player and team information")
    print("  • Top 5/10 lists and comparisons")
    print("  • Historical data and trends")
    print("\nType 'exit' or 'quit' to end the session.")
    print("="*60 + "\n")
    
    try:
        # Create a chat session with automatic function calling
        chat = client.chats.create(
            model="gemini-2.0-flash-exp",
            config=types.GenerateContentConfig(
                system_instruction=SEASON_CONTEXT,
                tools=[
                    get_nfl_scoreboard,
                    get_league_leaders,
                    get_team_stats,
                    search_player_stats
                ],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=False
                ),
                temperature=0.7,
                top_p=0.95
            )
        )
        
        while True:
            try:
                user_input = input("\n🙋 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print("\n🏈 Thanks for chatting! Enjoy the games! 🏈\n")
                    break
                
                # Send message and get response
                response = chat.send_message(user_input)
                
                # Display the AI's response
                print(f"\n🤖 NFL Analyst: {response.text}")
                
            except KeyboardInterrupt:
                print("\n\n🏈 Chat interrupted. Goodbye! 🏈\n")
                break
            except Exception as e:
                print(f"\n⚠️  Error processing your message: {str(e)}")
                print("Please try rephrasing your question.\n")
    
    except Exception as e:
        print(f"\n❌ Failed to initialize chat: {str(e)}")
        print("Please check your API key and internet connection.\n")


# ------------------ MAIN ENTRY POINT ------------------

if __name__ == "__main__":
    run_nfl_chat()