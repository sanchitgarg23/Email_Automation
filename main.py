import os
import sys
import time
from colorama import Fore, Style
from src.graph import Workflow
from src.config import settings

# LangGraph config 
config = {"recursion_limit": 100}

workflow = Workflow()
app = workflow.app


def print_help():
    print("""
SG AI Email Automation CLI
Usage:
  python main.py             Run a single scan over recent unanswered emails
  python main.py --watch     Run continuous inbox monitoring (polls every interval)
  python main.py --simulate  Run simulation mode with mock test emails
  python main.py --help      Show this help message
""")


def run_inbox_cycle():
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

    print(Fore.GREEN + f"[{time.strftime('%X')}] Scanning Gmail inbox ({settings.my_email})..." + Style.RESET_ALL)
    for output in app.stream(initial_state, config):
        for key, value in output.items():
            print(Fore.CYAN + f"Finished running: {key}:" + Style.RESET_ALL)


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        return

    if "--simulate" in sys.argv or "-s" in sys.argv:
        import simulate_run
        simulate_run.run_simulation()
        return

    watch_mode = "--watch" in sys.argv or "-w" in sys.argv
    if watch_mode:
        interval = settings.poll_interval
        print(Fore.GREEN + f"Starting continuous monitoring (polling every {interval}s). Press Ctrl+C to stop." + Style.RESET_ALL)
        try:
            while True:
                run_inbox_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nMonitoring stopped by user." + Style.RESET_ALL)
    else:
        run_inbox_cycle()


if __name__ == "__main__":
    main()
