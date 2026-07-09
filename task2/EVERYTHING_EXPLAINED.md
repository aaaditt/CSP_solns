# Everything We Built — A Complete Explanation

This document explains every concept, every file, and every line of thinking behind Task 2.
Read it top to bottom once and the whole picture will click.

---

## The Big Idea

You built three increasingly powerful things:

```
chatbot.py  →  a conversation that remembers you
agent.py    →  a conversation that can DO things
rag.py      →  a conversation that knows YOUR documents
```

Each one is built on top of the previous idea.

---

## Part 1: What is an LLM actually doing?

An LLM (Large Language Model) like Gemini is, at its core, doing one thing:

> **Given everything said so far, what word should come next?**

It was trained on billions of pages of text. It learned patterns. Now when you give it text,
it predicts what text should follow — over and over — until it decides to stop.

That's it. There's no "thinking" in the human sense. It's an extremely sophisticated
next-word predictor.

**The implication:** The model has no memory between conversations. Every time you call it,
it starts completely fresh. "Memory" is something WE have to build by feeding it the
conversation history every single time.

---

## Part 2: How does talking to a model actually work?

Every API call to Gemini (or any LLM) is just sending a list of messages:

```python
[
    {"role": "system",    "content": "You are a helpful assistant."},
    {"role": "user",      "content": "Hi, my name is Aadit."},
    {"role": "assistant", "content": "Hi Aadit! How can I help?"},
    {"role": "user",      "content": "What's my name?"},   # <-- new message
]
```

The model reads the ENTIRE list and generates the next message.
That's how it "remembers" — you keep passing the history back with every call.

---

## Part 3: What is LangChain and why use it?

Without LangChain, you'd write raw API calls every time:
- Manually format messages
- Manually track conversation history
- Manually connect tools
- Manually build retrieval logic

LangChain is a framework that gives you pre-built pieces for all of this.
You snap the pieces together with the `|` pipe operator (called a "chain"):

```python
chain = prompt | model
# prompt formats the input → model generates a response
```

---

## Part 4: Prompt Templates (prompts.py)

### What we built
Three reusable prompt templates with blank slots (`{placeholders}`) that you fill in later.

### Why not just use an f-string?
```python
# BAD — f-string fills in immediately, LangChain can't see the slots
template = f"Explain {topic} in {style} terms"

# GOOD — slots stay as text, LangChain fills them in when you call .invoke()
template = "Explain {topic} in {style} terms"
```

### The three types we made

**PromptTemplate** — a single instruction string with slots:
```python
simple_template = PromptTemplate.from_template("Explain {topic} in a {style} way.")
filled = simple_template.invoke({"topic": "black holes", "style": "simple"})
# Result: "Explain black holes in a simple way."
```

**ChatPromptTemplate** — a full conversation structure (system + human):
```python
chat_template = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} who speaks in a {tone} tone."),
    ("human",  "Tell me about {topic}."),
])
```
The `system` message sets the AI's persona. The `human` message is what the user says.
This maps directly to how the model API receives messages.

**Nothing called the AI yet.** Templates just produce formatted strings.
The actual model call happens in the next step.

---

## Part 5: The Chatbot with Memory (chatbot.py)

### What we built
A terminal chatbot you can have a back-and-forth conversation with.
It remembers everything you said earlier in the session.

### How memory works

```
You say "Hi, my name is Aadit"
    ↓
LangChain adds this to the history list
    ↓
You say "What's my name?"
    ↓
LangChain sends: [system msg] + [all previous messages] + [your new message]
    ↓
Model sees "my name is Aadit" in the history and answers correctly
```

### The key pieces

**The model:**
```python
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", ...)
```
This is the connection to Google's Gemini. It's just a Python object that
takes messages in and gives a response back.

**The prompt with a history slot:**
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly assistant named Aria."),
    MessagesPlaceholder(variable_name="history"),  # history gets injected here
    ("human", "{input}"),
])
```
`MessagesPlaceholder` is a special slot that doesn't take a string — it takes a whole
list of past messages and inserts them into the conversation.

**The chain:**
```python
chain = prompt | model
```
Prompt formats the input → model generates a response. The `|` passes output left → right.

**The memory store:**
```python
store = {}  # {"session_1": [msg1, msg2, ...], "session_2": [...]}

def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]
```
A dictionary where each key is a session ID and the value is the history for that session.
This is Activity 5 (separate conversation threads) — same session ID = same conversation.

**Wrapping it all together:**
```python
chatbot = RunnableWithMessageHistory(chain, get_session_history, ...)
```
This wrapper automatically:
1. Looks up history for the given session_id
2. Injects it into the `MessagesPlaceholder` slot
3. After the model responds, saves the new messages back to the store

**Every time you send a message:**
```python
response = chatbot.invoke(
    {"input": "What's my name?"},
    config={"configurable": {"session_id": "session_1"}}
)
```
The `session_id` tells the wrapper which conversation thread to use.

---

## Part 6: The Agent with Tools (agent.py)

### What we built
A chatbot that can USE external tools — a calculator, a weather lookup, a word counter.
The model decides ON ITS OWN when to use a tool and which one.

### The core idea: the ReAct loop

Without tools: User → Model → Answer

With tools (the ReAct loop):
```
User asks a question
    ↓
Model thinks: "Do I know this, or do I need a tool?"
    ↓
If tool needed: Model calls the tool with arguments
    ↓
Tool runs and returns a result
    ↓
Model reads the result and decides: "Am I done, or do I need another tool?"
    ↓
Eventually: Model gives final answer
```

This loop is what makes it an "agent" — it's reasoning across steps, not just answering.

### How we defined tools

```python
@tool
def calculator(expression: str) -> str:
    """
    Evaluates a math expression and returns the result.
    Use this for any arithmetic...
    """
    ...
```

`@tool` is a decorator — it wraps a normal function and tells LangChain
"this function is available for the model to call."

**The docstring is critical.** The model reads it to decide WHEN to use this tool.
If you write a bad docstring, the model won't know when to call it.

### Why we replaced eval() with ast

The original calculator used Python's `eval()` which runs any Python code — a security hole.
We replaced it with a safe AST (Abstract Syntax Tree) parser that only allows numbers and
arithmetic operators (+, -, *, /, **). It literally cannot run anything else.

```python
# eval("__import__('os').system('rm -rf /')") would work — dangerous
# our _safe_eval only allows: numbers, +, -, *, /, ** — nothing else
```

### Multi-step workflow (Activity 7)

```
"What's the temperature in Paris, and what would it be 10 degrees warmer?"

Step 1: Model calls get_weather("paris") → "18°C"
Step 2: Model calls calculator("18 + 10")  → "28"
Step 3: Model answers: "Paris is 18°C. 10 degrees warmer would be 28°C."
```

The model chained two tool calls to answer one question. You didn't tell it to do this —
it figured out the steps itself.

### Decision tracing (Activity 8)

`verbose=True` in `AgentExecutor` prints every step the agent takes:
- Which tool it called
- What arguments it passed
- What the tool returned
- What it decided to do next

This makes the agent's "reasoning" visible — it's not a black box.

---

## Part 7: RAG — Retrieval Augmented Generation (rag.py)

### The problem RAG solves

LLMs are trained on data up to a cutoff date. They don't know about:
- Your company's internal documents
- Recent events
- Private information

And even for things they do know, they sometimes "hallucinate" — confidently make things up.

RAG solves this by making the model answer from YOUR documents, not its training data.

### How RAG works — two phases

**Phase 1: Indexing (done once, at startup)**

```
Your documents
    ↓
Split into small chunks (300 characters each)
    ↓
Each chunk → Embedding model → A list of numbers (a "vector")
    ↓
All vectors stored in FAISS (a vector database)
```

A vector is a list of ~768 numbers that represents the *meaning* of text.
Similar meaning = similar numbers. "Paris is in France" and "France contains Paris"
would have very similar vectors even though the words are different.

**Phase 2: Retrieval + Generation (every time a question is asked)**

```
User's question
    ↓
Question → Embedding model → Vector
    ↓
FAISS finds the chunks whose vectors are closest to the question's vector
    ↓
Retrieved chunks passed to the model as context
    ↓
Model answers using ONLY those chunks
```

### The RAG prompt

```python
rag_prompt = ChatPromptTemplate.from_template("""
Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have that information."

Context:
{context}

Question: {question}
""")
```

"Use ONLY the context" is the instruction that grounds the model to your documents.
Without it, the model would mix in its own training knowledge.

### What proves it's working

We asked "What is the population of Tokyo?" — which is NOT in any of our documents.
The model said "I don't have that information in my documents."
If it had said a number, it would have been hallucinating from training data.

---

## Part 8: How all the files relate

```
prompts.py
└── Teaches the concept: templates with slots, filled by .invoke()

chatbot.py
├── Uses: ChatPromptTemplate, MessagesPlaceholder
├── Adds: InMemoryChatMessageHistory, RunnableWithMessageHistory
└── Teaches: memory = passing full history every call; session_id = separate threads

agent.py
├── Uses: ChatPromptTemplate, ChatGoogleGenerativeAI
├── Adds: @tool decorator, AgentExecutor, ReAct loop
└── Teaches: agents reason + act in a loop; tools extend what the model can DO

rag.py
├── Uses: ChatPromptTemplate, ChatGoogleGenerativeAI, Document
├── Adds: embeddings, FAISS vector store, retriever, text splitter
└── Teaches: ground answers in your documents; retrieval = semantic search
```

---

## Part 9: The vocabulary — quick reference

| Term | What it means |
|------|---------------|
| LLM | A model that predicts next tokens, trained on massive text data |
| Token | A chunk of text (~4 characters). Models think in tokens, not words |
| Temperature | How random the output is. 0 = deterministic, 1 = very creative |
| Prompt | The instruction/text you send to the model |
| System message | Instructions that set the model's persona/rules |
| Human message | What the "user" says in the conversation |
| Chain | A sequence of steps connected with `\|` — output of one feeds the next |
| Agent | A model that loops: reason → call tool → observe result → repeat |
| ReAct | The agent loop pattern: **Re**ason then **Act** |
| Tool | A Python function the agent can call to get real-world information |
| Embedding | Text converted to a list of numbers representing its meaning |
| Vector store | A database optimized for storing and searching vectors |
| RAG | Using retrieved document chunks as context for model answers |
| Session ID | A key that identifies which conversation thread to use |
| .invoke() | The standard way to run any LangChain component with input |
| verbose=True | Print every step the agent takes so you can see its reasoning |

---

## Part 10: The mental model that ties it all together

```
Every LLM call is just:

    [list of messages]  →  [Gemini]  →  [next message]

Everything else — memory, agents, RAG — is just:
    - Different ways of building that list of messages
    - Different ways of using the response
```

- **Memory** = automatically adding past messages to the list
- **Agent** = letting the model request tool calls, running them, adding results to the list
- **RAG** = searching your documents and adding the relevant chunks to the list

The model itself never changes. Only the messages you send it change.
```
