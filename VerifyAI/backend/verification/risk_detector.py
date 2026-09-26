import re
from typing import List
from models.schemas import GeneratedAnswer, EvidenceItem, VerificationResult

class RiskDetector:
    def check(self, answer: GeneratedAnswer, evidence: List[EvidenceItem]) -> VerificationResult:
        risk_items = []
        text = answer.answer_text.lower()
        
        # Dangerous commands
        dangerous_commands = ['rm -rf', 'drop table', 'sudo', 'format', 'delete']
        for cmd in dangerous_commands:
            if cmd in text:
                risk_items.append(f"Dangerous command detected: {cmd}")
                
        # Security risks
        security_risks = ['eval(', 'exec(', 'select * from']
        for risk in security_risks:
            if risk in text:
                risk_items.append(f"Security risk detected: {risk}")
                
        # Medical/Legal/Financial advice without disclaimers
        advice_keywords = ['treatment', 'cure', 'lawsuit', 'sue', 'invest in', 'buy stocks']
        disclaimers = ['not medical advice', 'not legal advice', 'not financial advice', 'consult a professional']
        
        has_advice = any(k in text for k in advice_keywords)
        has_disclaimer = any(d in text for d in disclaimers)
        
        if has_advice and not has_disclaimer:
            risk_items.append("Potential sensitive advice given without disclaimer.")
            
        score = max(0.0, 1.0 - (0.3 * len(risk_items)))
        
        if len(risk_items) > 0:
            status = "FAIL"
        else:
            status = "PASS"
            
        return VerificationResult(
            check_type="risk_detection",
            status=status,
            score=score,
            details=f"Found {len(risk_items)} risks.",
            failed_items=risk_items
        )
