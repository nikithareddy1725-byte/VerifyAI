from typing import Optional
from models.schemas import AmbiguityResult
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient

class AmbiguityAgent:
    def __init__(self, db_client: SupabaseClient, logger: Optional[AgentLogger] = None):
        self.db_client = db_client
        self.logger = logger or AgentLogger(__name__)

    async def execute(self, task_input: str, **kwargs) -> AmbiguityResult:
        self.logger.info("AmbiguityAgent starting")
        try:
            stripped = task_input.strip()
            words = [w for w in stripped.split() if w]
            req = False
            details = []
            assumptions = ["Standard domain interpretation and authoritative consensus assumed"]
            
            # Only trigger clarification if input is literally empty or meaningless punctuation
            if not stripped or len(stripped) <= 1 or stripped in ["?", "??", "...", "!", "help", "what", "why"]:
                req = True
                details.append("Input too brief or punctuation-only to determine intent")
            else:
                lower_input = stripped.lower()
                # If subjective or comparative, formulate explicit assumptions and proceed!
                if any(w in lower_input for w in ["best", "better", "should i", "which is faster", "compare"]):
                    assumptions.append("Comparative analysis based on standard industry benchmarks and trade-offs")
                if len(words) <= 2:
                    assumptions.append(f"Interpreted as encyclopedic conceptual inquiry regarding '{stripped}'")
                
            res = AmbiguityResult(
                ambiguous=req,
                clarification_required=req,
                details=details,
                ambiguities=details,
                assumptions=assumptions
            )
            self.logger.info(f"AmbiguityAgent completed. Required: {req}")
            return res
        except Exception as e:
            self.logger.error(f"AmbiguityAgent failed: {e}")
            raise
