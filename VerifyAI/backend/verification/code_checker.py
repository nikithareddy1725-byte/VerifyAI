import re
from typing import List
from models.schemas import GeneratedAnswer, EvidenceItem, VerificationResult
from tools.code_executor import CodeExecutor

class CodeChecker:
    def __init__(self):
        self.executor = CodeExecutor()

    def check(self, answer: GeneratedAnswer, evidence: List[EvidenceItem]) -> VerificationResult:
        code_blocks = re.findall(r'```(?:python|py)\s*(.*?)\s*```', answer.answer_text, re.DOTALL)
        
        if not code_blocks:
            return VerificationResult(
                check_type="code_check",
                status="NOT_REQUIRED",
                score=1.0,
                details="No code blocks detected.",
                failed_items=[]
            )

        failed_items = []
        score = 0.0
        
        for code in code_blocks:
            block_score = 0.0
            
            # Syntax OK
            try:
                compile(code, '<string>', 'exec')
                block_score += 0.4
            except SyntaxError as e:
                failed_items.append(f"Syntax error: {e}")
                
            # Common issues check (very basic heuristics)
            has_common_issues = False
            if 'while True' in code and 'break' not in code:
                failed_items.append("Possible infinite loop detected.")
                has_common_issues = True
            
            if not has_common_issues:
                block_score += 0.3
                
            # Execution OK
            res = self.executor.execute(code)
            if res.get('success'):
                block_score += 0.3
            else:
                failed_items.append(f"Execution error: {res.get('error')}")
                
            score += block_score
            
        score = score / len(code_blocks) if code_blocks else 1.0
        
        if score >= 0.8:
            status = "PASS"
        elif score >= 0.4:
            status = "WARNING"
        else:
            status = "FAIL"
            
        return VerificationResult(
            check_type="code_check",
            status=status,
            score=score,
            details=f"Checked {len(code_blocks)} code blocks.",
            failed_items=failed_items
        )
