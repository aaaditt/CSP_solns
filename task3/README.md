# Multi-Tool AI Agent (Task 3)

A LangChain-based agent that picks the right tool for each query — calculator, web search, or PDF Q&A — with a Streamlit chat interface.

## Architecture

```
User Input → Streamlit UI → LangChain Agent → Tool Selection
                                                    ↓
                                          ┌─────────┼─────────┐
                                          ↓         ↓         ↓
                                     Calculator  Web Search  PDF Tools
                                          ↓         ↓         ↓
                                          └─────────┼─────────┘
                                                    ↓
                                            Combined Response
```

## Tools

| Tool | Description |
|------|-------------|
| **Calculator** | Evaluates math expressions safely via AST (no `eval()`). Supports +, -, ×, ÷, powers, percentages |
| **Web Search** | Searches the web via Tavily API. Returns top 3 results with titles and URLs |
| **PDF Load** | Extracts text from uploaded PDF files using PyPDF2 |
| **PDF Query** | Answers questions about the loaded PDF content |

## Setup

### 1. Create a virtual environment

```bash
cd task3
python -m venv venv
venv\Scripts\activate      # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your API keys

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

- **Google API Key** — [Google AI Studio](https://aistudio.google.com/apikey)
- **Tavily API Key** — free at [tavily.com](https://tavily.com) (1000 searches/month)

### 4. Run

```bash
streamlit run app.py
```

## Example Queries

- `Calculate 15% VAT on 250 AED`
- `What is the latest AI news?`
- `Summarize this PDF` (after uploading one)
- `Search for LangChain and calculate 10% growth on 5000 AED` (multi-tool)

## Bonus Features

- **Chat Interface** — full Streamlit chat UI with PDF upload sidebar
- **Tool Usage History** — sidebar shows which tools ran and how long they took

## Tech Stack

Python · LangChain · LangGraph · Google Gemini 2.5 Flash · Tavily API · PyPDF2 · Streamlit
