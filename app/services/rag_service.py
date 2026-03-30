from __future__ import annotations

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models import SourceEvidence

_model: SentenceTransformer | None = None
_qdrant: QdrantClient | None = None


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


def retrieve_context(question: str, top_k: int = 3) -> list[SourceEvidence]:
    model = _get_model()
    qdrant = _get_qdrant()

    if not qdrant.collection_exists(settings.collection_name):
        return []

    query_vec = model.encode(question).tolist()

    results = qdrant.query_points(
        collection_name=settings.collection_name,
        query=query_vec,
        limit=top_k,
        with_payload=True,
    )

    sources: list[SourceEvidence] = []
    for point in results.points:
        payload = point.payload or {}
        sources.append(
            SourceEvidence(
                id=str(point.id),
                title=f"ChatDoctor row {payload.get('source_row', '?')} chunk {payload.get('chunk_idx', 0)}",
                snippet=str(payload.get("text", "")),
                score=round(point.score, 4),
            )
        )
    return sources
