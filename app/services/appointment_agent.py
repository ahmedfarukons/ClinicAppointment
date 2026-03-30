import re
from typing import Optional

from app.models import SourceEvidence


def _extract_date(message: str) -> Optional[str]:
    match = re.search(r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b", message)
    if match:
        return match.group(1)
    return None


def _extract_department(message: str) -> Optional[str]:
    departments = ["kardiyoloji", "dahiliye", "dermatoloji", "nöroloji", "noroloji"]
    text = message.lower()
    for dep in departments:
        if dep in text:
            return "nöroloji" if dep == "noroloji" else dep
    return None


def handle_appointment(message: str) -> tuple[str, list[SourceEvidence], float, str]:
    date = _extract_date(message)
    department = _extract_department(message)

    missing_slots = []
    if not department:
        missing_slots.append("bölüm")
    if not date:
        missing_slots.append("tarih")

    if missing_slots:
        ask = ", ".join(missing_slots)
        return (
            f"Randevu oluşturabilmem için şu bilgi(ler) eksik: {ask}. Lütfen bu bilgileri paylaşır mısınız?",
            [],
            0.74,
            "Slot-filling adımında zorunlu alanlar eksik bulundu.",
        )

    # PoC amaçlı sabit slot simülasyonu.
    answer = (
        f"{department.title()} için {date} tarihinde 10:30 ve 14:00 saatleri uygun görünüyor. "
        "Uygun olan saati seçerseniz randevu talebinizi tamamlayabilirim."
    )
    return (
        answer,
        [
            SourceEvidence(
                id="appointment-availability-mock",
                title="Randevu Uygunluk Motoru (Mock)",
                snippet=f"{department.title()} - {date} için örnek uygun slotlar: 10:30, 14:00",
                score=0.91,
            )
        ],
        0.88,
        "Bölüm ve tarih alanları bulundu, müsaitlik sorgusu başlatıldı.",
    )
