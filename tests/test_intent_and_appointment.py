from app.services.appointment_agent import handle_appointment
from app.services.intent_classifier import classify_intent


class TestIntentClassifier:
    def test_chest_pain_is_escalation(self):
        route, conf, _, _ = classify_intent("I have pain in my chest when I breathe deeply.")
        assert route == "escalation"
        assert conf >= 0.9

    def test_cant_breathe_is_escalation(self):
        route, _, _, _ = classify_intent("Help, I cannot breathe properly!")
        assert route == "escalation"

    def test_suicide_is_escalation(self):
        route, _, _, _ = classify_intent("I feel suicidal today.")
        assert route == "escalation"

    def test_appointment_keyword(self):
        route, _, _, _ = classify_intent("I would like to book an appointment for cardiology.")
        assert route == "appointment_request"

    def test_default_is_medical_info(self):
        route, _, _, _ = classify_intent("What are the symptoms of diabetes?")
        assert route == "medical_info"

    def test_empty_message_safe(self):
        route, _, _, steps = classify_intent("Hello")
        assert route in {"medical_info", "appointment_request", "escalation"}
        assert len(steps) >= 1


class TestAppointmentAgent:
    def test_missing_slots(self):
        answer, sources, conf, rationale = handle_appointment("I want an appointment")
        assert "department" in answer.lower() and "date" in answer.lower()
        assert sources == []
        assert conf < 0.8

    def test_full_slots_numeric_date(self):
        answer, sources, conf, _ = handle_appointment(
            "Book a cardiology appointment on 12/05/2026"
        )
        assert "cardiology" in answer.lower()
        assert "12/05/2026" in answer
        assert len(sources) == 1
        assert conf >= 0.85

    def test_full_slots_relative_date(self):
        answer, sources, _, _ = handle_appointment(
            "I need a dermatology visit tomorrow please."
        )
        assert "dermatology" in answer.lower()
        assert "tomorrow" in answer.lower()
        assert len(sources) == 1
