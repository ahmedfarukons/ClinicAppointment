from fastapi import FastAPI

from app.models import ChatRequest, ChatResponse
from app.services.orchestrator import run_pipeline

app = FastAPI(
    title="ChatDoctor Clinical Assistant",
    description="Intent Router + RAG + Appointment Agent + XAI",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return run_pipeline(payload.message)
