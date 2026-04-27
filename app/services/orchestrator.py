"""
Orchestrator: ties together query enhancement, multi-source retrieval,
re-ranking, structured LLM output, and XAI explanation.
"""

from __future__ import annotations

import structlog

from app.models import ChatResponse, DecisionStep, MedicalAnswer
from app.services.appointment_agent import handle_appointment
from app.services.intent_classifier import classify_intent
from app.services.multi_retriever import multi_retrieve
from app.services.query_enhancer import generate_hyde_document, rewrite_query
from app.services.reranker import rerank
from app.services.structured_output import generate_structured_answer
from app.services.xai_service import build_explanation

logger = structlog.get_logger(__name__)


def run_pipeline(
    message: str,
    session_id: str | None = None,
    conversation_history: list[dict] | None = None,
) -> ChatResponse:
    logger.info("pipeline_started", route_pending=True, session_id=session_id)

    # --- Step 1: Intent classification ---
    route, route_confidence, route_rationale, steps = classify_intent(message)
    logger.info("intent_classified", route=route, confidence=route_confidence)

    # --- Escalation: skip all retrieval ---
    if route == "escalation":
        answer = (
            "The situation you described may involve an emergency risk. "
            "Please call 911 immediately or go to the nearest emergency room."
        )
        steps.append(DecisionStep(
            step="escalation_response",
            outcome="generated",
            detail="Emergency redirect message generated; LLM call skipped.",
        ))
        xai = build_explanation(
            route=route, confidence=route_confidence,
            rationale=route_rationale, sources=[],
            decision_path=steps, message=message,
        )
        return ChatResponse(answer=answer, route=route, xai=xai, session_id=session_id)

    # --- Appointment request ---
    if route == "appointment_request":
        answer, sources, conf, rationale, department = handle_appointment(message)
        steps.append(DecisionStep(
            step="appointment_slot_filling",
            outcome="processed",
            detail=rationale,
        ))
        xai = build_explanation(
            route=route, confidence=min(route_confidence, conf),
            rationale=f"{route_rationale} {rationale}",
            sources=sources, decision_path=steps, message=message,
        )
        return ChatResponse(
            answer=answer, 
            route=route, 
            xai=xai, 
            session_id=session_id,
            suggested_department=department
        )

    # --- Medical info: full RAG pipeline ---

    # Step 2: Query enhancement (rewrite + HyDE)
    enhanced_query = rewrite_query(message)
    hyde_doc = generate_hyde_document(message)

    steps.append(DecisionStep(
        step="query_enhancement",
        outcome="rewritten" if enhanced_query != message else "original",
        detail=f"Query: '{enhanced_query[:80]}'" + (" | HyDE generated" if hyde_doc else ""),
    ))

    # Step 3: Embed HyDE doc or enhanced query for retrieval
    hyde_embedding: list[float] | None = None
    if hyde_doc:
        try:
            from sentence_transformers import SentenceTransformer
            from app.config import settings
            _model = SentenceTransformer(settings.embedding_model)
            # Blend original + HyDE embeddings
            import numpy as np
            orig_emb = _model.encode(enhanced_query)
            hyde_emb = _model.encode(hyde_doc)
            blended = (orig_emb * 0.4 + hyde_emb * 0.6)
            blended = blended / (np.linalg.norm(blended) + 1e-8)
            hyde_embedding = blended.tolist()
        except Exception:
            logger.exception("hyde_embedding_failed")

    # Step 4: Multi-source retrieval (top_k_per_source=8 → reranker will trim)
    raw_sources = multi_retrieve(
        question=enhanced_query,
        query_embedding=hyde_embedding,
        top_k_per_source=8,
    )
    steps.append(DecisionStep(
        step="multi_source_retrieval",
        outcome=f"{len(raw_sources)} sources found",
        detail=f"Collections searched: chatdoctor, guidelines, drugs",
    ))

    # Step 5: Re-ranking
    sources = rerank(message, raw_sources, top_k=3)
    steps.append(DecisionStep(
        step="cross_encoder_rerank",
        outcome=f"top {len(sources)} selected",
        detail=f"Top score: {sources[0].score if sources else 'N/A'}",
    ))

    # Step 6: Structured LLM generation
    answer, llm_confidence, structured = generate_structured_answer(message, sources)
    steps.append(DecisionStep(
        step="structured_llm_generation",
        outcome="answer_generated",
        detail=f"Confidence: {llm_confidence}, structured: {structured is not None}",
    ))

    # Step 7: Build XAI explanation
    xai = build_explanation(
        route=route,
        confidence=min(route_confidence, llm_confidence),
        rationale=f"{route_rationale} Answer grounded on multi-source retrieval.",
        sources=sources,
        decision_path=steps,
        message=message,
    )

    # Convert structured to model if present
    med_answer: MedicalAnswer | None = None
    if structured is not None:
        from app.models import Citation
        med_answer = MedicalAnswer(
            answer=structured.answer,
            citations=[Citation(source_id=c.source_id, relevance=c.relevance) for c in structured.citations],
            confidence_reasoning=structured.confidence_reasoning,
            follow_up_questions=structured.follow_up_questions,
        )

    # Attempt to extract department from medical symptom info so they can directly book
    from app.services.appointment_agent import _extract_department
    department = _extract_department(message)
    if department:
        steps.append(DecisionStep(
            step="symptom_triage",
            outcome="department_detected",
            detail=f"Detected {department} from symptoms.",
        ))

    logger.info("pipeline_completed", route=route, sources=len(sources))
    return ChatResponse(
        answer=answer,
        route=route,
        xai=xai,
        session_id=session_id,
        structured_answer=med_answer,
        suggested_department=department
    )
