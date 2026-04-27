"""
Cross-encoder re-ranking service.

After initial bi-encoder retrieval, re-ranks candidates using a
cross-encoder model for higher precision.
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)

_cross_encoder = None


def _get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        try:
            from sentence_transformers import CrossEncoder

            _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("cross_encoder_loaded", model="ms-marco-MiniLM-L-6-v2")
        except Exception:
            logger.exception("cross_encoder_load_failed")
            return None
    return _cross_encoder


def rerank(question: str, sources: list, top_k: int = 3) -> list:
    """Re-rank SourceEvidence list using cross-encoder scores.

    Args:
        question: The original user query.
        sources: List of SourceEvidence objects from initial retrieval.
        top_k: Number of top results to return after re-ranking.

    Returns:
        Re-ranked list of SourceEvidence (top_k items).
    """
    if not sources or len(sources) <= 1:
        return sources

    encoder = _get_cross_encoder()
    if encoder is None:
        logger.warning("rerank_skipped", reason="no_cross_encoder")
        return sources[:top_k]

    try:
        pairs = [(question, s.snippet) for s in sources]
        scores = encoder.predict(pairs)

        scored = list(zip(sources, scores))
        scored.sort(key=lambda x: x[1], reverse=True)

        reranked = []
        for source, new_score in scored[:top_k]:
            # Update score with cross-encoder score (normalized to 0-1)
            source.score = round(float(new_score), 4)
            reranked.append(source)

        logger.info(
            "rerank_completed",
            input_count=len(sources),
            output_count=len(reranked),
            top_score=reranked[0].score if reranked else None,
        )
        return reranked
    except Exception:
        logger.exception("rerank_failed")
        return sources[:top_k]
