import os
import ast
import operator
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

# Allowed operations for safe math evaluation via AST.
_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def _safe_eval(node):
    """Safely evaluates an AST node containing mathematical expressions."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported operation: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """
    Evaluates a math expression and returns the result.
    Use this for any arithmetic: addition, subtraction, multiplication,
    division, percentages, etc. Example input: '25 * 0.25' or '100 + 50'.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


@tool
def get_weather(city: str) -> str:
    """
    Returns the current temperature for a given city.
    Use this when the user asks about weather or temperature in a location.
    """
    weather_db = {
        "tokyo": 28,
        "paris": 18,
        "new york": 22,
        "london": 15,
        "mumbai": 34,
    }
    temp = weather_db.get(city.lower())
    if temp is None:
        return f"Weather data not available for {city}."
    return f"The current temperature in {city} is {temp}°C."


@tool
def word_count(text: str) -> str:
    """
    Counts the number of words in a piece of text.
    Use this when the user wants to know how many words are in something.
    """
    count = len(text.split())
    return f"The text has {count} words."


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)

tools = [calculator, get_weather, word_count]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use tools whenever they help you give a better answer."),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent = create_tool_calling_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print("=" * 60)
print("DEMO 1: Single tool — calculator")
print("=" * 60)
result = executor.invoke({"input": "What is 25% of 500?"})
print(f"\nFinal answer: {result['output']}\n")

print("=" * 60)
print("DEMO 2: Single tool — weather")
print("=" * 60)
result = executor.invoke({"input": "What is the weather in Tokyo?"})
print(f"\nFinal answer: {result['output']}\n")

print("=" * 60)
print("DEMO 3: Multi-step — weather + calculator (Activity 7)")
print("=" * 60)
result = executor.invoke({
    "input": "What is the current temperature in Paris, and what would it be if it were 10 degrees warmer?"
})
print(f"\nFinal answer: {result['output']}\n")

print("=" * 60)
print("DEMO 4: No tool needed — agent answers directly")
print("=" * 60)
result = executor.invoke({"input": "What is the capital of France?"})
print(f"\nFinal answer: {result['output']}\n")

print("=" * 60)
print("Interactive mode — ask anything. Type 'quit' to exit.")
print("=" * 60)

while True:
    user_input = input("\nYou: ").strip()
    if user_input.lower() == "quit":
        break
    if not user_input:
        continue
    result = executor.invoke({"input": user_input})
    print(f"\nAgent: {result['output']}")

