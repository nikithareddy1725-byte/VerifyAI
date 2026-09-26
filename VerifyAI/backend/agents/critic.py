from typing import Optional, List
from models.schemas import CriticReport, GeneratedAnswer, VerificationResult, EvidenceItem
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient

class CriticAgent:
    def __init__(self, db_client: SupabaseClient, logger: Optional[AgentLogger] = None):
        self.db_client = db_client
        self.logger = logger or AgentLogger(__name__)

    async def execute(self, answer: GeneratedAnswer, verification_results: List[VerificationResult], evidence: List[EvidenceItem], **kwargs) -> CriticReport:
        self.logger.info("CriticAgent starting")
        try:
            issues = []
            rec = "accept"
            for res in verification_results:
                if res.status == "FAIL":
                    issues.append(f"{res.check_type} failed")
                    rec = "correct"
            
            for claim in answer.claims:
                if not claim.supported or claim.confidence < 0.5:
                    issues.append("Low confidence or unsupported claim")
                    rec = "correct"

            report = CriticReport(
                issues_found=issues,
                severity="low" if not issues else "medium",
                recommendation=rec,
                details="Critic evaluation complete"
            )
            self.logger.info(f"CriticAgent completed with recommendation: {rec}")
            return report
        except Exception as e:
            self.logger.error(f"CriticAgent failed: {e}")
            raise
