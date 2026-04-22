from __future__ import annotations

import logging

from app.config import settings
from app.models import SourceEvidence

logger = logging.getLogger(__name__)

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        if not settings.gemini_api_key:
            return None
        from langchain_google_genai import ChatGoogleGenerativeAI

        _llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.3,
        )
    return _llm


SYSTEM_PROMPT = """\
You are a clinical information assistant. Your rules:
1. Answer ONLY based on the sources (CONTEXT) provided to you.
2. DO NOT fabricate information that is not in the sources.
3. At the end of each answer, cite which source(s) you relied on.
4. Do not give a definitive diagnosis or treatment; always add the disclaimer: "This information is for informational purposes only."
5. If you detect emergency symptoms, direct the patient to 911 or the nearest emergency room.
6. Answer in English.
"""


def _fallback_answer(question: str, sources: list[SourceEvidence]) -> tuple[str, float]:
    """Retrieval-only answer when no LLM API key is configured."""
    if not sources:
        return (
            "No reliable source was found for this topic. "
            "If your symptoms persist, it is important to consult your doctor.",
            0.30,
        )

    top = sources[0]
    answer = (
        f"Closest source information for your question (score: {top.score}):\n\n"
        f"{top.snippet}\n\n"
        "This information is for informational purposes only; "
        "a definitive diagnosis requires physician evaluation."
    )
    avg_score = sum(s.score for s in sources) / len(sources)
    return answer, round(min(0.95, avg_score * 0.85), 2)


def generate_answer(question: str, sources: list[SourceEvidence]) -> tuple[str, float]:
    """Return (answer_text, confidence_estimate)."""
    if not sources:
        return (
            "No reliable source was found for this topic. "
            "If your symptoms persist, it is important to consult your doctor.",
            0.30,
        )

    llm = _get_llm()
    if llm is None:
        logger.info("GEMINI_API_KEY not set, using retrieval-only fallback.")
        return _fallback_answer(question, sources)

    from langchain_core.messages import HumanMessage, SystemMessage

    context_block = "\n\n".join(
        f"[Source {s.id}] (score: {s.score}): {s.snippet}" for s in sources
    )

    user_content = (
        f"CONTEXT:\n{context_block}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer the question based on the sources above. "
        "Reference the source IDs in your answer."
    )

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ])

    answer = response.content

    avg_retrieval_score = sum(s.score for s in sources) / len(sources)
    confidence = round(min(0.95, avg_retrieval_score * 0.9), 2)

    return answer, confidence
