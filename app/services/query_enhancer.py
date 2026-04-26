"""
Query Enhancement: HyDE (Hypothetical Document Embeddings) and query rewriting.

Improves retrieval quality by generating a hypothetical answer first,
then using its embedding to search the vector store.
"""

from __future__ import annotations

import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

_llm = None


def _get_llm():
    global _llm
    if _llm is not None:
        return _llm
    if not settings.gemini_api_key:
        return None
    from langchain_google_genai import ChatGoogleGenerativeAI

    _llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.7,
    )
    return _llm


def rewrite_query(question: str) -> str:
    """Rewrite the user query for better retrieval."""
    llm = _get_llm()
    if llm is None:
        logger.debug("query_rewrite_skipped", reason="no_api_key")
        return question

    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        response = llm.invoke([
            SystemMessage(
                content=(
                    "You are a medical query optimizer. Rewrite the following patient question "
                    "to be more specific and medically precise for searching a clinical knowledge base. "
                    "Keep it concise (1-2 sentences). Return ONLY the rewritten query, nothing else."
                )
            ),
            HumanMessage(content=question),
        ])
        content = response.content
        if isinstance(content, list):
            content = "".join([str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content])
        rewritten = content.strip()
        logger.info("query_rewritten", original=question[:80], rewritten=rewritten[:80])
        return rewritten
    except Exception:
        logger.exception("query_rewrite_failed")
        return question


def generate_hyde_document(question: str) -> str | None:
    """Generate a hypothetical document (HyDE) to improve embedding search.

    Returns a hypothetical answer that can be embedded alongside the original
    query for better semantic matching.
    """
    llm = _get_llm()
    if llm is None:
        return None

    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        response = llm.invoke([
            SystemMessage(
                content=(
                    "You are a clinical knowledge base. Given a patient question, write a short "
                    "(2-3 sentence) hypothetical doctor answer that would be found in a medical "
                    "reference. Be factual and concise. Return ONLY the answer text."
                )
            ),
            HumanMessage(content=question),
        ])
        content = response.content
        if isinstance(content, list):
            content = "".join([str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content])
        hyde_doc = content.strip()
        logger.info("hyde_generated", question=question[:60], hyde_length=len(hyde_doc))
        return hyde_doc
    except Exception:
        logger.exception("hyde_generation_failed")
        return None
