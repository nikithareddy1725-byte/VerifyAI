from typing import List
from models.schemas import VerificationResult

class ConfidenceCalculator:
    def calculate(self, results: List[VerificationResult]) -> float:
        base_weights = {
            "fact_check": 0.25,
            "logic_check": 0.20,
            "computation_check": 0.15,
            "code_check": 0.15,
            "source_reliability": 0.10,
            "contradiction_check": 0.10,
            "risk_detection": 0.05
        }
        
        active_weights = {}
        active_scores = {}
        
        for res in results:
            if res.status != "NOT_REQUIRED" and res.check_type in base_weights:
                active_weights[res.check_type] = base_weights[res.check_type]
                active_scores[res.check_type] = res.score
                
        if not active_weights:
            return 1.0
            
        total_weight = sum(active_weights.values())
        
        weighted_score = sum(
            active_scores[ct] * (weight / total_weight)
            for ct, weight in active_weights.items()
        )
        
        return weighted_score
