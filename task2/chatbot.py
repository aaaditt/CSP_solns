import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly assistant named Aria. Remember everything the user tells you."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = prompt | model

store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Returns or initializes the message history for a given session."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chatbot = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

print("Chatbot ready. Type 'quit' to exit, 'new' to start a new session.\n")
session_id = "session_1"
print(f"Current session: {session_id}")

while True:
    user_input = input("\nYou: ").strip()

    if user_input.lower() == "quit":
        break
    elif user_input.lower() == "new":
        session_id = input("Enter new session name: ").strip()
        print(f"Switched to session: {session_id}")
        continue
    elif not user_input:
        continue

    response = chatbot.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}},
    )
    print(f"Aria: {response.content}")

