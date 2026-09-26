from typing import Optional, List
from models.schemas import FinalDecision, VerificationResult, CriticReport
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient

class FinalJudgeAgent:
    def __init__(self, db_client: SupabaseClient, logger: Optional[AgentLogger] = None):
        self.db_client = db_client
        self.logger = logger or AgentLogger(__name__)

    async def execute(self, verification_results: List[VerificationResult], critic_report: Optional[CriticReport], corrections_count: int, correction_failed: bool, **kwargs) -> FinalDecision:
        self.logger.info("FinalJudgeAgent starting")
        try:
            failed_checks = [r.check_type for r in verification_results if r.status == "FAIL"]
            passed_checks = [r.check_type for r in verification_results if r.status == "PASS"]
            
            if failed_checks or correction_failed:
                decision = "REJECT"
                reason = "Critical checks failed"
            elif corrections_count > 0:
                decision = "CORRECTED"
                reason = "Passed after corrections"
            else:
                decision = "ACCEPT"
                reason = "All checks passed initially"

            scores = [r.score for r in verification_results if r.status != "NOT_REQUIRED"]
            conf = sum(scores)/len(scores) if scores else 1.0

            res = FinalDecision(
                decision=decision,
                confidence=conf,
                reason=reason,
                failed_checks=failed_checks,
                passed_checks=passed_checks
            )
            self.logger.info(f"FinalJudgeAgent completed: {decision}")
            return res
        except Exception as e:
            self.logger.error(f"FinalJudgeAgent failed: {e}")
            raise
