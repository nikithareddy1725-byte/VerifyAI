import re
from typing import List
from models.schemas import GeneratedAnswer, EvidenceItem, VerificationResult

class FactChecker:
    def check(self, answer: GeneratedAnswer, evidence: List[EvidenceItem]) -> VerificationResult:
        fact_claims = [claim for claim in answer.claims if claim.category == 'fact']
        
        if not fact_claims:
            return VerificationResult(
                check_type="fact_check",
                status="NOT_REQUIRED",
                score=1.0,
                details="No factual claims found.",
                failed_items=[]
            )

        supported_count = 0
        unsupported_items = []

        for claim in fact_claims:
            claim_words = set(re.findall(r'\w+', claim.text.lower()))
            if not claim_words:
                continue

            is_supported = False
            for item in evidence:
                evidence_words = set(re.findall(r'\w+', item.supporting_text.lower()))
                if not evidence_words:
                    continue
                
                overlap = len(claim_words.intersection(evidence_words)) / len(claim_words)
                if overlap > 0.3:
                    is_supported = True
                    break
            
            if is_supported:
                supported_count += 1
            else:
                unsupported_items.append(claim.text)

        score = supported_count / len(fact_claims)
        
        if score >= 0.7:
            status = "PASS"
        elif score >= 0.4:
            status = "WARNING"
        else:
            status = "FAIL"

        return VerificationResult(
            check_type="fact_check",
            status=status,
            score=score,
            details=f"{supported_count} out of {len(fact_claims)} facts supported.",
            failed_items=unsupported_items
        )
