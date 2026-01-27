import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv

# ------------------ SETUP ------------------

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))

system_instructions = (
    "You are an expert NFL assistant. "
    "You can answer ANY football question including rankings, predictions, "
    "player stats, team analysis, history, and opinions. "
    "When live data is provided, use it to stay current, but do NOT restrict "
    "yourself to only that data — combine it with your football knowledge. "
    "Speak naturally and clearly."
)

model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview",
    system_instruction=system_instructions
)

# ------------------ LIVE DATA ------------------

def get_espn_scoreboard():
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    return requests.get(url).json()

def summarize_live_data(data):
    try:
        season_type = data.get("season", {}).get("type")
        week = data.get("week", {}).get("number")

        if season_type == 3:
            phase = "Postseason"
        elif season_type == 2:
            phase = f"Regular Season Week {week}"
        else:
            phase = "Preseason"

        events = data.get("events", [])
        completed = [e for e in events if e["status"]["type"]["completed"]]

        latest_game = None
        if completed:
            latest = sorted(completed, key=lambda e: e["date"])[-1]
            comp = latest["competitions"][0]
            home = comp["competitors"][0]
            away = comp["competitors"][1]
            latest_game = f"{away['team']['displayName']} {away['score']} vs {home['team']['displayName']} {home['score']}"

        return {
            "phase": phase,
            "latest_game": latest_game
        }
    except:
        return None

# ------------------ QUESTION DETECTOR ------------------

def needs_live_data(text):
    text = text.lower()
    keywords = ["score", "week", "playoff", "latest", "last game", "today", "standings"]
    return any(word in text for word in keywords)

# ------------------ CHAT LOOP ------------------

def start_chat():
    chat = model.start_chat(history=[])

    print("🏈 Hi! I'm your NFL AI with live updates.")
    print("Ask me anything about players, teams, stats, predictions, or history.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye! 👋")
            break

        try:
            if needs_live_data(user_input):
                data = get_espn_scoreboard()
                summary = summarize_live_data(data)

                prompt = f"""
User question:
{user_input}

Here is current NFL context:
Current phase: {summary['phase']}
Latest game: {summary['latest_game']}

Use this information if helpful, but feel free to use your football knowledge too.
"""
            else:
                prompt = user_input

            response = chat.send_message(prompt)
            print(f"\nAI: {response.text}\n")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_chat()
