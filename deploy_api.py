import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from src.graph import Workflow
from src.config import settings
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="SG AI Email Automation API",
    version="1.0",
    description="LangGraph multi-agent backend API for AI Gmail automation",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_runnable():
    return Workflow().app


try:
    runnable = get_runnable()
    add_routes(app, runnable)
except Exception as e:
    print(f"[Warning] Could not initialize LangServe runnable: {e}")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SG AI Email Automation API",
        "groq_model": settings.groq_model,
        "my_email": settings.my_email,
        "agency": settings.agency_name,
    }


def main():
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
