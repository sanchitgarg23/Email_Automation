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

# Page Setup
st.set_page_config(
    page_title="SG AI • Email Automation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End SaaS CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Hero Header Card */
    .hero-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 6px;
        margin-bottom: 14px;
    }

    /* Badges */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.04);
        color: #e2e8f0;
        margin-right: 8px;
    }

    .badge-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 8px #10b981;
    }

    /* Metric Tiles */
    .metric-box {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 18px 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-box:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #f8fafc;
        margin-top: 4px;
    }

    /* Pipeline Visualizer */
    .pipeline-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 24px;
        overflow-x: auto;
    }
    .pipeline-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        min-width: 110px;
    }
    .step-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #818cf8;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 6px;
    }
    .step-name {
        font-size: 0.76rem;
        font-weight: 600;
        color: #cbd5e1;
    }
    .step-arrow {
        color: #475569;
        font-size: 1.1rem;
        margin: 0 4px;
    }

    /* Email Card */
    .draft-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 18px;
        transition: border-color 0.2s ease;
    }
    .draft-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
    }
    .draft-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        padding-bottom: 12px;
    }
    .sender-avatar {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .cat-enquiry {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .cat-complaint {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .cat-feedback {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "stats" not in st.session_state:
    st.session_state.stats = {"scanned": 0, "drafts": 0, "unrelated": 0}
if "pipeline_events" not in st.session_state:
    st.session_state.pipeline_events = []


# Sidebar
with st.sidebar:
    st.markdown("### ⚡ SG AI System")
    st.caption("Autonomous LangGraph Multi-Agent Assistant")
    st.markdown("---")

    st.markdown("#### **Deployment Profile**")
    st.markdown(f"**Maintainer:** Sanchit Garg")
    st.markdown(f"**Connected Gmail:**\n`{settings.my_email}`")
    st.markdown(f"**Groq Model:**\n`{settings.groq_model}`")
    st.markdown(f"**Vector Store:**\n`ChromaDB (Local MiniLM)`")

    mode_badge = "🟢 Auto-Send Live" if settings.auto_send else "🛡️ Draft Review Mode"
    st.info(f"**Execution Mode:** {mode_badge}")

    st.markdown("---")
    st.markdown("#### **Knowledge Base (RAG)**")
    with st.expander("📄 View `data/agency.txt`", expanded=False):
        agency_path = "data/agency.txt"
        if os.path.exists(agency_path):
            with open(agency_path, "r", encoding="utf-8") as f:
                content = f.read()
            st.text_area("Indexed Content", content, height=220, disabled=True)
        else:
            st.warning("agency.txt not found")

    st.markdown("---")
    st.caption("SG AI Email Automation • v1.0.0")


# Hero Header Card
st.markdown("""
<div class="hero-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
            <h1 class="hero-title">SG AI Email Automation Command Center</h1>
            <p class="hero-subtitle">Multi-Agent LangGraph Orchestrator for Real-Time Gmail Processing, RAG Search & QA Proofreading</p>
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            <div class="badge-pill"><span class="badge-dot"></span> System Live</div>
            <div class="badge-pill">⚡ Groq LPU</div>
            <div class="badge-pill">🧠 Chroma ONNX</div>
            <div class="badge-pill">📬 Gmail API</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# High-Level Metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Inbox Evaluated</div>
        <div class="metric-value">{st.session_state.stats['scanned']}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Draft Replies Formulated</div>
        <div class="metric-value" style="color: #818cf8;">{st.session_state.stats['drafts']}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Spam & Marketing Filtered</div>
        <div class="metric-value" style="color: #94a3b8;">{st.session_state.stats['unrelated']}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Agent Engine Status</div>
        <div class="metric-value" style="color: #34d399; font-size: 1.25rem; padding-top: 6px;">Ready & Polling</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# Visual Workflow Pipeline Stepper
st.markdown("""
<div class="pipeline-container">
    <div class="pipeline-step">
        <div class="step-icon">1</div>
        <div class="step-name">Scan Inbox</div>
    </div>
    <div class="step-arrow">➔</div>
    <div class="pipeline-step">
        <div class="step-icon">2</div>
        <div class="step-name">Categorize</div>
    </div>
    <div class="step-arrow">➔</div>
    <div class="pipeline-step">
        <div class="step-icon">3</div>
        <div class="step-name">RAG Search</div>
    </div>
    <div class="step-arrow">➔</div>
    <div class="pipeline-step">
        <div class="step-icon">4</div>
        <div class="step-name">Draft Reply</div>
    </div>
    <div class="step-arrow">➔</div>
    <div class="pipeline-step">
        <div class="step-icon">5</div>
        <div class="step-name">QA Proofread</div>
    </div>
    <div class="step-arrow">➔</div>
    <div class="pipeline-step">
        <div class="step-icon" style="background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.3); color: #34d399;">6</div>
        <div class="step-name">Gmail Action</div>
    </div>
</div>
""", unsafe_allow_html=True)


# Tabs for Operations, Interactive Playground, and RAG Explorer
tab_ops, tab_playground, tab_rag = st.tabs(["🚀 Operations & Live Feed", "🧪 Custom Email Playground", "📚 Vector RAG Explorer"])


def execute_workflow(is_simulation: bool, custom_email=None):
    if is_simulation:
        if custom_email:
            class CustomMockGmailTools:
                def __init__(self):
                    self._emails = [custom_email]
                def fetch_unanswered_emails(self, max_results=50):
                    res = list(self._emails)
                    self._emails = []
                    return res
                def create_draft_reply(self, initial_email, reply_text):
                    return {"id": "custom_mock_draft"}
                def send_reply(self, initial_email, reply_text):
                    return {"id": "custom_mock_sent"}
            src.nodes.GmailToolsClass = CustomMockGmailTools
        else:
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

    with st.status(f"⚡ Running {mode_label} LangGraph Orchestrator...", expanded=True) as status_box:
        st.write("📥 **Step 1: Ingesting recent email threads...**")

        for output in app.stream(initial_state, config):
            for node_name, state_update in output.items():
                if node_name == "load_inbox_emails":
                    emails = state_update.get("emails", [])
                    scanned_count = len(emails)
                    st.write(f"📥 Loaded `{len(emails)}` email(s) from inbox queue.")

                elif node_name == "categorize_email":
                    cat = state_update.get("email_category", "")
                    email = state_update.get("current_email")
                    sender = email.sender if hasattr(email, "sender") else "Unknown"
                    st.write(f"🏷️ **Intent Classified:** `{sender}` ➔ **`{cat}`**")

                elif node_name == "construct_rag_queries":
                    queries = state_update.get("rag_queries", [])
                    st.write(f"🔍 **Generated RAG Search Queries:** `{queries}`")

                elif node_name == "retrieve_from_rag":
                    st.write("🧠 **ChromaDB Semantic Search:** Retrieved knowledge context from local vector DB.")

                elif node_name == "email_writer":
                    st.write("✍️ **Email Writer Agent:** Composed initial draft response.")

                elif node_name == "email_proofreader":
                    sendable = state_update.get("sendable", False)
                    if sendable:
                        st.write("✅ **Proofreader QA Quality Passed:** Reply verified for accuracy & tone.")
                    else:
                        st.write("🔄 **Proofreader QA Quality Check:** Triggered revision loop.")

                elif node_name == "send_email":
                    draft_text = state_update.get("generated_email", "")
                    current_email = state_update.get("current_email")
                    category = state_update.get("email_category", "product_enquiry")
                    generated_drafts.append({
                        "sender": getattr(current_email, "sender", "Customer"),
                        "subject": getattr(current_email, "subject", "Inquiry"),
                        "category": category,
                        "reply": draft_text,
                        "timestamp": datetime.now().strftime("%I:%M %p")
                    })
                    st.write(f"📬 **Gmail Action Executed:** Draft created in Gmail!")

                elif node_name == "skip_unrelated_email":
                    unrelated_count += 1
                    st.write("🛡️ **Spam Filter:** Skipped promotional / unrelated email.")

        status_box.update(
            label=f"🎉 {mode_label} Pipeline Successfully Executed!",
            state="complete",
            expanded=False,
        )

    # Update session statistics
    st.session_state.stats["scanned"] += scanned_count
    st.session_state.stats["drafts"] += len(generated_drafts)
    st.session_state.stats["unrelated"] += unrelated_count

    for draft in generated_drafts:
        st.session_state.history.insert(0, draft)

    if scanned_count == 0 and not is_simulation:
        st.info("ℹ️ No new unanswered emails found in your Gmail inbox in the last 8 hours.")


# TAB 1: OPERATIONS & LIVE FEED
with tab_ops:
    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
    with col_btn1:
        live_scan = st.button("🚀 Scan Live Gmail Inbox", type="primary", use_container_width=True)
    with col_btn2:
        sample_sim = st.button("🧪 Run Sample Simulation (3 Scenarios)", use_container_width=True)
    with col_btn3:
        if st.button("🗑️ Reset", use_container_width=True):
            st.session_state.history = []
            st.session_state.stats = {"scanned": 0, "drafts": 0, "unrelated": 0}
            st.rerun()

    if live_scan:
        execute_workflow(is_simulation=False)

    if sample_sim:
        execute_workflow(is_simulation=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📬 Generated Draft Responses")

    if not st.session_state.history:
        st.markdown("""
        <div style="text-align: center; padding: 40px; background: rgba(17, 24, 39, 0.4); border-radius: 12px; border: 1px dashed rgba(255, 255, 255, 0.1);">
            <div style="font-size: 2.2rem; margin-bottom: 8px;">📭</div>
            <div style="font-weight: 600; color: #cbd5e1;">No drafts generated in this session yet</div>
            <div style="color: #64748b; font-size: 0.88rem; margin-top: 4px;">Click 'Scan Live Gmail Inbox' or 'Run Sample Simulation' above to trigger the agents.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, item in enumerate(st.session_state.history):
            badge_class = "cat-enquiry"
            if item.get("category") == "customer_complaint":
                badge_class = "cat-complaint"
            elif item.get("category") == "customer_feedback":
                badge_class = "cat-feedback"

            initial = item["sender"][:1].upper() if item["sender"] else "C"

            st.markdown(f"""
            <div class="draft-card">
                <div class="draft-header">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div class="sender-avatar">{initial}</div>
                        <div>
                            <div style="font-weight: 700; font-size: 1.05rem; color: #f8fafc;">Re: {item['subject']}</div>
                            <div style="color: #94a3b8; font-size: 0.85rem;">To: <span style="color: #cbd5e1; font-family: monospace;">{item['sender']}</span> • {item['timestamp']}</div>
                        </div>
                    </div>
                    <div>
                        <span class="{badge_class}">{item.get('category', 'product_enquiry')}</span>
                        <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-left: 6px;">QA Verified</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("📄 View & Copy Formulated Response", expanded=(idx == 0)):
                st.text_area("Email Content", value=item["reply"], height=280, key=f"draft_view_{idx}")


# TAB 2: INTERACTIVE CUSTOM EMAIL PLAYGROUND
with tab_playground:
    st.markdown("#### 🧪 Test Individual Customer Inquiries")
    st.caption("Compose a custom email or select a scenario to watch the LangGraph agent categorize, search RAG, and formulate a reply in real-time.")

    p_col1, p_col2 = st.columns([1, 1])
    with p_col1:
        preset = st.selectbox(
            "Quick Scenario Preset:",
            [
                "Custom (Type your own)",
                "Pricing Inquiry: Asking for Web Dev Packages & Onboarding",
                "Client Complaint: Project Delivery Deadline Missed",
                "Spam Offer: Cryptocurrency Promo"
            ]
        )

        default_sender = "sarah.connor@example.com"
        default_subject = "Inquiry about Agency Pricing and Services"
        default_body = "Hello Sanchit, I am interested in your web development and digital marketing services. Could you please share your pricing packages and onboarding process? Thanks!"

        if "Complaint" in preset:
            default_sender = "alex.rivera@enterprise.org"
            default_subject = "Urgent: Delivery Milestone Delayed"
            default_body = "Hi Team, we were promised the staging deployment by Friday. It is now Monday and we have received no updates. What is the status?"
        elif "Spam" in preset:
            default_sender = "promo@global-rewards.xyz"
            default_subject = "Claim your $1,000 gift card immediately!"
            default_body = "Congratulations! You have been selected to receive a complimentary gift. Click here to claim your reward."

        input_sender = st.text_input("Sender Email Address:", value=default_sender)
        input_subject = st.text_input("Email Subject:", value=default_subject)

    with p_col2:
        input_body = st.text_area("Email Body Message:", value=default_body, height=155)
        run_custom = st.button("⚡ Test Agent on this Email", type="primary", use_container_width=True)

    if run_custom:
        custom_payload = {
            "id": f"custom_{int(time.time())}",
            "threadId": f"t_{int(time.time())}",
            "messageId": f"m_{int(time.time())}",
            "references": "",
            "sender": input_sender,
            "subject": input_subject,
            "body": input_body,
        }
        execute_workflow(is_simulation=True, custom_email=custom_payload)


# TAB 3: VECTOR RAG EXPLORER
with tab_rag:
    st.markdown("#### 🧠 ChromaDB Semantic Search Inspector")
    st.caption("Test how the local on-device ONNX vector embeddings retrieve knowledge chunks from your agency database.")

    search_query = st.text_input("Test Knowledge Query:", value="What are your service pricing tiers?")
    if st.button("🔍 Search ChromaDB Vector Store"):
        try:
            from src.agents import LocalEmbeddings
            from langchain_chroma import Chroma

            embeddings = LocalEmbeddings()
            vectorstore = Chroma(persist_directory="db", embedding_function=embeddings)
            results = vectorstore.similarity_search_with_score(search_query, k=3)

            st.write(f"**Found {len(results)} relevant context chunks:**")
            for i, (doc, score) in enumerate(results):
                with st.expander(f"Chunk #{i+1} (Cosine Distance: {score:.4f})", expanded=True):
                    st.markdown(doc.page_content)
        except Exception as e:
            st.error(f"Error searching vector store: {e}")
