import re
from typing import List
from models.schemas import GeneratedAnswer, EvidenceItem, VerificationResult
from tools.calculator import Calculator

class ComputationChecker:
    def __init__(self):
        self.calculator = Calculator()

    def check(self, answer: GeneratedAnswer, evidence: List[EvidenceItem]) -> VerificationResult:
        # Detect basic mathematical expressions e.g. 5 + 3 = 8 or something similar
        # Extract expressions like "5 + 3" and the expected result
        math_pattern = r'(\d+(?:\.\d+)?\s*[\+\-\*\/]\s*\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)'
        computations = re.findall(math_pattern, answer.answer_text)
        
        if not computations:
            return VerificationResult(
                check_type="computation_check",
                status="NOT_REQUIRED",
                score=1.0,
                details="No mathematical computations detected.",
                failed_items=[]
            )

        correct = 0
        failed_items = []
        
        for expr, expected_str in computations:
            expected = float(expected_str)
            res = self.calculator.evaluate(expr)
            if res.get('success'):
                if abs(float(res['result']) - expected) < 1e-5:
                    correct += 1
                else:
                    failed_items.append(f"Computation failed: {expr} != {expected}")
            else:
                failed_items.append(f"Invalid computation: {expr}")
                
        score = correct / len(computations) if computations else 1.0
        
        if score == 1.0:
            status = "PASS"
        elif score >= 0.5:
            status = "WARNING"
        else:
            status = "FAIL"
            
        return VerificationResult(
            check_type="computation_check",
            status=status,
            score=score,
            details=f"{correct} out of {len(computations)} computations verified.",
            failed_items=failed_items
        )
