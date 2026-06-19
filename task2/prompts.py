from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# --- Template 1: Simple PromptTemplate ---
# Plain string with {placeholders} — no f-string, LangChain fills these in later
simple_template = PromptTemplate.from_template("Explain {topic} in a {style} way.")

filled = simple_template.invoke({"topic": "black holes", "style": "simple"})
print("Template 1:", filled.text)

# --- Template 2: ChatPromptTemplate ---
# Models like Gemini/GPT receive a list of messages: system sets the persona,
# human is the actual user message. ChatPromptTemplate builds that list for you.
chat_template = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} who speaks in a {tone} tone."),
    ("human", "Tell me about {topic}."),
])

messages = chat_template.invoke({"role": "scientist", "tone": "enthusiastic", "topic": "mars"})
print("\nTemplate 2 (chat messages):")
for msg in messages.messages:
    print(f"  [{msg.type}]: {msg.content}")

# --- Template 3: Reusable translator template ---
translate_template = PromptTemplate.from_template(
    "Translate the following text to {language}:\n\n{text}"
)

filled3 = translate_template.invoke({"language": "French", "text": "Good morning, how are you?"})
print("\nTemplate 3:", filled3.text)
