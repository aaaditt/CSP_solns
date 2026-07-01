"""Streamlit chat UI for the multi-tool agent. Run with: streamlit run app.py"""

import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from agent.agent import create_my_agent, run_agent, tool_history

load_dotenv()

# Bridge Streamlit Cloud secrets → env vars (so os.getenv works on both local and cloud)
for key in ["GOOGLE_API_KEY", "TAVILY_API_KEY"]:
    if key not in os.environ:
        try:
            os.environ[key] = st.secrets[key]
        except (KeyError, FileNotFoundError):
            pass

st.set_page_config(
    page_title="Multi-Tool AI Agent",
    page_icon="🤖",
    layout="wide",
)

# Session state
if "agent" not in st.session_state:
    st.session_state.agent = create_my_agent()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar — PDF upload + tool history
with st.sidebar:
    st.header("📄 Upload PDF")
    uploaded_file = st.file_uploader(
        "Upload a PDF to ask questions about it",
        type=["pdf"],
    )

    if uploaded_file and uploaded_file.name not in st.session_state.get("loaded_pdfs", []):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        with st.spinner("Loading PDF..."):
            run_agent(
                st.session_state.agent,
                f"Load this PDF file: {tmp_path}",
                st.session_state.messages,
            )
            st.success(f"✅ Loaded: {uploaded_file.name}")

            if "loaded_pdfs" not in st.session_state:
                st.session_state.loaded_pdfs = []
            st.session_state.loaded_pdfs.append(uploaded_file.name)

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"📄 PDF loaded: **{uploaded_file.name}**. You can now ask questions about it!",
            })

    st.divider()

    st.header("🔧 Tool Usage History")
    if tool_history:
        for entry in reversed(tool_history[-10:]):
            with st.expander(f"{entry['tool']} ({entry['time_seconds']}s)"):
                st.text(entry["output"][:300])
    else:
        st.caption("No tools used yet. Start chatting!")

# Main chat area
st.title("🤖 Multi-Tool AI Agent")
st.caption("Calculator · Web Search · PDF Summarizer — powered by LangChain + Gemini")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(
                st.session_state.agent,
                user_input,
                st.session_state.messages[:-1],
            )
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
