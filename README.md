# 🚀 Customer Support Email Automation with AI Agents and RAG

An autonomous, multi-agent AI customer support email assistant built with **LangChain**, **LangGraph**, **ChromaDB**, and the **Gmail API**.

The system automatically monitors an incoming Gmail inbox, categorizes emails, performs Retrieval-Augmented Generation (RAG) against company knowledge, writes tailored draft replies, and verifies quality before creating drafts directly inside Gmail.

---

## 🌟 Key Features

* **Real-time Gmail Monitoring**: Continuously fetches new, unanswered email threads within an 8-hour window.
* **Intelligent Email Categorization**: Classifies incoming emails into `product_enquiry`, `customer_complaint`, `customer_feedback`, or `unrelated`.
* **Safe Spam & Marketing Filtering**: Automatically filters out promotional newsletters, social notifications, and bot emails without sending unintended replies.
* **Semantic Search (RAG)**: Uses **on-device local vector embeddings** (`all-MiniLM-L6-v2` via ONNX/ChromaDB) to accurately answer product, service, and pricing questions.
* **AI Draft Generation & QA Proofreading**: Drafts professional responses and runs automated quality and tone checks before approval.
* **Interactive Live Web Dashboard**: Built-in FastAPI dashboard featuring real-time Server-Sent Events (SSE) streaming, pipeline stepper visualization, and generated draft previews.

---

## 🛠️ Architecture & Tech Stack

* **Workflow Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph) (StateGraph with conditional edge routing)
* **LLM Engine**: [Groq](https://groq.com/) (using high-speed open models like `openai/gpt-oss-120b`)
* **Vector Store & Embeddings**: [ChromaDB](https://www.trychroma.com/) with free, on-device local ONNX embeddings
* **Email Service**: Google Gmail API (OAuth 2.0 Desktop Flow)
* **Web Server & Dashboard**: [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), Tailwind CSS, Lucide Icons

---

## 🚀 Quickstart Guide

### 1. Prerequisites
* Python 3.11+
* Groq API Key (available free at [console.groq.com](https://console.groq.com))
* Google Cloud OAuth 2.0 Desktop Credentials (`credentials.json`) with Gmail API enabled

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd langgraph-email-automation

# Create virtual environment and activate
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the project root (see `.env.example`):

```env
MY_EMAIL=sanchitgarg23april@gmail.com
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

Place your Google Cloud OAuth client secret JSON in the project root as `credentials.json`.

---

## 🖥️ Running the Application

### Option A: Interactive Web Dashboard (Recommended)
Run the real-time web interface with live streaming activity logs:
```bash
source .venv/bin/activate
python deploy_api.py
```
* **Dashboard**: [http://localhost:8001](http://localhost:8001)
* **LangServe Playground**: [http://localhost:8001/playground](http://localhost:8001/playground)
* **Swagger API Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)

### Option B: Terminal Inbox Automation Worker
Run a single scan and response cycle directly in the console:
```bash
source .venv/bin/activate
python main.py
```

### Option C: Offline Simulation Mode
Test the LangGraph multi-agent flow locally with mock emails (no Gmail connection required):
```bash
source .venv/bin/activate
python simulate_run.py
```

---

## 📚 Customizing Knowledge Base (RAG)

To update the agency knowledge base:
1. Edit or replace [`data/agency.txt`](data/agency.txt) with your product, pricing, and FAQ documentation.
2. Re-index your local vector store:
```bash
python create_index.py
```

---

## 👤 Maintainer

* **Sanchit Garg** ([sanchitgarg23april@gmail.com](mailto:sanchitgarg23april@gmail.com))
