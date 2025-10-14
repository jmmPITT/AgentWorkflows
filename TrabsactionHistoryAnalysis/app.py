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

# Display existing chat messages
for msg in st.session_state.messages:
    # Use a default avatar if a specific one isn't found
    avatar_path = AVATARS.get(msg["author"])
    if avatar_path and not os.path.exists(avatar_path):
        avatar_path = None # Fallback to default icon if image file is missing

    with st.chat_message(msg["author"], avatar=avatar_path):
        if msg["type"] == "reasoning":
            st.info(f"**Reasoning:**\n\n{msg['content']}")
        elif msg["type"] == "directive":
            st.code(msg["content"], language="python", line_numbers=True)
        elif msg["type"] == "analyst_output":
            st.text(msg["content"])
        elif msg["type"] == "attachment":
            st.markdown(f"📎 **Attachment:** {msg['content']}")
            if msg["path"].endswith(('.png', '.jpg')):
                st.image(msg["path"])
            elif msg["path"].endswith('.md'):
                with open(msg["path"], 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                with st.expander("View Report"):
                    # *** NEW ROBUST RENDERING LOGIC ***
                    # We will parse the markdown line by line and render images manually.
                    
                    # Split the report into a buffer of lines
                    lines_buffer = report_content.split('\n')
                    # Use a list to accumulate markdown text between images
                    text_chunk = []

                    for line in lines_buffer:
                        # Check if the line is a markdown image tag
                        image_match = re.match(r'!\[(.*)\]\((.*)\)', line.strip())
                        
                        if image_match:
                            # If we have accumulated text, render it first.
                            if text_chunk:
                                st.markdown("\n".join(text_chunk), unsafe_allow_html=True)
                                text_chunk = [] # Reset the chunk

                            # Extract caption and path from the regex match
                            caption = image_match.group(1)
                            path = image_match.group(2)
                            
                            # Correct the path for Streamlit (remove leading slash)
                            image_path = path.lstrip('/') 

                            # Render the image using st.image, which we know works
                            if os.path.exists(image_path):
                                st.image(image_path, caption=caption)
                            else:
                                st.error(f"Image not found at path: {image_path}")
                        else:
                            # If it's not an image, add the line to our text chunk.
                            text_chunk.append(line)
                    
                    # Render any remaining text at the end of the report
                    if text_chunk:
                        st.markdown("\n".join(text_chunk), unsafe_allow_html=True)

        else: # System messages
            st.markdown(f"*{msg['content']}*")

# --- Main App Logic ---
start_button = st.button("🚀 Start New Analysis", type="primary", disabled=st.session_state.analysis_running)

if start_button:
    # Clean up previous run's output and state
    if os.path.exists("output"):
        shutil.rmtree("output")
    os.makedirs("output")
    
    st.session_state.messages = []
    st.session_state.analysis_running = True
    
    # Initialize the orchestrator generator
    orchestrator = AppAgentOrchestrator()
    local_csv_path = "data/artisan_digital_transactions.csv"
    st.session_state.run_generator = orchestrator.run(local_csv_path)
    
    st.session_state.messages.append({"type": "system", "author": "System", "content": "Orchestrator initialized. Starting analysis..."})
    st.rerun()

if st.session_state.analysis_running:
    try:
        # Get the next event from the agent workflow
        event = next(st.session_state.run_generator)
        st.session_state.messages.append(event)
        
        # Rerun the app to display the new message with a small delay for readability
        time.sleep(1) 
        st.rerun()

    except StopIteration:
        # The generator is exhausted, meaning the workflow is complete
        final_message = {"type": "system", "author": "System", "content": "🎉 **Workflow Complete!** All cycles finished."}
        st.session_state.messages.append(final_message)
        st.session_state.analysis_running = False
        st.balloons()
        st.rerun()