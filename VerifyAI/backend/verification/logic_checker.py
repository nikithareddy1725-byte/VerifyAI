import re
from typing import List
from models.schemas import GeneratedAnswer, EvidenceItem, VerificationResult

class LogicChecker:
    def check(self, answer: GeneratedAnswer, evidence: List[EvidenceItem]) -> VerificationResult:
        score = 1.0
        failed_items = []
        
        # Absolute words
        absolutes = {'always', 'never', 'all', 'none'}
        causal_words = {'because', 'therefore', 'causes', 'thus', 'consequently'}
        
        for claim in answer.claims:
            words = set(re.findall(r'\w+', claim.text.lower()))
            
            # Check for absolutes without evidence
            if words.intersection(absolutes):
                score -= 0.15
                failed_items.append(f"Absolute claim detected without qualification: {claim.text}")
                
            # Check for causal words
            if words.intersection(causal_words):
                # Check if there is evidence supporting this causal claim
                has_support = any(
                    cw in item.supporting_text.lower() for item in evidence for cw in causal_words
                )
                if not has_support:
                    score -= 0.15
                    failed_items.append(f"Unsupported causal claim: {claim.text}")

        # Basic contradiction and circular reasoning check
        texts = [c.text.lower() for c in answer.claims]
        for i, text1 in enumerate(texts):
            for j, text2 in enumerate(texts):
                if i != j:
                    if f"not {text1}" in text2 or f"not {text2}" in text1:
                        score -= 0.15
                        failed_items.append("Contradictory statements detected.")
        
        score = max(0.0, score)
        
        if score >= 0.7:
            status = "PASS"
        elif score >= 0.4:
            status = "WARNING"
        else:
            status = "FAIL"
            
        if score == 1.0 and not failed_items:
            details = "No logical issues detected."
        else:
            details = f"Detected {len(failed_items)} logical issues."
            
        return VerificationResult(
            check_type="logic_check",
            status=status,
            score=score,
            details=details,
            failed_items=failed_items
        )
