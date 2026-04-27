"""
Multi-source retrieval service.

Searches across multiple Qdrant collections (chatdoctor, guidelines, drugs)
and merges results with source-type tagging.
"""

from __future__ import annotations

import structlog
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models import SourceEvidence

logger = structlog.get_logger(__name__)

_model: SentenceTransformer | None = None
_qdrant: QdrantClient | None = None

# Collection definitions: (collection_name, source_type_label)
COLLECTIONS = [
    (settings.collection_name, "chatdoctor"),
    ("clinical_guidelines", "guideline"),
    ("drug_information", "drug"),
]


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def _get_qdrant() -> QdrantClient:
    global _qdrant
    if _qdrant is None:
        _qdrant = QdrantClient(path=settings.qdrant_path)
    return _qdrant


def multi_retrieve(
    question: str,
    query_embedding: list[float] | None = None,
    top_k_per_source: int = 5,
) -> list[SourceEvidence]:
    """Retrieve from all available collections and merge results.

    Args:
        question: The user's query (used to generate embedding if none provided).
        query_embedding: Pre-computed embedding vector (e.g. from HyDE).
        top_k_per_source: How many results to fetch per collection.

    Returns:
        Combined list of SourceEvidence from all available collections.
    """
    model = _get_model()
    qdrant = _get_qdrant()

    if query_embedding is None:
        query_embedding = model.encode(question).tolist()

    all_sources: list[SourceEvidence] = []

    for collection_name, source_type in COLLECTIONS:
        try:
            if not qdrant.collection_exists(collection_name):
                logger.debug("collection_not_found", collection=collection_name)
                continue

            results = qdrant.query_points(
                collection_name=collection_name,
                query=query_embedding,
                limit=top_k_per_source,
                with_payload=True,
            )

            for point in results.points:
                payload = point.payload or {}
                all_sources.append(
                    SourceEvidence(
                        id=f"{source_type}:{point.id}",
                        title=payload.get("title", f"{source_type} row {payload.get('source_row', '?')}"),
                        snippet=str(payload.get("text", "")),
                        score=round(point.score, 4),
                        source_type=source_type,
                    )
                )

            logger.info(
                "collection_searched",
                collection=collection_name,
                results=len(results.points),
            )
        except Exception:
            logger.exception("collection_search_failed", collection=collection_name)

    # Sort all results by score descending
    all_sources.sort(key=lambda s: s.score, reverse=True)
    logger.info("multi_retrieve_completed", total_sources=len(all_sources))
    return all_sources
