from __future__ import annotations

import re

from app.models import DecisionStep, RouteType


def _normalize(text: str) -> str:
    """Lowercase and strip punctuation for robust matching."""
    text = text.lower()
    text = re.sub(r"[^\w\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _tokens(text: str) -> set[str]:
    return set(_normalize(text).split())


APPOINTMENT_KEYWORDS = {
    "appointment",
    "schedule",
    "book",
    "booking",
    "reserve",
    "visit",
    "consultation",
    "doctor",
    "physician",
    "clinic",
    "department",
}

# Multi-word red-flag phrases (substring match on normalized text).
RED_FLAG_PHRASES = {
    "chest pain",
    "cant breathe",
    "can not breathe",
    "cannot breathe",
    "shortness of breath",
    "difficulty breathing",
    "trouble breathing",
    "losing consciousness",
    "loss of consciousness",
    "unconscious",
    "heavy bleeding",
    "severe bleeding",
    "suicidal",
    "suicide",
    "kill myself",
    "heart attack",
    "stroke",
    "severe headache",
    "numbness in arm",
    "slurred speech",
}

# Co-occurrence rules: if ALL tokens in the tuple are present, count as red flag.
RED_FLAG_COOCCUR = [
    ("pain", "chest"),
    ("pain", "heart"),
    ("breathe", "cannot"),
    ("breath", "short"),
    ("bleeding", "severe"),
    ("bleeding", "heavy"),
]


def _detect_red_flags(normalized_text: str, tokens: set[str]) -> list[str]:
    matches: list[str] = []
    for phrase in RED_FLAG_PHRASES:
        if phrase in normalized_text:
            matches.append(phrase)
    for combo in RED_FLAG_COOCCUR:
        if all(tok in tokens for tok in combo):
            matches.append("+".join(combo))
    return sorted(set(matches))


def classify_intent(
    message: str,
) -> tuple[RouteType, float, str, list[DecisionStep]]:
    normalized = _normalize(message)
    tokens = set(normalized.split())
    steps: list[DecisionStep] = []

    matched_red = _detect_red_flags(normalized, tokens)
    if matched_red:
        steps.append(
            DecisionStep(
                step="red_flag_check",
                outcome="triggered",
                detail=f"Matched red flags: {matched_red}",
            )
        )
        return (
            "escalation",
            0.95,
            "High-risk symptom keywords were detected in the message.",
            steps,
        )

    steps.append(
        DecisionStep(
            step="red_flag_check",
            outcome="clear",
            detail="No red-flag phrase was found.",
        )
    )

    matched_appt = sorted(tokens & APPOINTMENT_KEYWORDS)
    if matched_appt:
        steps.append(
            DecisionStep(
                step="appointment_keyword_check",
                outcome="triggered",
                detail=f"Matched appointment signals: {matched_appt}",
            )
        )
        return (
            "appointment_request",
            0.86,
            "Appointment-related intent signals were found in the message.",
            steps,
        )

    steps.append(
        DecisionStep(
            step="appointment_keyword_check",
            outcome="clear",
            detail="No appointment signal found.",
        )
    )
    steps.append(
        DecisionStep(
            step="default_route",
            outcome="medical_info",
            detail="Message classified as an informational/medical request.",
        )
    )

    return (
        "medical_info",
        0.80,
        "Message classified as an informational/medical-information request.",
        steps,
    )
