import re
import json
from typing import List
from models.schemas import GeneratedAnswer, EvidenceItem, VerificationResult

class ApiChecker:
    def check(self, answer: GeneratedAnswer, evidence: List[EvidenceItem]) -> VerificationResult:
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        urls = re.findall(url_pattern, answer.answer_text)
        methods = re.findall(r'\b(GET|POST|PUT|DELETE|PATCH)\b', answer.answer_text)
        
        if not urls and not methods:
            return VerificationResult(
                check_type="api_check",
                status="NOT_REQUIRED",
                score=1.0,
                details="No API content detected.",
                failed_items=[]
            )

        failed_items = []
        issues = 0
        
        for url in urls:
            if not re.match(r'^https?://[^\s/$.?#].[^\s]*$', url):
                issues += 1
                failed_items.append(f"Invalid URL format: {url}")
                
        # Look for JSON blocks
        json_blocks = re.findall(r'```json\s*(.*?)\s*```', answer.answer_text, re.DOTALL)
        for jb in json_blocks:
            try:
                json.loads(jb)
            except json.JSONDecodeError:
                issues += 1
                failed_items.append("Invalid JSON body structure.")

        score = max(0.0, 1.0 - (0.2 * issues))
        
        if score == 1.0:
            status = "PASS"
        elif score >= 0.5:
            status = "WARNING"
        else:
            status = "FAIL"
            
        return VerificationResult(
            check_type="api_check",
            status=status,
            score=score,
            details="API check completed.",
            failed_items=failed_items
        )
