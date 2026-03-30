from app.models import DecisionStep, RouteType

_TR_MAP = str.maketrans("çğıöşüâîû", "cgiosuaiu")


def _normalize(text: str) -> str:
    return text.lower().translate(_TR_MAP)


APPOINTMENT_KEYWORDS = {
    "randevu",
    "appointment",
    "doktor",
    "muayene",
    "saat",
    "tarih",
    "bolum",
}

RED_FLAG_KEYWORDS = {
    "nefes alamiyorum",
    "gogus agrisi",
    "bilinc kaybi",
    "intihar",
    "asiri kanama",
    "chest pain",
    "can't breathe",
    "suicidal",
}


def classify_intent(
    message: str,
) -> tuple[RouteType, float, str, list[DecisionStep]]:
    text = _normalize(message)
    steps: list[DecisionStep] = []

    matched_red = [f for f in RED_FLAG_KEYWORDS if f in text]
    if matched_red:
        steps.append(
            DecisionStep(
                step="red_flag_check",
                outcome="triggered",
                detail=f"Eşleşen kırmızı bayraklar: {matched_red}",
            )
        )
        return (
            "escalation",
            0.95,
            "Mesajda yüksek riskli semptom anahtar kelimeleri tespit edildi.",
            steps,
        )

    steps.append(
        DecisionStep(
            step="red_flag_check",
            outcome="clear",
            detail="Kırmızı bayrak ifadesi bulunamadı.",
        )
    )

    matched_appt = [w for w in APPOINTMENT_KEYWORDS if w in text]
    if matched_appt:
        steps.append(
            DecisionStep(
                step="appointment_keyword_check",
                outcome="triggered",
                detail=f"Eşleşen randevu sinyalleri: {matched_appt}",
            )
        )
        return (
            "appointment_request",
            0.86,
            "Mesajda randevu ile ilgili niyet sinyalleri bulundu.",
            steps,
        )

    steps.append(
        DecisionStep(
            step="appointment_keyword_check",
            outcome="clear",
            detail="Randevu sinyali bulunamadı.",
        )
    )
    steps.append(
        DecisionStep(
            step="default_route",
            outcome="medical_info",
            detail="Mesaj bilgilendirme talebi olarak sınıflandırıldı.",
        )
    )

    return (
        "medical_info",
        0.80,
        "Mesaj bilgilendirme/medikal bilgi talebi olarak sınıflandırıldı.",
        steps,
    )
