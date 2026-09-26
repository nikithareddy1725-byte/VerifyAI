from typing import List
from models.schemas import GeneratedAnswer, EvidenceItem, VerificationResult

class SourceReliabilityChecker:
    def check(self, answer: GeneratedAnswer, evidence: List[EvidenceItem]) -> VerificationResult:
        if not evidence:
            return VerificationResult(
                check_type="source_reliability",
                status="NOT_REQUIRED",
                score=1.0,
                details="No evidence provided to check.",
                failed_items=[]
            )

        total_reliability = 0.0
        
        for item in evidence:
            st = item.source_type.lower() if item.source_type else ''
            
            if any(k in st for k in ['documentation', 'encyclopedia', 'academic', 'journal', 'reference', 'textbook', 'database', 'official']):
                base_score = 0.95
            elif any(k in st for k in ['research', 'study', 'compendium']):
                base_score = 0.90
            elif 'web' in st or 'news' in st:
                base_score = 0.80
            elif 'user' in st:
                base_score = 0.60
            else:
                base_score = getattr(item, 'source_reliability', 0.85)
                
            # Adjust based on specificity (length of supporting text)
            if len(item.supporting_text) > 50:
                base_score = min(1.0, base_score + 0.05)
                
            # Assume relevance is provided in EvidenceItem, fallback to 1.0
            relevance = getattr(item, 'relevance', 1.0)
            reliability = base_score * relevance
            total_reliability += reliability
            
        avg_reliability = total_reliability / len(evidence)
        
        if avg_reliability > 0.7:
            status = "PASS"
        elif avg_reliability > 0.4:
            status = "WARNING"
        else:
            status = "FAIL"
            
        return VerificationResult(
            check_type="source_reliability",
            status=status,
            score=avg_reliability,
            details=f"Average source reliability: {avg_reliability:.2f}",
            failed_items=[]
        )
