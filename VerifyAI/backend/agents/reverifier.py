from typing import Optional, List
from models.schemas import VerificationResult, CorrectionResult, EvidenceItem, GeneratedAnswer
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient
from .verifier import VerifierAgent

class ReverifierAgent:
    def __init__(self, db_client: SupabaseClient, logger: Optional[AgentLogger] = None):
        self.db_client = db_client
        self.logger = logger or AgentLogger(__name__)

    async def execute(self, corrected: CorrectionResult, evidence: List[EvidenceItem], required_checks: List[str], **kwargs) -> List[VerificationResult]:
        self.logger.info("ReverifierAgent starting")
        try:
            ans = GeneratedAnswer(
                answer_text=corrected.corrected_answer,
                claims=corrected.corrected_claims,
                assumptions=[],
                uncertainties=[]
            )
            verifier = VerifierAgent(self.db_client, self.logger)
            results = await verifier.execute(answer=ans, evidence=evidence, required_checks=required_checks)
            self.logger.info("ReverifierAgent completed")
            return results
        except Exception as e:
            self.logger.error(f"ReverifierAgent failed: {e}")
            raise
