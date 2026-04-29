from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


RouteType = Literal["medical_info", "appointment_request", "escalation"]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, description="Patient question")
    patient_id: Optional[str] = None
    session_id: Optional[str] = None


class SourceEvidence(BaseModel):
    id: str
    title: str
    snippet: str
    score: float
    source_type: str = "chatdoctor"  # chatdoctor | guideline | drug


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


class Citation(BaseModel):
    source_id: str
    relevance: str = ""


class MedicalAnswer(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    confidence_reasoning: str = ""
    follow_up_questions: List[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    route: RouteType
    xai: XAIExplanation
    session_id: Optional[str] = None
    structured_answer: Optional[MedicalAnswer] = None
    suggested_department: Optional[str] = None


# --- Auth models ---
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: str
    username: str
    is_active: bool
    created_at: str
    session_count: int = 0
    appointment_count: int = 0


# --- Session models ---
class SessionInfo(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class MessageInfo(BaseModel):
    id: str
    role: str
    content: str
    route: Optional[str] = None
    created_at: str


# --- Appointment models ---
class AppointmentCreate(BaseModel):
    patient_name: str
    phone: str
    date: str
    time: str
    department: Optional[str] = None
    doctor: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: str
    patient_name: str
    phone: str
    date: str
    time: str
    department: Optional[str] = None
    doctor: Optional[str] = None
    status: str = "pending"
    created_at: str


# --- Admin models ---
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AppointmentStatusUpdate(BaseModel):
    status: str  # "pending" | "confirmed" | "cancelled"


class AdminStats(BaseModel):
    total: int
    today: int
    this_week: int
    by_department: dict
    by_status: dict
