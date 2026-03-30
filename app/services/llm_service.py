from __future__ import annotations

import logging

from app.config import settings
from app.models import SourceEvidence

logger = logging.getLogger(__name__)

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        if not settings.groq_api_key:
            return None
        from langchain_core.messages import HumanMessage, SystemMessage  # noqa: F401
        from langchain_groq import ChatGroq

        _llm = ChatGroq(
            model=settings.llm_model,
            api_key=settings.groq_api_key,
            temperature=0.3,
        )
    return _llm


SYSTEM_PROMPT = """\
Sen bir klinik bilgilendirme asistanısın. Kuralların:
1. Yalnızca sana verilen kaynaklara (CONTEXT) dayanarak cevap ver.
2. Kaynaklarda bulunmayan bilgiyi UYDURMA.
3. Her cevabın sonunda hangi kaynağa dayandığını belirt.
4. Kesin tanı veya tedavi önerme; "Bu bilgi yalnızca bilgilendirme amaçlıdır" uyarısını ekle.
5. Acil belirti tespit edersen hastayı 112 veya acil servise yönlendir.
6. Cevabını Türkçe ver.
"""


def _fallback_answer(question: str, sources: list[SourceEvidence]) -> tuple[str, float]:
    """Retrieval-only answer when no LLM API key is configured."""
    if not sources:
        return (
            "Bu konuda güvenilir kaynak bulunamadı. "
            "Belirtileriniz devam ederse doktorunuza başvurmanız önemlidir.",
            0.30,
        )

    top = sources[0]
    answer = (
        f"Sorunuza en yakın kaynak bilgisi (skor: {top.score}):\n\n"
        f"{top.snippet}\n\n"
        "Bu bilgi yalnızca bilgilendirme amaçlıdır; kesin tanı için hekim değerlendirmesi gerekir."
    )
    avg_score = sum(s.score for s in sources) / len(sources)
    return answer, round(min(0.95, avg_score * 0.85), 2)


def generate_answer(question: str, sources: list[SourceEvidence]) -> tuple[str, float]:
    """Return (answer_text, confidence_estimate)."""
    if not sources:
        return (
            "Bu konuda güvenilir kaynak bulunamadı. "
            "Belirtileriniz devam ederse doktorunuza başvurmanız önemlidir.",
            0.30,
        )

    llm = _get_llm()
    if llm is None:
        logger.info("GROQ_API_KEY not set, using retrieval-only fallback.")
        return _fallback_answer(question, sources)

    from langchain_core.messages import HumanMessage, SystemMessage

    context_block = "\n\n".join(
        f"[Kaynak {s.id}] (skor: {s.score}): {s.snippet}" for s in sources
    )

    user_content = (
        f"CONTEXT:\n{context_block}\n\n"
        f"SORU: {question}\n\n"
        "Yukarıdaki kaynaklara dayanarak soruyu yanıtla. "
        "Cevabında kaynak ID'lerini referans göster."
    )

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ])

    answer = response.content

    avg_retrieval_score = sum(s.score for s in sources) / len(sources)
    confidence = round(min(0.95, avg_retrieval_score * 0.9), 2)

    return answer, confidence
