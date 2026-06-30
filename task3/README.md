# Multi-Tool AI Agent (Task 3)

A LangChain-based AI agent that intelligently selects and uses different tools based on user queries. Features a Streamlit chat interface.

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

| Tool | What it does |
|------|-------------|
| **Calculator** | Evaluates math expressions safely (no `eval()`). Handles +, -, ×, ÷, powers, percentages |
| **Web Search** | Searches the web via Tavily API. Returns top 3 results with titles and URLs |
| **PDF Load** | Extracts text from uploaded PDF files using PyPDF2 |
| **PDF Query** | Answers questions about the loaded PDF content |

## Setup

### 1. Create virtual environment

```bash
cd task3
python -m venv venv
venv\Scripts\activate      # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set API keys

Edit the `.env` file:

```
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- **Google API Key**: From [Google AI Studio](https://aistudio.google.com/apikey)
- **Tavily API Key**: Free at [tavily.com](https://tavily.com) (1000 searches/month)

### 4. Run the app

```bash
streamlit run app.py
```

## Example Queries

- "Calculate 15% VAT on 250 AED"
- "What is the latest AI news?"
- "Summarize this PDF" (after uploading one)
- "Search for LangChain and calculate 10% growth on 5000 AED" (multi-tool)

## Bonus Features

1. **Streamlit Chat Interface** — Full chat UI with PDF upload sidebar
2. **Tool Usage History** — Sidebar shows which tools were called and execution time

## Tech Stack

- Python, LangChain, Google Gemini 2.5 Flash, Tavily API, PyPDF2, Streamlit
