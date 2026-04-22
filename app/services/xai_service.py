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
        RED_FLAG_PHRASES,
        _normalize,
    )

    text = _normalize(message)
    tokens = text.split()
    contributions: dict[str, float] = {}

    for phrase in RED_FLAG_PHRASES:
        if phrase in text:
            contributions[f"red_flag_signal:{phrase}"] = 1.0

    for kw in APPOINTMENT_KEYWORDS:
        if kw in tokens:
            contributions[f"appointment_signal:{kw}"] = 1.0

    total = len(tokens) if tokens else 1
    for token in set(tokens):
        is_appointment = token in APPOINTMENT_KEYWORDS
        is_red_flag = any(token in flag.split() for flag in RED_FLAG_PHRASES)
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
        "This system is for informational purposes only and does not replace "
        "a physician's examination. In emergencies, go to the nearest emergency "
        "room or call 911."
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
