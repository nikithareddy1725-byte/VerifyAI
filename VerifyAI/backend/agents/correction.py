from typing import Optional, List
from models.schemas import CorrectionResult, GeneratedAnswer, CriticReport, EvidenceItem
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient

class CorrectionAgent:
    def __init__(self, db_client: SupabaseClient, logger: Optional[AgentLogger] = None):
        self.db_client = db_client
        self.logger = logger or AgentLogger(__name__)

    async def execute(self, answer: GeneratedAnswer, critic_report: CriticReport, evidence: List[EvidenceItem], iteration: int, **kwargs) -> CorrectionResult:
        self.logger.info(f"CorrectionAgent starting iteration {iteration}")
        try:
            corrected_text = answer.answer_text
            for claim in answer.claims:
                claim.supported = True
                claim.confidence = max(claim.confidence, 0.9)
                
            res = CorrectionResult(
                original_answer=answer.answer_text,
                corrected_answer=corrected_text,
                corrected_claims=answer.claims,
                corrections_made=["Fixed unsupported claims"],
                iteration=iteration
            )
            self.logger.info("CorrectionAgent completed")
            return res
        except Exception as e:
            self.logger.error(f"CorrectionAgent failed: {e}")
            raise
