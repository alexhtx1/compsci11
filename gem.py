import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the API
genai.configure(api_key=os.getenv('API_KEY'))

# System message to define the persona
normal_instructions = "You are a friendly helpful sports AI. You respond in clear, normal conversational English. You specialize in the NFL. Answer questions directly, explain thinking simply, and avoid role-playing or pirate language."

# Initialize the model with system instructions
model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview",
    system_instruction=normal_instructions
)

def start_chat():
    # Start a chat session to maintain context (optional but recommended)
    chat_session = model.start_chat(history=[])
    
    print("👋 Hi! I'm your NFL Sports AI. Ask me anything about players, teams, or stats.")
    print("Type 'exit' at any time to quit. \n")

    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Goodbye! Thanks for chatting about football.")
            break
        
        try:
            # Send message to the model
            response = chat_session.send_message(user_input)
            print(f"\nAI: {response.text}\n")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    start_chat()
    