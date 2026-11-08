import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AppConfig:
    """Central configuration for SG AI Email Automation."""
    my_email: str = os.getenv("MY_EMAIL", "sanchitgarg23april@gmail.com")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    agency_name: str = os.getenv("AGENCY_NAME", "SG AI Automation")
    auto_send: bool = os.getenv("AUTO_SEND", "false").lower() in ("true", "1", "yes")
    poll_interval: int = int(os.getenv("POLL_INTERVAL_SECONDS", "120"))
    max_trials: int = int(os.getenv("MAX_TRIALS", "3"))
    rag_k: int = int(os.getenv("RAG_K", "3"))
    temperature: float = float(os.getenv("MODEL_TEMPERATURE", "0.1"))


settings = AppConfig()

