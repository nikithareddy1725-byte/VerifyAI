import re
from typing import Optional
from models.schemas import TaskPlan
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient

class PlannerAgent:
    def __init__(self, db_client: SupabaseClient, logger: Optional[AgentLogger] = None):
        self.db_client = db_client
        self.logger = logger or AgentLogger(__name__)

    async def execute(self, task_input: str, task_type: str = "general", **kwargs) -> TaskPlan:
        self.logger.info(f"PlannerAgent evaluating task input: {task_input[:50]}")
        try:
            text_lower = task_input.lower()
            detected_type = task_type.lower()
            
            # Automatic intent recognition if general or auto
            if detected_type in ["general", "auto", ""]:
                # 1. Risk
                if any(k in text_lower for k in ["rm -rf", "delete all", "drop database", "drop table", "hack ", "exploit", "format c:", "destroy"]):
                    detected_type = "risk"
                # 2. Math & Numerical / Algebra (equations, expressions like 3x+5=, etc.)
                elif (
                    any(k in text_lower for k in ["solve", "calculate", "equation", "integral", "derivative", "sqrt", "algebra", "arithmetic"]) or
                    re.search(r'^\s*[+-]?\s*\d*\s*[a-zA-Z]\s*[+-]\s*\d+', task_input) or
                    re.search(r'^\s*[+-]?\s*\d*\s*[a-zA-Z]\s*=', task_input) or
                    re.search(r'\d+\s*[a-zA-Z]', task_input) or
                    re.search(r'[\d\w]\s*[\+\-\*\/\^%]\s*[\d\w]', task_input) or
                    re.search(r'\d+\s*[+\-*/=^]', task_input) or
                    ("=" in task_input and any(c.isalnum() for c in task_input))
                ) and not any(text_lower.startswith(q) for q in ["who ", "where ", "when ", "why ", "what is ", "explain ", "describe ", "is "]):
                    detected_type = "algebra" if any(c.isalpha() for c in task_input.replace("solve", "").replace("calculate", "")) else "math"
                # 3. Factual Verification & Claim Verification
                elif (
                    any(text_lower.startswith(q) for q in ["is this claim true", "verify that", "is it true", "who ", "what is", "what are", "where is", "when was", "when did", "why is", "how does", "explain", "describe", "tell me about", "is water", "is "]) or
                    any(k in text_lower for k in ["capital of", "who wrote", "who discovered", "who invented", "who painted", "who founded", "ceo of", "prime minister", "president of", "chemical formula"])
                ):
                    detected_type = "fact"
                # 4. Code & Programming
                elif any(k in text_lower for k in ["def ", "class ", "python", "javascript", "write code", "implement function", "script to", "binary search", "factorial", "palindrome", "fibonacci", "algorithm"]):
                    detected_type = "code"
                # 5. Logic & Reasoning
                elif any(k in text_lower for k in ["paradox", "syllogism", "if all ", "fallacy", "contradiction", "premise", "deduce"]):
                    detected_type = "logic"
                # 6. API (use word boundary so 'capital' does not trigger 'api'!)
                elif re.search(r'\b(api|rest api|endpoint|curl|http method|post request|get request)\b', text_lower):
                    detected_type = "api"
                # 7. Text Analysis
                elif any(k in text_lower for k in ["summarize", "sentiment", "analyze text", "grammar check", "word count"]):
                    detected_type = "text_analysis"
                else:
                    detected_type = "general"

            complexity = "low"
            if len(task_input.split()) > 25 or "?" in task_input or any(c in task_input for c in [";", "{", "}"]):
                complexity = "medium"
            if len(task_input.split()) > 60:
                complexity = "high"
            
            agents_map = {
                "general": ["researcher", "evidence_agent", "generator", "fact_checker", "source_reliability", "critic"],
                "fact": ["researcher", "evidence_agent", "generator", "fact_checker", "source_reliability", "contradiction", "critic"],
                "code": ["generator", "code_checker", "logic_checker", "critic"],
                "logic": ["generator", "computation_checker", "logic_checker", "critic"],
                "math": ["generator", "computation_checker", "logic_checker", "critic"],
                "risk": ["researcher", "generator", "risk_detector", "fact_checker", "critic"],
                "api": ["researcher", "generator", "api_checker", "critic"]
            }
            
            required = agents_map.get(detected_type, agents_map["general"])
            steps = [
                f"1. Analyze {detected_type} task intent and complexity ({complexity})",
                "2. Conduct grounded evidence retrieval and source authority ranking",
                "3. Formulate atomic claim decomposition in Generator Agent",
                f"4. Run independent verification pipeline: {', '.join(required[:3])}",
                "5. Subject results to adversarial Critic review and self-correction if required"
            ]
            
            plan = TaskPlan(
                task_type=detected_type,
                complexity=complexity,
                required_agents=required,
                steps=steps,
                verification_requirements=[f"Verify {detected_type} integrity", "Check source reliability and claim support"]
            )
            self.logger.info(f"PlannerAgent completed. Auto-detected Profile: {detected_type}, Complexity: {complexity}")
            return plan
        except Exception as e:
            self.logger.error(f"PlannerAgent failed: {e}")
            raise
