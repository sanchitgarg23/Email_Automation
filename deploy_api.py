import os
import json
import asyncio
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from langserve import add_routes
from src.graph import Workflow
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = FastAPI(
    title="SG AI Email Automation",
    version="1.0",
    description="LangGraph backend & dashboard for AI Gmail automation workflow",
)

# Set CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


def get_runnable():
    return Workflow().app


# LangServe Playground & API routes
try:
    runnable = get_runnable()
    add_routes(app, runnable)
except Exception as e:
    print(f"[Warning] Could not initialize default LangServe runnable on startup: {e}")


# Dashboard UI route
@app.get("/", response_class=HTMLResponse)
async def dashboard_index():
    template_path = Path(__file__).parent / "templates" / "dashboard.html"
    if not template_path.exists():
        return HTMLResponse("<h1>Dashboard template not found</h1>", status_code=404)

    html_content = template_path.read_text(encoding="utf-8")
    user_email = os.getenv("MY_EMAIL", "sanchitgarg23april@gmail.com")
    groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    html_content = html_content.replace("{{ user_email }}", user_email)
    html_content = html_content.replace("{{ groq_model }}", groq_model)
    return HTMLResponse(content=html_content)


def serialize_email(email_obj):
    if hasattr(email_obj, "model_dump"):
        return email_obj.model_dump()
    elif isinstance(email_obj, dict):
        return email_obj
    return {
        "id": getattr(email_obj, "id", ""),
        "sender": getattr(email_obj, "sender", "Unknown"),
        "subject": getattr(email_obj, "subject", "No Subject"),
        "body": getattr(email_obj, "body", ""),
    }


# Server-Sent Events generator for live workflow progress
async def event_stream_generator(is_simulation=False):
    if is_simulation:
        from simulate_run import MockGmailTools
        import src.nodes
        src.nodes.GmailToolsClass = MockGmailTools

    workflow = Workflow()
    graph_app = workflow.app

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

    last_email = {}
    last_draft = ""
    last_proof = {}

    for output in graph_app.stream(initial_state, config):
        for node_name, state_chunk in output.items():
            if node_name == "load_inbox_emails":
                emails_loaded = state_chunk.get("emails", [])
                event = {"type": "node_load", "count": len(emails_loaded)}
                yield f"data: {json.dumps(event)}\n\n"

            elif node_name == "categorize_email":
                curr = state_chunk.get("current_email")
                last_email = serialize_email(curr) if curr else {}
                cat = state_chunk.get("email_category", "")
                event = {
                    "type": "email_categorized",
                    "sender": last_email.get("sender", "Unknown"),
                    "subject": last_email.get("subject", "No Subject"),
                    "category": cat,
                }
                yield f"data: {json.dumps(event)}\n\n"

            elif node_name == "construct_rag_queries":
                queries = state_chunk.get("rag_queries", [])
                event = {"type": "rag_retrieval", "queries": queries}
                yield f"data: {json.dumps(event)}\n\n"

            elif node_name == "email_writer":
                last_draft = state_chunk.get("generated_email", "")
                trial_num = state_chunk.get("trials", 1)
                event = {
                    "type": "draft_written",
                    "draft": last_draft,
                    "trial": trial_num,
                }
                yield f"data: {json.dumps(event)}\n\n"

            elif node_name == "email_proofreader":
                sendable = state_chunk.get("sendable", False)
                writer_msgs = state_chunk.get("writer_messages", [])
                feedback = writer_msgs[-1] if writer_msgs else ""
                event = {
                    "type": "email_proofread",
                    "sendable": sendable,
                    "feedback": feedback,
                }
                yield f"data: {json.dumps(event)}\n\n"

            elif node_name == "send_email":
                event = {
                    "type": "draft_created",
                    "recipient": last_email.get("sender", "Customer"),
                    "subject": last_email.get("subject", "Inquiry"),
                    "body": last_draft,
                }
                yield f"data: {json.dumps(event)}\n\n"

            elif node_name == "skip_unrelated_email":
                event = {
                    "type": "email_skipped",
                    "subject": last_email.get("subject", ""),
                }
                yield f"data: {json.dumps(event)}\n\n"

        await asyncio.sleep(0.05)

    yield f"data: {json.dumps({'type': 'complete'})}\n\n"


@app.get("/api/stream/scan")
async def stream_scan_inbox():
    return StreamingResponse(
        event_stream_generator(is_simulation=False),
        media_type="text/event-stream",
    )


@app.get("/api/stream/simulate")
async def stream_simulate():
    return StreamingResponse(
        event_stream_generator(is_simulation=True),
        media_type="text/event-stream",
    )


def main():
    port = int(os.getenv("PORT", "8000"))
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", port)) == 0:
            port = 8001
    print(f"Starting server on http://localhost:{port}")
    uvicorn.run("deploy_api:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
