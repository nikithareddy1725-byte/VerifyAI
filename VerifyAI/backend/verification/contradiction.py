from typing import List
from models.schemas import GeneratedAnswer, EvidenceItem, VerificationResult, ContradictionResult

class ContradictionDetector:
    def detect(self, answer: GeneratedAnswer, evidence: List[EvidenceItem]) -> ContradictionResult:
        conflicts = []
        negations = ['not', "don't", 'never', 'none', 'cannot']
        
        claims = [c.text for c in answer.claims]
        
        # Internal contradictions
        for i, c1 in enumerate(claims):
            for j, c2 in enumerate(claims):
                if i < j:
                    for neg in negations:
                        if f"{neg} " in c1 and c1.replace(f"{neg} ", "") in c2:
                            conflicts.append({'claim_a': c1, 'claim_b': c2, 'reason': 'Direct negation'})
                        elif f"{neg} " in c2 and c2.replace(f"{neg} ", "") in c1:
                            conflicts.append({'claim_a': c1, 'claim_b': c2, 'reason': 'Direct negation'})
                            
        # Contradictions with evidence
        for claim in claims:
            for item in evidence:
                for neg in negations:
                    if f"{neg} " in claim and claim.replace(f"{neg} ", "") in item.supporting_text:
                        conflicts.append({'claim_a': claim, 'claim_b': item.supporting_text, 'reason': 'Contradicts evidence'})
                    elif f"{neg} " in item.supporting_text and item.supporting_text.replace(f"{neg} ", "") in claim:
                        conflicts.append({'claim_a': claim, 'claim_b': item.supporting_text, 'reason': 'Contradicts evidence'})
                        
        if len(conflicts) > 2:
            severity = 'high'
        elif len(conflicts) > 0:
            severity = 'medium'
        else:
            severity = 'low'
            
        return ContradictionResult(
            has_contradiction=len(conflicts) > 0,
            conflicts=conflicts,
            severity=severity
        )

    def check(self, answer: GeneratedAnswer, evidence: List[EvidenceItem]) -> VerificationResult:
        res = self.detect(answer, evidence)
        
        if res.has_contradiction:
            score = max(0.0, 1.0 - (0.3 * len(res.conflicts)))
            if score >= 0.7:
                status = "WARNING"
            else:
                status = "FAIL"
        else:
            score = 1.0
            status = "PASS"
            
        return VerificationResult(
            check_type="contradiction_check",
            status=status,
            score=score,
            details=f"Detected {len(res.conflicts)} contradictions.",
            failed_items=[c['reason'] for c in res.conflicts]
        )
