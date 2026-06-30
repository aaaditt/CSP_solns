"""
Agent Setup
Creates the LangChain agent with all tools, conversation memory,
and tool execution timing.
"""

import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

# Import our tools
from tools.calculator import calculator
from tools.web_search import web_search
from tools.pdf_summarizer import load_pdf, query_pdf

load_dotenv()

# ── Tool execution tracker (Bonus: timing + history) ──────────────

tool_history = []  # List of dicts: {tool, output, time_seconds}


# ── Build the agent ───────────────────────────────────────────────

def create_my_agent():
    """Creates and returns the agent graph with all tools."""

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0,
    )

    tools = [calculator, web_search, load_pdf, query_pdf]

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You are a helpful AI assistant with access to these tools:\n"
            "- calculator: for math expressions (percentages, arithmetic)\n"
            "- web_search: for current information from the internet\n"
            "- load_pdf: to load a PDF file (call this first before querying)\n"
            "- query_pdf: to answer questions about a loaded PDF\n\n"
            "Pick the right tool based on the user's question. "
            "You can use multiple tools in one response if needed. "
            "Always give a clear, helpful final answer."
        ),
    )

    return agent


def run_agent(agent, user_input, chat_history):
    """
    Runs the agent with a user message and returns the response.
    Tracks tool execution timing.

    Args:
        agent: The compiled agent graph
        user_input: The user's message string
        chat_history: List of previous messages (dicts with role/content)

    Returns:
        tuple: (response_text, updated_chat_history)
    """
    # Build messages list from chat history + new input
    messages = []
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    start_time = time.time()

    try:
        result = agent.invoke({"messages": messages})
        # The last message in the result is the AI's response
        output_messages = result["messages"]

        # Track any tool calls that happened
        for msg in output_messages:
            msg_type = getattr(msg, "type", "")
            if msg_type == "tool":
                elapsed = time.time() - start_time
                tool_history.append({
                    "tool": getattr(msg, "name", "unknown"),
                    "output": str(getattr(msg, "content", ""))[:200],
                    "time_seconds": round(elapsed, 2),
                })

        # Get the final AI response (last AI message)
        response_text = ""
        for msg in reversed(output_messages):
            if getattr(msg, "type", "") == "ai" and getattr(msg, "content", ""):
                response_text = msg.content
                break

        if not response_text:
            response_text = "I processed your request but couldn't generate a response."

        return response_text

    except Exception as e:
        return f"Sorry, something went wrong: {e}"
