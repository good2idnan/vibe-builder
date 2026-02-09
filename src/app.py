"""
VibeBuilder V2 - Fixed Component Error
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import sys
import time
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

st.set_page_config(
    page_title="VibeBuilder",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimal CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    #MainMenu, footer, .stDeployButton, header {display: none !important; visibility: hidden;}
    
    .stApp {
        background: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        padding: 2rem !important;
        max-width: 1100px !important;
    }
    
    .header {
        text-align: center;
        padding: 3rem 0 2rem 0;
    }
    
    .header h1 {
        font-size: 1.75rem;
        font-weight: 600;
        color: #202123;
        margin: 0;
    }
    
    .header p {
        color: #6e6e80;
        font-size: 0.95rem;
        margin-top: 0.5rem;
    }
    
    .stTextArea textarea {
        border: 1px solid #d9d9e3 !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        font-size: 1rem !important;
        background: #ffffff !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #10a37f !important;
        box-shadow: none !important;
    }
    
    .stButton > button {
        background: #10a37f !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background: #0d8a6c !important;
    }
    
    .step-box {
        background: #f7f7f8;
        border-left: 3px solid #10a37f;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .step-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #10a37f;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    
    .step-content {
        font-size: 0.9rem;
        color: #202123;
    }
    
    .error-box {
        background: #fef2f2;
        border-left: 3px solid #ef4444;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        color: #991b1b;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'idea' not in st.session_state:
    st.session_state.idea = ''
if 'code' not in st.session_state:
    st.session_state.code = ''
if 'built' not in st.session_state:
    st.session_state.built = False

API_KEY = os.getenv("GOOGLE_API_KEY", "")


def show_welcome():
    """Welcome page"""
    st.markdown("""
    <div class="header">
        <h1>🔨 VibeBuilder</h1>
        <p>Describe your app idea and watch AI build it</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not API_KEY:
        st.error("Add `GOOGLE_API_KEY=your_key` to `.env` file")
        st.stop()
    
    idea = st.text_area(
        "What would you like to build?",
        placeholder="A todo app with dark mode...",
        height=100,
        label_visibility="collapsed"
    )
    
    if st.button("Build →", use_container_width=True):
        if idea.strip():
            st.session_state.idea = idea
            st.session_state.page = 'building'
            st.session_state.code = ''
            st.session_state.built = False
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Examples:")
    cols = st.columns(4)
    for i, ex in enumerate(["Todo app", "Calculator", "Timer", "Notes"]):
        with cols[i]:
            if st.button(ex, key=f"ex{i}", use_container_width=True):
                st.session_state.idea = ex
                st.session_state.page = 'building'
                st.session_state.code = ''
                st.session_state.built = False
                st.rerun()


def show_building():
    """Building page"""
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"**Building:** {st.session_state.idea[:60]}")
    with col2:
        if st.button("New"):
            st.session_state.page = 'welcome'
            st.session_state.code = ''
            st.session_state.built = False
            st.rerun()
    
    st.divider()
    
    left, right = st.columns([1, 1])
    
    with left:
        st.markdown("##### Progress")
        
        if not st.session_state.built:
            run_build()
        else:
            st.success("✅ Build complete!")
        
        # Refinement
        if st.session_state.code:
            st.divider()
            feedback = st.text_input("Want changes?", placeholder="Make button bigger...")
            if st.button("Apply") and feedback:
                apply_changes(feedback)
    
    with right:
        st.markdown("##### Result")
        
        if st.session_state.code:
            tab1, tab2 = st.tabs(["Preview", "Code"])
            with tab1:
                components.html(st.session_state.code, height=450, scrolling=True)
            with tab2:
                st.code(st.session_state.code, language="html")
                st.download_button("Download", st.session_state.code, "app.html", "text/html")
        else:
            st.info("Your app will appear here...")


def run_build():
    """Execute build"""
    try:
        from agents.orchestrator import VibeBuilderOrchestrator
    except ImportError as e:
        st.markdown(f'<div class="error-box">Import Error: {e}</div>', unsafe_allow_html=True)
        st.session_state.built = True
        return
    
    try:
        orchestrator = VibeBuilderOrchestrator(API_KEY)
        steps = {1: "Research", 2: "Plan", 3: "Code", 4: "Test", 6: "Fix", 8: "Complete"}
        
        for update in orchestrator.build(st.session_state.idea, max_iterations=2):
            step = update.get("step", 0)
            phase = update.get("phase", "")
            status = update.get("status", "")
            message = update.get("message", "")
            step_name = steps.get(step, "Working")
            
            st.markdown(f'''
            <div class="step-box">
                <div class="step-label">{step_name}</div>
                <div class="step-content">{message}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Capture code
            if phase == "code" and status == "complete":
                code = update.get("data", {}).get("code", "")
                if code:
                    st.session_state.code = code
            
            elif phase == "fix" and status == "complete":
                code = update.get("data", {}).get("fixed_code", "")
                if code:
                    st.session_state.code = code
            
            elif phase == "export":
                code = update.get("final_code", st.session_state.code)
                if code:
                    st.session_state.code = code
        
        st.session_state.built = True
        st.success("✅ Build complete!")
        st.rerun()  # Rerun to show the result
        
    except Exception as e:
        st.markdown(f'<div class="error-box">Error: {str(e)[:200]}</div>', unsafe_allow_html=True)
        st.session_state.built = True


def apply_changes(feedback: str):
    """Apply refinement"""
    try:
        from agents.orchestrator import VibeBuilderOrchestrator
        
        st.markdown(f'''
        <div class="step-box">
            <div class="step-label">Refine</div>
            <div class="step-content">Applying: {feedback[:50]}...</div>
        </div>
        ''', unsafe_allow_html=True)
        
        orchestrator = VibeBuilderOrchestrator(API_KEY)
        
        for update in orchestrator.refine(st.session_state.code, feedback):
            if update.get("status") == "complete":
                code = update.get("refined_code", st.session_state.code)
                st.session_state.code = code
        
        st.success("✅ Changes applied!")
        st.rerun()
        
    except Exception as e:
        st.markdown(f'<div class="error-box">Error: {str(e)[:100]}</div>', unsafe_allow_html=True)


# Main router
if st.session_state.page == 'welcome':
    show_welcome()
else:
    show_building()

st.caption("VibeBuilder V2 • Gemini Hackathon")
