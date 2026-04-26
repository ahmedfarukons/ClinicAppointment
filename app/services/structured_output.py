"""
Structured LLM output using Pydantic schema.

Forces the LLM to return JSON conforming to a medical answer schema,
providing structured citations, confidence reasoning, and follow-up questions.
"""

from __future__ import annotations

import json

import structlog
from pydantic import BaseModel, Field

from app.config import settings
from app.models import SourceEvidence

logger = structlog.get_logger(__name__)


class Citation(BaseModel):
    source_id: str
    relevance: str = Field(description="Why this source is relevant")


class MedicalAnswer(BaseModel):
    answer: str = Field(description="The main clinical answer")
    citations: list[Citation] = Field(default_factory=list, description="Sources cited")
    confidence_reasoning: str = Field(default="", description="Why confidence is at this level")
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="Suggested follow-up questions for the patient",
    )


STRUCTURED_PROMPT = """\
You are a clinical information assistant. Answer the patient question based ONLY on the CONTEXT sources below.

Rules:
1. Base your answer strictly on the provided sources.
2. Cite source IDs in your answer.
3. Add a medical disclaimer.
4. Suggest 1-2 follow-up questions the patient might want to ask.

Respond ONLY with valid JSON matching this exact schema (no markdown, no extra text):
{{
  "answer": "Your clinical answer here...",
  "citations": [
    {{"source_id": "ID", "relevance": "Why relevant"}}
  ],
  "confidence_reasoning": "Explain confidence level",
  "follow_up_questions": ["Question 1?", "Question 2?"]
}}

CONTEXT:
{context}

QUESTION: {question}
"""


def generate_structured_answer(
    question: str,
    sources: list[SourceEvidence],
) -> tuple[str, float, MedicalAnswer | None]:
    """Generate a structured medical answer using Pydantic schema.

    Returns:
        Tuple of (answer_text, confidence, structured_answer_or_None).
    """
    if not sources:
        return (
            "No reliable source was found for this topic. "
            "If your symptoms persist, please consult your doctor.",
            0.30,
            None,
        )

    if not settings.gemini_api_key:
        logger.info("structured_output_skipped", reason="no_api_key")
        return _fallback(sources)

    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.2,
        )

        context_block = "\n\n".join(
            f"[Source {s.id}] (score: {s.score}): {s.snippet}" for s in sources
        )

        prompt = STRUCTURED_PROMPT.format(context=context_block, question=question)

        response = llm.invoke([
            SystemMessage(content="You respond only in valid JSON."),
            HumanMessage(content=prompt),
        ])

        content = response.content
        if isinstance(content, list):
            # Extract text from parts if list elements are dicts, else str(part)
            content = "".join([str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content])
        
        raw = content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3].strip()

        structured = MedicalAnswer.model_validate_json(raw)
        avg_score = sum(s.score for s in sources) / len(sources)
        confidence = round(min(0.95, avg_score * 0.9), 2)

        logger.info(
            "structured_output_generated",
            citations=len(structured.citations),
            follow_ups=len(structured.follow_up_questions),
        )
        return structured.answer, confidence, structured

    except (json.JSONDecodeError, Exception):
        logger.exception("structured_output_parse_failed")
        return _fallback(sources)


def _fallback(sources: list[SourceEvidence]) -> tuple[str, float, None]:
    """Fallback when structured generation fails."""
    top = sources[0]
    answer = (
        f"Based on the retrieved source (score: {top.score}):\n\n"
        f"{top.snippet}\n\n"
        "This information is for informational purposes only."
    )
    avg_score = sum(s.score for s in sources) / len(sources)
    return answer, round(min(0.95, avg_score * 0.85), 2), None
