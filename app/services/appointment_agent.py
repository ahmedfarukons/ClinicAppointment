from __future__ import annotations

import re
from typing import Optional

from app.models import SourceEvidence


DATE_REGEX = re.compile(r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b")
RELATIVE_DAYS = {
    "today": 0,
    "tomorrow": 1,
    "monday": None,
    "tuesday": None,
    "wednesday": None,
    "thursday": None,
    "friday": None,
    "saturday": None,
    "sunday": None,
}
DEPARTMENTS = {
    "cardiology",
    "internal medicine",
    "dermatology",
    "neurology",
    "pediatrics",
    "orthopedics",
    "ent",
    "ophthalmology",
    "psychiatry",
    "gynecology",
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


def _extract_department(message: str) -> Optional[str]:
    text = message.lower()
    for dep in DEPARTMENTS:
        pattern = r"\b" + re.escape(dep) + r"\b"
        if re.search(pattern, text):
            return dep
    return None


def handle_appointment(
    message: str,
) -> tuple[str, list[SourceEvidence], float, str]:
    date = _extract_date(message)
    department = _extract_department(message)

    missing_slots = []
    if not department:
        missing_slots.append("department")
    if not date:
        missing_slots.append("date")

    if missing_slots:
        ask = ", ".join(missing_slots)
        return (
            f"To book an appointment I still need the following: {ask}. "
            "Could you please provide this information?",
            [],
            0.74,
            "Slot-filling step: required fields are missing.",
        )

    # PoC-level mock availability.
    answer = (
        f"For {department.title()} on {date}, 10:30 and 14:00 appear to be available. "
        "If you choose one of these times, I can finalize your appointment request."
    )
    return (
        answer,
        [
            SourceEvidence(
                id="appointment-availability-mock",
                title="Appointment Availability Engine (Mock)",
                snippet=f"{department.title()} - {date} example open slots: 10:30, 14:00",
                score=0.91,
            )
        ],
        0.88,
        "Department and date fields were detected; availability lookup initiated.",
    )
