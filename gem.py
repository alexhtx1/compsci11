import google.generativeai as genai
import os
import requests
import time
from dotenv import load_dotenv

# ------------------ SETUP ------------------

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))

system_instructions = (
    "You are an expert NFL analyst AI. "
    "Answer ANY football question including rankings, predictions, player stats, "
    "historical info, comparisons, and opinions. "
    "When live data is provided, ALWAYS prioritize it over memory, "
    "but never refuse to answer if some data is missing."
)

model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview",
    system_instruction=system_instructions
)

# ------------------ ESPN ENDPOINTS ------------------

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
LEADERS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/leaders"

# ------------------ LIVE DATA FUNCTIONS ------------------

def get_scoreboard():
    return requests.get(SCOREBOARD_URL).json()

def get_passing_leaders():
    params = {"limit": 5, "category": "passingYards"}
    return requests.get(LEADERS_URL, params=params).json()

def get_rushing_leaders():
    params = {"limit": 5, "category": "rushingYards"}
    return requests.get(LEADERS_URL, params=params).json()

def get_receiving_leaders():
    params = {"limit": 5, "category": "receivingYards"}
    return requests.get(LEADERS_URL, params=params).json()

# ------------------ DATA SUMMARIZERS ------------------

def summarize_scoreboard(data):
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
            teams = comp["competitors"]
            t1 = teams[0]
            t2 = teams[1]
            latest_game = f"{t1['team']['displayName']} {t1['score']} vs {t2['team']['displayName']} {t2['score']}"

        return {"phase": phase, "latest_game": latest_game}
    except:
        return {"phase": "Unknown", "latest_game": None}

def summarize_leaders(data):
    try:
        leaders = []
        for athlete in data["leaders"][0]["leaders"]:
            leaders.append(
                f"{athlete['athlete']['displayName']} ({athlete['team']['displayName']}) — {athlete['value']}"
            )
        return leaders
    except:
        return None

# ------------------ INTENT DETECTION ------------------

def detect_intent(text):
    t = text.lower()
    if "passing yards" in t:
        return "passing_leaders"
    if "rushing yards" in t:
        return "rushing_leaders"
    if "receiving yards" in t:
        return "receiving_leaders"
    if "week" in t or "latest" in t or "playoff" in t or "score" in t or "champion" in t:
        return "scoreboard"
    return "general"

# ------------------ FALLBACK NFL BRAIN (RATE LIMIT SAFETY) ------------------

def offline_brain(question):
    q = question.lower()

    if "top 5 qb" in q:
        return (
            "Here are my current top 5 NFL quarterbacks:\n"
            "1. Patrick Mahomes\n"
            "2. Josh Allen\n"
            "3. Joe Burrow\n"
            "4. Lamar Jackson\n"
            "5. Justin Herbert\n"
        )

    if "top 5 wr" in q:
        return (
            "Here are my current top 5 wide receivers:\n"
            "1. Tyreek Hill\n"
            "2. Justin Jefferson\n"
            "3. Ja'Marr Chase\n"
            "4. CeeDee Lamb\n"
            "5. Davante Adams\n"
        )

    if "top 5 rb" in q:
        return (
            "Here are my current top 5 running backs:\n"
            "1. Christian McCaffrey\n"
            "2. Derrick Henry\n"
            "3. Bijan Robinson\n"
            "4. Jahmyr Gibbs\n"
            "5. Nick Chubb\n"
        )

    if "super bowl" in q:
        return (
            "Based on current playoff performance and roster strength, "
            "the top Super Bowl contenders right now are the Chiefs, "
            "49ers, Ravens, and Bills — with Kansas City slightly favored."
        )

    return None

# ------------------ GEMINI SAFE CALL ------------------

def safe_gemini(chat, prompt):
    try:
        return chat.send_message(prompt)
    except Exception as e:
        if "429" in str(e):
            return None
        raise e

# ------------------ CHAT LOOP ------------------

def start_chat():
    chat = model.start_chat(history=[])

    print("🏈 Hi! I'm your NFL AI with live stats.")
    print("Ask me anything about players, teams, rankings, stats, or predictions.")
    print("Type 'exit' to quit.\n")

    while True:
        user = input("You: ")
        if user.lower() == "exit":
            print("Goodbye! 👋")
            break

        try:
            intent = detect_intent(user)
            live_context = ""

            if intent == "passing_leaders":
                data = get_passing_leaders()
                leaders = summarize_leaders(data)
                if leaders:
                    live_context = "Current NFL passing yard leaders:\n" + "\n".join(leaders)

            elif intent == "rushing_leaders":
                data = get_rushing_leaders()
                leaders = summarize_leaders(data)
                if leaders:
                    live_context = "Current NFL rushing yard leaders:\n" + "\n".join(leaders)

            elif intent == "receiving_leaders":
                data = get_receiving_leaders()
                leaders = summarize_leaders(data)
                if leaders:
                    live_context = "Current NFL receiving yard leaders:\n" + "\n".join(leaders)

            elif intent == "scoreboard":
                data = get_scoreboard()
                summary = summarize_scoreboard(data)
                live_context = f"Current NFL phase: {summary['phase']}\nLatest game: {summary['latest_game']}"

            if live_context:
                prompt = f"""
User question:
{user}

Here is current NFL data:
{live_context}

Answer clearly and naturally using this data when relevant.
"""
            else:
                prompt = user

            response = safe_gemini(chat, prompt)

            if response:
                print(f"\nAI: {response.text}\n")
            else:
                fallback = offline_brain(user)
                if fallback:
                    print(f"\nAI: {fallback}\n")
                else:
                    print("\nAI: I'm temporarily rate-limited, but based on current league trends, elite teams and players continue to dominate.\n")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_chat()
