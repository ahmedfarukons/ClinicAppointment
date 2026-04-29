from __future__ import annotations

import re
from typing import Optional

from app.models import SourceEvidence
from app.services.clinic_knowledge import (
    DEPARTMENT_QUESTIONS,
    KEYWORD_MAP,
    TRIAGE_CONTEXT,
)

DATE_REGEX = re.compile(r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b")
RELATIVE_DAYS = {
    "bugün": 0, "yarın": 1, "today": 0, "tomorrow": 1,
    "monday": None, "tuesday": None, "wednesday": None,
    "thursday": None, "friday": None, "saturday": None, "sunday": None,
}

DEPARTMENTS = {"Internal Medicine", "Cardiology", "Dermatology", "Laboratory"}

DEPT_TR = {
    "Internal Medicine": "Dahiliye",
    "Cardiology": "Kardiyoloji",
    "Dermatology": "Dermatoloji",
    "Laboratory": "Laboratuvar",
}


def _extract_date(message: str) -> Optional[str]:
    match = DATE_REGEX.search(message)
    if match:
        return match.group(1)
    text = message.lower()
    for word in RELATIVE_DAYS:
        if re.search(rf"\b{word}\b", text):
            return word
    return None


def _extract_department_fast(message: str) -> Optional[str]:
    """
    Fast two-stage matching:
    1. KEYWORD_MAP: multi-word phrases are checked first.
    2. DEPARTMENT_QUESTIONS: token similarity with sample patient questions.
    """
    text = message.lower().strip()

    # 1. Keyword map (longer phrases first)
    sorted_keywords = sorted(KEYWORD_MAP.keys(), key=len, reverse=True)
    for kw in sorted_keywords:
        if kw in text:
            return KEYWORD_MAP[kw]

    # 2. Token similarity with sample questions
    text_tokens = set(re.findall(r"\w+", text))
    best_dept = None
    best_score = 0.0
    for dept, questions in DEPARTMENT_QUESTIONS.items():
        for q in questions:
            q_tokens = set(re.findall(r"\w+", q.lower()))
            if not q_tokens:
                continue
            common = text_tokens & q_tokens
            score = len(common) / len(q_tokens)
            if score > best_score and score >= 0.35:
                best_score = score
                best_dept = dept
    return best_dept


def _extract_department(message: str) -> str:
    """Detect the department and always return a result."""
    # Fast rule-based match first
    fast = _extract_department_fast(message)
    if fast:
        return fast

    # LLM fallback
    from app.services.llm_service import _get_llm
    llm = _get_llm()
    if llm is None:
        return "Internal Medicine"

    deps = list(DEPARTMENTS)
    from langchain_core.messages import HumanMessage
    prompt = f"""{TRIAGE_CONTEXT}

Patient message: "{message}"

Choose the most appropriate department based on the guide above.
Write only one of these 4 names and nothing else:
Internal Medicine | Cardiology | Dermatology | Laboratory"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        out = response.content.strip()
        for d in deps:
            if d.lower() == out.lower():
                return d
        for d in deps:
            if d.lower() in out.lower() or out.lower() in d.lower():
                return d
    except Exception as e:
        import structlog
        structlog.get_logger(__name__).error("llm_dept_extract_failed", error=str(e))

    return "Internal Medicine"


def handle_appointment(
    message: str,
) -> tuple[str, list[SourceEvidence], float, str, Optional[str]]:
    department = _extract_department(message)
    department_label = f"{DEPT_TR.get(department, department)} ({department})"

    answer = (
        f"Based on the symptoms you described, I recommend the **{department_label}** department. "
        "Click the button below to continue to the appointment page, where you can choose a suitable doctor and time."
    )
    return (
        answer,
        [
            SourceEvidence(
                id="triage-engine",
                title="Clinical Triage Engine",
                snippet=f"Detected department: {department}. Redirecting to the appointment page.",
                score=0.98,
            )
        ],
        0.95,
        "Department detected; redirecting to the appointment form.",
        department,
    )
