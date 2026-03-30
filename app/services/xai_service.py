from __future__ import annotations

from app.models import DecisionStep, RouteType, SourceEvidence, XAIExplanation


def _compute_retrieval_quality(sources: list[SourceEvidence]) -> dict[str, float] | None:
    if not sources:
        return None
    scores = [s.score for s in sources]
    return {
        "avg_score": round(sum(scores) / len(scores), 4),
        "max_score": round(max(scores), 4),
        "min_score": round(min(scores), 4),
        "source_count": float(len(scores)),
    }


def _compute_feature_contributions(
    message: str,
    route: RouteType,
) -> dict[str, float]:
    from app.services.intent_classifier import (
        APPOINTMENT_KEYWORDS,
        RED_FLAG_KEYWORDS,
        _normalize,
    )

    text = _normalize(message)
    contributions: dict[str, float] = {}

    keyword_sets: dict[str, set[str]] = {
        "appointment_signal": APPOINTMENT_KEYWORDS,
        "red_flag_signal": RED_FLAG_KEYWORDS,
    }

    for label, kw_set in keyword_sets.items():
        for kw in kw_set:
            if kw in text:
                contributions[f"{label}:{kw}"] = 1.0

    tokens = text.split()
    total = len(tokens) if tokens else 1
    for token in set(tokens):
        is_appointment = token in APPOINTMENT_KEYWORDS
        is_red_flag = any(token in flag for flag in RED_FLAG_KEYWORDS)
        if is_appointment or is_red_flag:
            contributions[f"token_weight:{token}"] = round(1.0 / total, 4)

    return contributions


def build_explanation(
    route: RouteType,
    confidence: float,
    rationale: str,
    sources: list[SourceEvidence],
    decision_path: list[DecisionStep] | None = None,
    message: str = "",
) -> XAIExplanation:
    safety_note = (
        "Bu sistem bilgilendirme amaçlıdır, doktor muayenesinin yerine geçmez. "
        "Acil durumlarda en yakın acil servise başvurun veya 112'yi arayın."
    )

    retrieval_quality = _compute_retrieval_quality(sources)
    feature_contributions = _compute_feature_contributions(message, route)

    if decision_path is None:
        decision_path = []

    return XAIExplanation(
        route=route,
        confidence=round(confidence, 2),
        rationale=rationale,
        decision_path=decision_path,
        feature_contributions=feature_contributions,
        sources=sources,
        retrieval_quality=retrieval_quality,
        safety_note=safety_note,
    )
