"""
Structured LLM output using Pydantic schema.
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
You are a clinical information assistant. The patient asked a question or described symptoms.

Rules:
1. If CONTEXT sources are provided, use them and include source IDs.
2. If the provided sources are limited or missing, answer accurately using your medical knowledge.
3. Always include this warning: "This information is for general guidance only and does not replace professional medical diagnosis."
4. End your response with 1-2 suggested follow-up questions for the patient.
5. IMPORTANT: Always respond in English.
6. CONTEXT may contain non-English text. Translate and summarize it in English; never copy non-English source text into the answer.
7. Keep the response high-quality, warm, and professional.

CONTEXT:
{context}

QUESTION/SYMPTOM: {question}

Respond in the following JSON schema (no markdown, JSON only):
{{
  "answer": "Your clinical response in English...",
  "citations": [
    {{"source_id": "ID", "relevance": "Why this source is relevant"}}
  ],
  "confidence_reasoning": "Why confidence is at this level",
  "follow_up_questions": ["Follow-up question 1?", "Follow-up question 2?"]
}}
"""


def _contains_turkish(text: str) -> bool:
    lowered = text.lower()
    if any(char in lowered for char in "çğıöşü"):
        return True
    turkish_markers = {
        "baş", "ağrı", "ağrıyor", "doktor", "randevu", "şikayet",
        "belirti", "tedavi", "muayene", "hastalık", "göğüs", "nefes",
        "bulantı", "başvuru", "sağlık", "acil", "önerilir",
    }
    words = set(lowered.replace(".", " ").replace(",", " ").split())
    return bool(words & turkish_markers)


def generate_structured_answer(
    question: str,
    sources: list[SourceEvidence],
) -> tuple[str, float, MedicalAnswer | None]:
    """Generate a structured medical answer. Falls back to LLM knowledge if no sources."""

    if not settings.gemini_api_key:
        logger.info("structured_output_skipped", reason="no_api_key")
        return _fallback(sources, question)

    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.3,
        )

        if sources:
            context_block = "\n\n".join(
                f"[Source {s.id}] (score: {s.score}): {s.snippet}" for s in sources
            )
        else:
            context_block = "No dedicated source was found in the clinical database for this query. Use your medical knowledge."

        prompt = STRUCTURED_PROMPT.format(context=context_block, question=question)

        response = llm.invoke([
            SystemMessage(content="You are an English clinical assistant. Return valid JSON only. All string values must be in English, never Turkish."),
            HumanMessage(content=prompt),
        ])

        content = response.content
        if isinstance(content, list):
            content = "".join([str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content])
        
        raw = content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3].strip()

        structured = MedicalAnswer.model_validate_json(raw)
        combined_text = " ".join(
            [
                structured.answer,
                structured.confidence_reasoning,
                " ".join(structured.follow_up_questions),
                " ".join(c.relevance for c in structured.citations),
            ]
        )
        if _contains_turkish(combined_text):
            logger.warning("structured_output_non_english_detected")
            return _fallback(sources, question)

        avg_score = sum(s.score for s in sources) / len(sources) if sources else 0.75
        confidence = round(min(0.95, avg_score * 0.9), 2) if sources else 0.75

        logger.info(
            "structured_output_generated",
            citations=len(structured.citations),
            follow_ups=len(structured.follow_up_questions),
        )
        return structured.answer, confidence, structured

    except (json.JSONDecodeError, Exception):
        logger.exception("structured_output_parse_failed")
        return _fallback(sources, question)


def _fallback(sources: list[SourceEvidence], question: str = "") -> tuple[str, float, None]:
    """Fallback when structured generation fails."""
    if sources:
        top = sources[0]
        answer = (
            f"I found relevant clinical evidence for your concern from {top.title} "
            f"(source {top.id}, score: {top.score}). Please share how long the symptom has been present, "
            "how severe it is, and whether you have warning signs such as chest pain, shortness of breath, "
            "fainting, weakness, confusion, severe vomiting, or a sudden severe headache.\n\n"
            "This information is for general guidance only and does not replace professional medical diagnosis."
        )
        avg_score = sum(s.score for s in sources) / len(sources)
        return answer, round(min(0.95, avg_score * 0.85), 2), None
    else:
        answer = (
            "I received your concern. A direct clinical examination by one of our specialists will provide the most accurate outcome. "
            "You can continue by booking an appointment with the relevant department."
        )
        return answer, 0.60, None

