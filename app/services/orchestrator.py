from app.models import ChatResponse, DecisionStep
from app.services.appointment_agent import handle_appointment
from app.services.intent_classifier import classify_intent
from app.services.llm_service import generate_answer
from app.services.rag_service import retrieve_context
from app.services.xai_service import build_explanation


def run_pipeline(message: str) -> ChatResponse:
    route, route_confidence, route_rationale, steps = classify_intent(message)

    if route == "escalation":
        answer = (
            "The situation you described may involve an emergency risk. "
            "Please call 911 immediately or go to the nearest emergency room."
        )
        steps.append(
            DecisionStep(
                step="escalation_response",
                outcome="generated",
                detail="Emergency redirect message generated; LLM call skipped.",
            )
        )
        xai = build_explanation(
            route=route,
            confidence=route_confidence,
            rationale=route_rationale,
            sources=[],
            decision_path=steps,
            message=message,
        )
        return ChatResponse(answer=answer, route=route, xai=xai)

    if route == "appointment_request":
        answer, sources, conf, rationale = handle_appointment(message)
        steps.append(
            DecisionStep(
                step="appointment_slot_filling",
                outcome="processed",
                detail=rationale,
            )
        )
        xai = build_explanation(
            route=route,
            confidence=min(route_confidence, conf),
            rationale=f"{route_rationale} {rationale}",
            sources=sources,
            decision_path=steps,
            message=message,
        )
        return ChatResponse(answer=answer, route=route, xai=xai)

    # --- medical_info: RAG + LLM ---
    sources = retrieve_context(message)
    steps.append(
        DecisionStep(
            step="rag_retrieval",
            outcome=f"{len(sources)} sources found",
            detail=f"Top score: {sources[0].score if sources else 'N/A'}",
        )
    )

    answer, llm_confidence = generate_answer(message, sources)
    steps.append(
        DecisionStep(
            step="llm_generation",
            outcome="answer_generated",
            detail=f"LLM confidence estimate: {llm_confidence}",
        )
    )

    xai = build_explanation(
        route=route,
        confidence=min(route_confidence, llm_confidence),
        rationale=f"{route_rationale} The answer was grounded on sources found via retrieval.",
        sources=sources,
        decision_path=steps,
        message=message,
    )
    return ChatResponse(answer=answer, route=route, xai=xai)
