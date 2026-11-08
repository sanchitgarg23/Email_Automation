import os
import sys
from colorama import Fore, Style
from dotenv import load_dotenv

load_dotenv()

# Sample incoming customer emails
SAMPLE_EMAILS = [
    {
        "id": "msg_001",
        "threadId": "t_001",
        "messageId": "m_001",
        "references": "",
        "sender": "sarah.connor@example.com",
        "subject": "Inquiry about Agency Pricing and Services",
        "body": "Hello, I am interested in your web development and digital marketing services. Could you please share your pricing packages and onboarding process? Thanks!"
    },
    {
        "id": "msg_002",
        "threadId": "t_002",
        "messageId": "m_002",
        "references": "",
        "sender": "john.doe@example.com",
        "subject": "Delay in Project Delivery - Urgent",
        "body": "Hi Support, our project delivery was promised by last Friday, but we have not received any updates or deliverable files yet. This is affecting our timeline."
    },
    {
        "id": "msg_003",
        "threadId": "t_003",
        "messageId": "m_003",
        "references": "",
        "sender": "marketing@crypto-deals.xyz",
        "subject": "Claim your $500 bonus now!",
        "body": "Congratulations! You have been selected to win a $500 crypto bonus. Click here to claim your reward."
    }
]

class MockGmailTools:
    """Simulates Gmail operations without requiring Google Cloud OAuth credentials."""
    def __init__(self):
        self._emails = list(SAMPLE_EMAILS)

    def fetch_unanswered_emails(self, max_results=50):
        emails_to_return = list(self._emails)
        self._emails = []
        return emails_to_return

    def create_draft_reply(self, initial_email, reply_text):
        print(Fore.GREEN + f"\n[Mock Gmail] Draft reply created for {initial_email.sender}:" + Style.RESET_ALL)
        print(f" Subject: Re: {initial_email.subject}")
        print(f"--- DRAFT CONTENT ---\n{reply_text}\n---------------------\n")
        return {"id": "mock_draft_123"}

    def send_reply(self, initial_email, reply_text):
        print(Fore.GREEN + f"[Mock Gmail] Email sent to {initial_email.sender}!" + Style.RESET_ALL)
        return {"id": "mock_sent_123"}


def run_simulation():
    print(Fore.CYAN + "=" * 65)
    print("  CUSTOMER SUPPORT EMAIL AUTOMATION - LIVE AI SIMULATION RUN")
    print("=" * 65 + Style.RESET_ALL)

    # Patch Gmail tools so credentials.json is not required for simulation
    import src.nodes
    src.nodes.GmailToolsClass = MockGmailTools

    groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    print(Fore.GREEN + f"[INFO] Running with REAL LLM ({groq_model}) and local embeddings on Chroma DB!\n" + Style.RESET_ALL)

    from src.graph import Workflow
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
            "body": ""
        },
        "email_category": "",
        "generated_email": "",
        "rag_queries": [],
        "retrieved_documents": "",
        "writer_messages": [],
        "sendable": False,
        "trials": 0
    }

    config = {"recursion_limit": 100}
    print(Fore.GREEN + "Starting workflow stream...\n" + Style.RESET_ALL)
    for output in app.stream(initial_state, config):
        for key, value in output.items():
            print(Fore.CYAN + f">> Finished Node: {key}\n" + Style.RESET_ALL)

    print(Fore.GREEN + "=" * 65)
    print("  SIMULATION WORKFLOW COMPLETED SUCCESSFULLY!")
    print("=" * 65 + Style.RESET_ALL)

if __name__ == "__main__":
    run_simulation()
