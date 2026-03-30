from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


RouteType = Literal["medical_info", "appointment_request", "escalation"]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, description="Patient question")
    patient_id: Optional[str] = None


class SourceEvidence(BaseModel):
    id: str
    title: str
    snippet: str
    score: float


class DecisionStep(BaseModel):
    step: str
    outcome: str
    detail: str


class XAIExplanation(BaseModel):
    route: RouteType
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str

    decision_path: List[DecisionStep] = Field(
        default_factory=list,
        description="Ordered list of reasoning steps the system took",
    )

    feature_contributions: Dict[str, float] = Field(
        default_factory=dict,
        description="Keywords/signals and their contribution weight to the decision",
    )

    sources: List[SourceEvidence] = Field(default_factory=list)

    retrieval_quality: Optional[Dict[str, float]] = Field(
        default=None,
        description="Retrieval metrics: avg_score, max_score, coverage",
    )

    safety_note: str


class ChatResponse(BaseModel):
    answer: str
    route: RouteType
    xai: XAIExplanation
