# app.py
import streamlit as st
import os
import time
import shutil
import re
from app_agents import AppAgentOrchestrator

# --- Page Configuration ---
st.set_page_config(
    page_title="Abound | AI Agent Workflow",
    page_icon="🤖",
    layout="wide"
)

# --- AVATARS ---
AVATARS = {
    "Senior Analyst": "assets/senior.png",
    "Statistician": "assets/statistician.png",
    "Analyst": "assets/analyst.png",
    "System": "🤖"
}

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "run_generator" not in st.session_state:
    st.session_state.run_generator = None
if "analysis_running" not in st.session_state:
    st.session_state.analysis_running = False

# --- UI Rendering ---
st.title("Abound B2B Credit Assessment")
st.caption("A multi-agent system for analyzing business financial health.")

# --- Step 1: File Uploader ---
st.subheader("1. Upload Your Data")
uploaded_file = st.file_uploader(
    "Upload a CSV file containing transaction history.",
    type=["csv"]
)

if uploaded_file:
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

# --- Step 2: Define Analytical Objective ---
st.subheader("2. Define the Analytical Objective 🎯")
user_prompt = st.text_area(
    "What do you want to understand about this data?",
    placeholder="e.g., Analyze the monthly cash flow and identify the top 5 spending categories.",
    key="user_prompt",
    height=100
)

# --- Step 3: Start Button ---
st.subheader("3. Start the Analysis")
start_button = st.button(
    "▶️ Start New Analysis",
    type="primary",
    disabled=not uploaded_file or not st.session_state.user_prompt or st.session_state.analysis_running
)

st.divider()

# --- Display existing chat messages ---
for msg in st.session_state.messages:
    avatar_path = AVATARS.get(msg["author"])
    if avatar_path and not os.path.exists(avatar_path):
        avatar_path = None

    with st.chat_message(msg["author"], avatar=avatar_path):
        if msg["type"] == "reasoning":
            st.info(f"**Reasoning:**\n\n{msg['content']}")
        elif msg["type"] == "directive":
            st.code(msg["content"], language="python", line_numbers=True)
        elif msg["type"] == "analyst_output":
            st.text(msg["content"])
        elif msg["type"] == "attachment":
            st.markdown(f"**Attachment:** {msg['content']}")
            if msg["path"].endswith(('.png', '.jpg')):
                st.image(msg["path"])
            elif msg["path"].endswith('.md'):
                with open(msg["path"], 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                with st.expander("View Report"):
                    lines_buffer = report_content.split('\n')
                    text_chunk = []
                    for line in lines_buffer:
                        image_match = re.match(r'!\[(.*)\]\((.*)\)', line.strip())
                        if image_match:
                            if text_chunk:
                                st.markdown("\n".join(text_chunk), unsafe_allow_html=True)
                                text_chunk = []
                            caption = image_match.group(1)
                            path = image_match.group(2)
                            image_path = path.lstrip('./').lstrip('/') # Robust path correction
                            if os.path.exists(image_path):
                                st.image(image_path, caption=caption)
                            else:
                                st.error(f"Image not found at path: {image_path}")
                        else:
                            text_chunk.append(line)
                    if text_chunk:
                        st.markdown("\n".join(text_chunk), unsafe_allow_html=True)
        else: # System messages
            st.markdown(f"*{msg['content']}*")

# --- App Execution Logic ---
if start_button and uploaded_file and st.session_state.user_prompt:
    # Cleanup logic for a new run
    if os.path.exists("output"):
        shutil.rmtree("output")
    os.makedirs("output")
    
    # Save the uploaded file locally
    os.makedirs("data", exist_ok=True)
    save_path = os.path.join("data", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    st.session_state.messages = []
    st.session_state.analysis_running = True
    
    orchestrator = AppAgentOrchestrator()
    st.session_state.run_generator = orchestrator.run(save_path, st.session_state.user_prompt)
    
    st.session_state.messages.append({"type": "system", "author": "System", "content": f"Orchestrator initialized. Starting analysis on `{uploaded_file.name}` with the objective: '{st.session_state.user_prompt}'..."})
    st.rerun()

# Main generator loop to process agent events
if st.session_state.analysis_running:
    try:
        event = next(st.session_state.run_generator)
        st.session_state.messages.append(event)
        time.sleep(1) 
        st.rerun()
    except StopIteration:
        final_message = {"type": "system", "author": "System", "content": "✅ **Workflow Complete!** All cycles finished."}
        st.session_state.messages.append(final_message)
        st.session_state.analysis_running = False
        st.balloons()
        st.rerun()