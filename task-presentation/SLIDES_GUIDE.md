# Presentation Guide — Internship Slides (for Canva)

**Target:** 6 core slides (+ 1 optional demo slide). Talk length ~10–15 minutes.
**How to use this file:** Each slide below gives you (1) a **Title**, (2) **On-slide text** you
can copy straight into Canva — keep it short, don't paste the speaker notes onto the slide,
(3) a **Visual suggestion**, and (4) **Speaker notes** = what you actually *say* out loud.

**The one idea that ties everything together (say this in your own words throughout):**
> "My internship went from data fundamentals → understanding how AI/LLM apps are built →
> shipping a real, deployed AI product."

**Timing map (aim ~12 min, leaves buffer for questions):**
| Slide | Topic | Time |
|-------|-------|------|
| 1 | Title | 0:30 |
| 2 | Overview / the journey | 2:00 |
| 3 | Task 1 — CSV Analyzer | 2:00 |
| 4 | Task 2 — LLM building blocks | 3:00 |
| 5 | Task 3 — Multi-Tool AI Agent | 3:00 |
| 6 | Learnings & conclusion | 1:30 |
| (7) | Optional live demo | +2:00 |

---

## Slide 1 — Title

**On-slide text:**
- **AI / LLM Application Development — Summer Internship**
- [Your Name]
- [University / Program] · [Course / Unit code]
- [Month Year]

**Visual suggestion:** Clean title slide. A row of small logos along the bottom:
Python, LangChain, Google Gemini, Streamlit. One accent color used consistently across all slides.

**Speaker notes (~30s):**
"Hi, I'm [name]. Over my summer internship I worked on three tasks that build on each other —
starting with core Python data handling, then learning how modern AI applications are built,
and finally shipping a working AI web app. I'll walk through each and what I took away."

---

## Slide 2 — Overview: The Journey

**On-slide text:**
- **Three tasks, one progression:**
- 1️⃣ **Task 1 — Data fundamentals** (Python + pandas)
- 2️⃣ **Task 2 — The LLM building blocks** (LangChain + Gemini)
- 3️⃣ **Task 3 — A deployed AI product** (Streamlit Cloud)
- *Tech stack:* Python · pandas · LangChain · LangGraph · Google Gemini · FAISS · Tavily · Streamlit

**Visual suggestion:** A horizontal 3-step arrow diagram: **Fundamentals → Building blocks →
Shipped product.** Put a small icon in each box (spreadsheet → gears/brain → globe/rocket).

**Speaker notes (~2 min):**
"The three tasks weren't random — they form a deliberate learning curve.
Task 1 was about handling data reliably in Python with pandas — no AI yet, just the foundation.
Task 2 was where I learned the actual building blocks of AI applications — memory, tools, and
retrieval — using LangChain with Google's Gemini model.
Task 3 is where it all came together: I built and *deployed* a real multi-tool AI agent as a web
app that anyone can use in the browser.
So the story is: get the fundamentals right, understand the pieces, then ship something real."

---

## Slide 3 — Task 1: CSV Analyzer

**On-slide text:**
- **Goal:** A command-line tool to explore any CSV file (Python + pandas)
- **Features:**
  - Summary: rows, columns, data types, missing values, numeric stats
  - Filter (type-aware), Sort, Export to CSV
  - Robust error handling (missing file, empty file, bad input)
- **Growth:** started as a basic summarizer → grew into a full interactive tool

**Visual suggestion:** A screenshot of the terminal running the summary (the "DATA SUMMARY" box).
Optional: a tiny "before/after" — `csv_basic.py` (just summary) vs `csv_analyzer.py` (full menu).

**Speaker notes (~2 min):**
"Task 1 was pure Python and pandas — no AI. The goal was a tool that loads any CSV and gives you
a full picture: how many rows and columns, the data types, how many values are missing, and basic
statistics for the numeric columns.
On top of that it can filter, sort, and export. One detail I'm happy with: the filter is
*type-aware* — if the column is numeric it matches numbers, otherwise it does a case-insensitive
text match. And every operation has proper error handling, so a wrong filename or empty file gives
a friendly message instead of crashing.
I actually built it twice — a simple version first, then a polished interactive version — which
taught me a lot about iterating on code."

---

## Slide 4 — Task 2: Learning the LLM Building Blocks

**On-slide text:**
- **Goal:** Understand how AI apps are built — using LangChain + Gemini
- **Three concepts, three programs:**
  - 🧠 **Chatbot → memory** (remembers the conversation)
  - 🛠️ **Agent → tools** (decides to run a calculator, weather lookup, etc.)
  - 📚 **RAG → your documents** (answers only from given text)
- **The mental model:** every AI call is just **[messages] → Gemini → next message**

**Visual suggestion:** Three columns/cards side by side — Memory · Tools · RAG — each with an icon.
Below them, one strip showing the arrow: `[messages] → Gemini → reply`.

**Speaker notes (~3 min):**
"Task 2 was the conceptual heart of the internship. Instead of one app, I built three small
programs, each teaching one building block of AI applications.
The **chatbot** taught me *memory*: an AI model has no memory on its own, so 'remembering' means
re-sending the whole conversation each time. LangChain handles that automatically per session.
The **agent** taught me *tools*: I gave the model a calculator, a weather lookup, and a word
counter, and the model itself decides which one to call — and can even chain them. For example,
'what's the temperature in Paris, plus 10 degrees' makes it call weather, then the calculator.
One security detail: my calculator never uses Python's dangerous `eval()` — it safely parses the
math instead.
The **RAG** program taught me how to make the AI answer from *my* documents — it finds the most
relevant text and instructs the model to answer using only that, which prevents made-up answers.
The big takeaway: all three are really the same thing — you're just building the list of messages
you send to the model in different ways."

---

## Slide 5 — Task 3: Multi-Tool AI Agent (Deployed)

**On-slide text:**
- **Goal:** A real, deployed AI web app that picks the right tool for the job
- **Built with:** Streamlit + LangGraph ReAct agent + Gemini
- **4 tools:** 🧮 Calculator · 🌐 Live Web Search (Tavily) · 📄 PDF Load · 📄 PDF Q&A
- **Features:** chat interface, multi-tool chaining, tool-usage history panel
- **Deployed on Streamlit Cloud** — runs in the browser, no install

**Visual suggestion:** Screenshot of your running Streamlit app (chat + sidebar). Next to it, a
simple flow diagram: **User → Chat UI → Agent → [Calculator / Web Search / PDF] → Answer.**

**Speaker notes (~3 min):**
"Task 3 brought everything together into a product. It's a web app — built with Streamlit and
deployed to Streamlit Cloud — so anyone can open it in a browser and chat with it.
Behind the chat is a ReAct agent that has four tools: a calculator, a live web search, and the
ability to load a PDF and answer questions about it. The agent reads your question and decides
which tool to use — and it can combine them in a single answer.
Two things I'm proud of here. First, the web search: the search service returns data in a few
different formats, so I wrote code to normalize all of them into clean, readable text. Second,
deployment: locally the app reads API keys from a file, but on the cloud there's no such file, so
I added a 'bridge' that reads the keys from Streamlit's secure secrets — so the exact same code
runs in both places.
There's also a sidebar that shows a history of which tools were used and how long each took."

---

## Slide 6 — Key Learnings & Conclusion

**On-slide text:**
- **What I learned:**
  - Data handling with pandas + clean error handling
  - How LLM apps work: prompts, memory, agents/tools, RAG
  - Writing safe code (AST-based calculator instead of `eval()`)
  - Deploying a real app + managing secrets (local vs cloud)
- **From fundamentals → building blocks → a shipped product**
- **Next steps:** persistent memory, per-user sessions, more tools

**Visual suggestion:** Reuse the 3-step arrow from Slide 2 with a checkmark on each, plus a short
"skills gained" list. End on a clean closing line + "Thank you / Questions?"

**Speaker notes (~1.5 min):**
"To wrap up — across the three tasks I went from solid Python data handling, to understanding the
core building blocks of AI applications, to actually deploying one.
Along the way I picked up practical habits: writing robust error handling, thinking about security
(like avoiding `eval`), and dealing with the real-world gap between running code locally and in the
cloud.
If I continued this, I'd add persistent memory, proper per-user sessions, and more tools.
Thank you — I'm happy to take any questions, or give a quick live demo."

---

## Slide 7 (Optional) — Live Demo / Screenshots

**On-slide text:**
- **Live demo:** [your Streamlit Cloud URL]
- Example prompts to try:
  - "What is 15% of 2500?"  (calculator)
  - "Search for the latest LangChain release" (web search)
  - Upload a PDF → "Summarize this document" (PDF Q&A)

**Visual suggestion:** Big QR code / URL to the deployed app, plus 2–3 screenshots of it answering.

**Speaker notes (~2 min):**
"If there's time, here's the app live. I'll ask it a math question, then a web-search question, and
then upload a PDF and ask about it — you can watch it pick the right tool each time in the sidebar."

---

### Presentation tips
- **Don't read the slides** — the on-slide text is the summary; your speaker notes are the story.
- Keep each slide to **~5 bullets max**; use the visuals to carry the weight.
- **Rehearse once with a timer** — you're aiming for 10–15 min, so ~2 min per content slide.
- Have the **live app open in a tab** as backup even if you don't formally demo it.
- If asked "what was hardest?", good honest answers: normalizing the web-search output, or getting
  secrets working on Streamlit Cloud (both are real things you solved).
