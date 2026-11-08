import os
import time
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

from src.config import settings
from src.graph import Workflow
from simulate_run import SAMPLE_EMAILS, MockGmailTools
import src.nodes

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="SG AI Email Automation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Mode Accents)
st.markdown("""
<style>
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
    }
    .email-card {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .badge-product {
        background-color: #1f6feb;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
    .badge-complaint {
        background-color: #d29922;
        color: black;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
    .badge-unrelated {
        background-color: #6e7681;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "stats" not in st.session_state:
    st.session_state.stats = {"scanned": 0, "drafts": 0, "unrelated": 0}


# Sidebar
with st.sidebar:
    st.title("⚡ SG AI Automation")
    st.caption("Autonomous LangGraph Multi-Agent System")
    st.markdown("---")

    st.subheader("System Status")
    st.write(f"**Maintainer:** Sanchit Garg")
    st.write(f"**Connected Gmail:** `{settings.my_email}`")
    st.write(f"**Active LLM:** `{settings.groq_model}`")
    st.write(f"**Embeddings:** Local `all-MiniLM-L6-v2` (ONNX)")
    st.write(f"**Vector Store:** ChromaDB (`db/`)")
    
    send_mode = "Direct Auto-Send" if settings.auto_send else "Drafts Review Mode"
    st.write(f"**Action Mode:** `{send_mode}`")

    st.markdown("---")
    st.subheader("Agency Knowledge Base")
    with st.expander("Inspect `data/agency.txt`"):
        agency_file = "data/agency.txt"
        if os.path.exists(agency_file):
            with open(agency_file, "r", encoding="utf-8") as f:
                st.text(f.read())
        else:
            st.warning("agency.txt not found")

    st.markdown("---")
    st.caption("SG AI Email Automation v1.0 • Built with LangGraph & Streamlit")


# Main Dashboard Header
st.title("⚡ Multi-Agent Email Support Orchestrator")
st.markdown(
    "Automates incoming Gmail processing using LangGraph: email intent classification, "
    "local RAG knowledge retrieval, draft generation, and automated QA proofreading."
)

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Emails Evaluated", st.session_state.stats["scanned"])
col2.metric("Draft Replies Created", st.session_state.stats["drafts"])
col3.metric("Spam / Filtered", st.session_state.stats["unrelated"])
col4.metric("Engine Health", "Online (Groq + Chroma)")

st.markdown("---")

# Operations Controls
st.subheader("Workflow Operations")
btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 2])

scan_clicked = btn_col1.button("🚀 Scan Live Gmail Inbox", type="primary", use_container_width=True)
sim_clicked = btn_col2.button("🧪 Run Test Simulation", use_container_width=True)
clear_clicked = btn_col3.button("🗑️ Clear Activity History", use_container_width=True)

if clear_clicked:
    st.session_state.history = []
    st.session_state.stats = {"scanned": 0, "drafts": 0, "unrelated": 0}
    st.rerun()


def run_pipeline(is_simulation: bool):
    # Setup tools based on mode
    if is_simulation:
        src.nodes.GmailToolsClass = MockGmailTools
        mode_label = "Simulation"
    else:
        from src.tools.GmailTools import GmailToolsClass as RealGmailTools
        src.nodes.GmailToolsClass = RealGmailTools
        mode_label = "Live Gmail"

    workflow = Workflow()
    app = workflow.app

    initial_state = {
        "emails": [],
        "current_email": {
            "id": "",
            "threadId": "",
            "messageId": "",
            "references": "",
            "sender": "",
            "subject": "",
            "body": "",
        },
        "email_category": "",
        "generated_email": "",
        "rag_queries": [],
        "retrieved_documents": "",
        "writer_messages": [],
        "sendable": False,
        "trials": 0,
    }

    config = {"recursion_limit": 100}
    generated_drafts = []
    scanned_count = 0
    unrelated_count = 0

    with st.status(f"Running {mode_label} Agent Pipeline...", expanded=True) as status_box:
        st.write("🔍 Initializing LangGraph state and fetching emails...")
        
        for output in app.stream(initial_state, config):
            for node_name, state_update in output.items():
                if node_name == "load_inbox_emails":
                    emails = state_update.get("emails", [])
                    scanned_count = len(emails)
                    st.write(f"📥 **Loaded Inbox:** Found `{len(emails)}` unaddressed email(s).")

                elif node_name == "categorize_email":
                    cat = state_update.get("email_category", "")
                    email = state_update.get("current_email")
                    sender = email.sender if hasattr(email, "sender") else "Unknown"
                    st.write(f"🏷️ **Categorized:** `{sender}` ➔ `{cat}`")

                elif node_name == "construct_rag_queries":
                    queries = state_update.get("rag_queries", [])
                    st.write(f"🔎 **Formulated RAG Queries:** {queries}")

                elif node_name == "retrieve_from_rag":
                    st.write("📚 **ChromaDB:** Semantic context retrieved from local vector store.")

                elif node_name == "email_writer":
                    st.write("✍️ **Email Writer:** Draft response synthesized.")

                elif node_name == "email_proofreader":
                    sendable = state_update.get("sendable", False)
                    if sendable:
                        st.write("✅ **Proofreader QA:** Approved for sending/drafting.")
                    else:
                        st.write("⚠️ **Proofreader QA:** Requested revision.")

                elif node_name == "send_email":
                    draft_text = state_update.get("generated_email", "")
                    current_email = state_update.get("current_email")
                    generated_drafts.append({
                        "sender": getattr(current_email, "sender", "Customer"),
                        "subject": getattr(current_email, "subject", "Inquiry"),
                        "reply": draft_text,
                        "timestamp": datetime.now().strftime("%I:%M %p")
                    })
                    st.write(f"📬 **Gmail Action:** Draft reply created successfully!")

                elif node_name == "skip_unrelated_email":
                    unrelated_count += 1
                    st.write("🛡️ **Spam Filter:** Skipped unrelated / promotional message.")

        status_box.update(
            label=f"{mode_label} Pipeline Complete!",
            state="complete",
            expanded=False
        )

    # Update stats
    st.session_state.stats["scanned"] += scanned_count
    st.session_state.stats["drafts"] += len(generated_drafts)
    st.session_state.stats["unrelated"] += unrelated_count

    # Save to history
    for draft in generated_drafts:
        st.session_state.history.insert(0, draft)

    if scanned_count == 0 and not is_simulation:
        st.info("No unanswered emails found in your Gmail inbox within the last 8 hours.")


# Trigger Pipeline Runs
if scan_clicked:
    run_pipeline(is_simulation=False)

if sim_clicked:
    run_pipeline(is_simulation=True)


# Activity & Drafts View
st.subheader("Generated Email Replies & Drafts")

if not st.session_state.history:
    st.info("No drafts generated yet. Click **'Scan Live Gmail Inbox'** or **'Run Test Simulation'** above to run the AI agents.")
else:
    for idx, item in enumerate(st.session_state.history):
        with st.expander(f"✉️ Re: {item['subject']} — To: {item['sender']} ({item['timestamp']})", expanded=(idx == 0)):
            st.markdown(f"**Recipient:** `{item['sender']}`")
            st.markdown(f"**Subject:** `Re: {item['subject']}`")
            st.markdown(f"**Status:** `Saved to Gmail Drafts`")
            st.text_area("Draft Content", value=item["reply"], height=260, key=f"draft_{idx}")
