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
Sen bir klinik bilgi asistanısın. Hastan sana soru sordu ya da şikayetini aktardı.

Kurallar:
1. Eğer sağlanan CONTEXT (bağlam) kaynakları mevcutsa onları kullan ve kaynak ID'lerini belirt.
2. Eğer sağlanan kaynaklar yetersiz veya yoksa, kendi tıbbi bilginle ayrıntılı ve doğru bir yanıt ver.
3. Her zaman şu uyarıyı ekle: "Bu bilgi yalnızca genel bilgilendirme amaçlıdır; kesin tanı için mutlaka bir uzmana başvurun."
4. Cevabının sonunda hastaya 1-2 takip sorusu öner.
5. ÖNEMLI: Yanıtını MUTLAKA Türkçe ver (kullanıcı başka bir dilde yazdıysa da).
6. Yanıt kaliteli, sıcak ve profesyonel olsun.

CONTEXT:
{context}

SORU/ŞİKAYET: {question}

Aşağıdaki JSON şemasıyla yanıt ver (markdown yok, sadece JSON):
{{
  "answer": "Türkçe klinik yanıtın burada...",
  "citations": [
    {{"source_id": "ID", "relevance": "Neden ilgili"}}
  ],
  "confidence_reasoning": "Güven düzeyi açıklaması",
  "follow_up_questions": ["Soru 1?", "Soru 2?"]
}}
"""


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
                f"[Kaynak {s.id}] (skor: {s.score}): {s.snippet}" for s in sources
            )
        else:
            context_block = "Klinik veritabanında bu konu için özel kaynak bulunamadı. Kendi tıbbi bilginle yanıt ver."

        prompt = STRUCTURED_PROMPT.format(context=context_block, question=question)

        response = llm.invoke([
            SystemMessage(content="Sen bir Türkçe tıbbi asistansın. Sadece geçerli JSON döndür."),
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
            f"Aldığımız bilgilere göre (skor: {top.score}):\n\n"
            f"{top.snippet}\n\n"
            "Bu bilgi yalnızca genel bilgilendirme amaçlıdır; kesin tanı için mutlaka bir uzmana başvurun."
        )
        avg_score = sum(s.score for s in sources) / len(sources)
        return answer, round(min(0.95, avg_score * 0.85), 2), None
    else:
        answer = (
            "Şikayetinizi aldım. Kliniğimizdeki uzmanlardan birinin sizi muayene etmesi en doğru sonucu verecektir. "
            "Aşağıdaki butona tıklayarak ilgili bölümden randevu alabilirsiniz."
        )
        return answer, 0.60, None

