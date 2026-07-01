"""
Sets up the LangChain agent with tools, memory, and tool-call timing.
"""

import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools.calculator import calculator
from tools.web_search import web_search
from tools.pdf_summarizer import load_pdf, query_pdf

load_dotenv()

# Stores tool execution history for the sidebar display
tool_history = []


def create_my_agent():
    """Builds the agent with Gemini + all four tools."""

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0,
    )

    tools = [calculator, web_search, load_pdf, query_pdf]

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=(
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
    Sends user_input to the agent and returns the response text.
    Also logs tool calls with their execution time to tool_history.
    """
    messages = [{"role": m["role"], "content": m["content"]} for m in chat_history]
    messages.append({"role": "user", "content": user_input})

    start_time = time.time()

    try:
        result = agent.invoke({"messages": messages})
        output_messages = result["messages"]

        # Log any tool calls that happened during this run
        for msg in output_messages:
            if getattr(msg, "type", "") == "tool":
                elapsed = time.time() - start_time
                tool_history.append({
                    "tool": getattr(msg, "name", "unknown"),
                    "output": str(getattr(msg, "content", ""))[:200],
                    "time_seconds": round(elapsed, 2),
                })

        # Grab the final AI response (last AI message with content)
        response_text = ""
        for msg in reversed(output_messages):
            if getattr(msg, "type", "") == "ai" and getattr(msg, "content", ""):
                response_text = msg.content
                break

        return response_text or "I processed your request but couldn't generate a response."

    except Exception as e:
        return f"Sorry, something went wrong: {e}"
