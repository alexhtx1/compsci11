import os
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# ------------------ CONFIGURATION ------------------

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("❌ Missing API_KEY in .env file.")

# Initialize the modern Gemini Client
client = genai.Client(api_key=API_KEY)

# Context: February 2026 - Super Bowl LX
CURRENT_DATE = "February 2, 2026"
SEASON_CONTEXT = (
    "It is currently February 2, 2026. The NFL is in Super Bowl Week. "
    "Super Bowl LX features the Seattle Seahawks vs. the New England Patriots "
    "at Levi's Stadium on February 8. You are an elite NFL analyst. "
    "Use the provided tools to fetch real-time stats or scores when asked."
)

# ------------------ LIVE DATA TOOLS ------------------

def get_nfl_scoreboard():
    """Fetches the latest NFL scores and schedules from ESPN."""
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        events = data.get("events", [])
        results = []
        for e in events:
            name = e.get("name")
            status = e.get("status", {}).get("type", {}).get("detail")
            competitors = e['competitions'][0]['competitors']
            score = " vs ".join([f"{t['team']['displayName']} {t['score']}" for t in competitors])
            results.append(f"{name}: {score} ({status})")
        return "\n".join(results) if results else "No recent games found."
    except Exception as e:
        return f"Error fetching scores: {str(e)}"

def get_league_leaders(category: str):
    """
    Fetches top 10 NFL leaders for a specific statistical category.
    Supported categories: 'passingYards', 'rushingYards', 'receivingYards', 'sacks', 'interceptions'
    """
    # Mapping to handle common natural language phrases from the AI
    mapping = {
        "passing yards": "passingYards",
        "rushing yards": "rushingYards",
        "receiving yards": "receivingYards",
        "picks": "interceptions",
        "ints": "interceptions"
    }
    
    clean_category = mapping.get(category.lower(), category)
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/leaders"
    params = {"category": clean_category, "limit": 10}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        leaders = data["leaders"][0]["leaders"]
        output = [f"{i+1}. {l['athlete']['displayName']} ({l['team']['displayName']}): {l['value']}" 
                  for i, l in enumerate(leaders)]
        return "\n".join(output)
    except Exception:
        return f"Could not find leaders for the category: {category}."

# ------------------ CHAT IMPLEMENTATION ------------------

def run_nfl_chat():
    print(f"🏈 NFL AI Analyst - {CURRENT_DATE}")
    print("Ask about Super Bowl LX, stats, or top 10 lists (type 'exit' to quit).")

    # Create a chat session with automatic function calling enabled
    # Using 'gemini-2.0-flash' which is the standard for 2026
    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=SEASON_CONTEXT,
            tools=[get_nfl_scoreboard, get_league_leaders],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
        )
    )

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Analyst signing off. Enjoy the Super Bowl!")
            break
            
        try:
            # Send the message; the SDK handles the back-and-forth for tool execution
            response = chat.send_message(user_input)
            print(f"\nAI: {response.text}")
        except Exception as e:
            print(f"\nAI Error: {e}")

if __name__ == "__main__":
    run_nfl_chat()