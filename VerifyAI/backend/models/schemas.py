from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

def generate_uuid() -> str:
    return str(uuid.uuid4())

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

class TaskRequest(BaseModel):
    input_text: Optional[str] = None
    query: Optional[str] = None
    task_type: str = "auto"
    gemini_api_key: Optional[str] = None

class TaskPlan(BaseModel):
    task_type: str
    complexity: str = "low"
    required_agents: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    verification_requirements: List[str] = Field(default_factory=list)

class AmbiguityResult(BaseModel):
    ambiguous: bool = False
    ambiguities: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    clarification_required: bool = False
    details: Optional[Union[List[str], Dict[str, Any], str]] = None

class EvidenceItem(BaseModel):
    evidence_id: str = Field(default_factory=generate_uuid)
    claim_supported: Union[bool, str] = True
    source: str = "local_kb"
    source_type: str = "database"
    source_reliability: float = 0.8
    relevance: float = 0.8
    supporting_text: str = ""
    timestamp: Optional[str] = Field(default_factory=now_iso)

class Claim(BaseModel):
    claim_id: str = Field(default_factory=generate_uuid)
    text: str
    category: str = "fact"  # fact, inference, assumption, uncertainty
    supported: bool = False
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.0

class GeneratedAnswer(BaseModel):
    answer_text: str
    claims: List[Claim] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)

class VerificationResult(BaseModel):
    check_type: str
    status: str = "PASS"  # PASS, FAIL, WARNING, NOT_REQUIRED
    score: float = 1.0
    details: str = ""
    failed_items: List[str] = Field(default_factory=list)

class ContradictionResult(BaseModel):
    has_contradiction: bool = False
    conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    severity: str = "low"

class CriticReport(BaseModel):
    issues_found: List[str] = Field(default_factory=list)
    severity: str = "low"  # low, medium, high
    recommendation: str = "accept"  # accept, correct, reject
    details: str = ""

class CorrectionResult(BaseModel):
    original_answer: str
    corrected_answer: str
    corrected_claims: List[Claim] = Field(default_factory=list)
    corrections_made: List[str] = Field(default_factory=list)
    iteration: int = 1

class FinalDecision(BaseModel):
    decision: str = "ACCEPT"  # ACCEPT, CORRECTED, REJECT, NEEDS_CLARIFICATION
    confidence: float = 1.0
    reason: str = ""
    failed_checks: List[str] = Field(default_factory=list)
    passed_checks: List[str] = Field(default_factory=list)

class VerificationPassport(BaseModel):
    task_id: str
    claims_checked: int = 0
    claims_supported: int = 0
    unsupported_claims: int = 0
    evidence_sources: int = 0
    contradictions: int = 0
    logic_check: str = "PASS"
    fact_check: str = "PASS"
    computation_check: str = "NOT_REQUIRED"
    code_check: str = "NOT_REQUIRED"
    api_check: str = "NOT_REQUIRED"
    risk_check: str = "PASS"
    corrections: int = 0
    reverification: str = "PASS"
    final_decision: str = "ACCEPT"
    final_confidence: float = 1.0
    summary: Optional[str] = None

class AgentRunRecord(BaseModel):
    task_id: str
    agent_name: str
    agent_icon: str = "◈"
    action: str = ""
    status: str = "SUCCESS"  # SUCCESS, FAIL, PROCESSING, WAITING
    step_order: int = 0
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    input_summary: str = ""
    output_summary: str = ""
    started_at: str = Field(default_factory=now_iso)
    completed_at: Optional[str] = Field(default_factory=now_iso)
    error: Optional[str] = None
    error_message: Optional[str] = None

class PipelineResult(BaseModel):
    task_id: str
    status: str = "completed"
    success: bool = True
    intent: Optional[str] = None
    profile: Optional[str] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    message: Optional[str] = None
    plan: Optional[TaskPlan] = None
    generated_answer: Optional[GeneratedAnswer] = None
    verification_results: List[VerificationResult] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    critic_report: Optional[CriticReport] = None
    corrections: List[CorrectionResult] = Field(default_factory=list)
    final_decision: Union[str, FinalDecision] = "ACCEPT"
    verification_passport: Optional[VerificationPassport] = None
    audit: Optional[Dict[str, Any]] = None
    agent_runs: List[AgentRunRecord] = Field(default_factory=list)
    details: Optional[Dict[str, Any]] = None
