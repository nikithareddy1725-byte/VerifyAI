from typing import Optional, List
from models.schemas import VerificationResult, GeneratedAnswer, EvidenceItem
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient
from verification import (
    FactChecker,
    LogicChecker,
    ComputationChecker,
    CodeChecker,
    ApiChecker,
    ContradictionDetector,
    SourceReliabilityChecker,
    RiskDetector,
    ConfidenceCalculator
)

class VerifierAgent:
    def __init__(self, db_client: SupabaseClient, logger: Optional[AgentLogger] = None):
        self.db_client = db_client
        self.logger = logger or AgentLogger(__name__)
        
        self.checkers = {
            "fact_checker": FactChecker(),
            "logic_checker": LogicChecker(),
            "computation_checker": ComputationChecker(),
            "code_checker": CodeChecker(),
            "api_checker": ApiChecker(),
            "contradiction": ContradictionDetector(),
            "source_reliability": SourceReliabilityChecker(),
            "risk_detector": RiskDetector()
        }

    async def execute(self, answer: GeneratedAnswer, evidence: List[EvidenceItem], required_checks: List[str], **kwargs) -> List[VerificationResult]:
        self.logger.info(f"VerifierAgent starting independent verification. Required checks: {required_checks}")
        results = []
        
        for name, checker in self.checkers.items():
            try:
                if name in required_checks or not required_checks:
                    res = checker.check(answer, evidence)
                else:
                    res = VerificationResult(
                        check_type=name,
                        status="NOT_REQUIRED",
                        score=1.0,
                        details="Check not required for this task profile.",
                        failed_items=[]
                    )
                results.append(res)
            except Exception as e:
                self.logger.error(f"Checker {name} error: {e}")
                results.append(VerificationResult(
                    check_type=name,
                    status="WARNING",
                    score=0.5,
                    details=f"Checker execution warning: {e}",
                    failed_items=[str(e)]
                ))
                
        self.logger.info(f"VerifierAgent completed {len(results)} independent checks")
        return results
