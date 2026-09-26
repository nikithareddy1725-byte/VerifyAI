from typing import Optional, List, Dict, Any
from models.schemas import TaskPlan
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient
from retrieval.evidence import EvidenceRetriever
from retrieval.gemini_service import GeminiService

class ResearcherAgent:
    def __init__(self, db_client: SupabaseClient, logger: Optional[AgentLogger] = None):
        self.db_client = db_client
        self.logger = logger or AgentLogger(__name__)
        self.retriever = EvidenceRetriever()

    async def execute(self, task_input: str, plan: TaskPlan, gemini_api_key: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        self.logger.info(f"ResearcherAgent starting evidence retrieval for: {task_input[:50]}")
        try:
            # 1. Try Live Gemini Search / Research if API key is provided
            if gemini_api_key or GeminiService().is_active:
                gemini = GeminiService(api_key=gemini_api_key)
                if gemini.is_active:
                    gemini_evidence = gemini.research(query=task_input, task_type=plan.task_type)
                    if gemini_evidence:
                        self.logger.info(f"ResearcherAgent obtained {len(gemini_evidence)} live Gemini research items")
                        return gemini_evidence

            # 2. Local semantic retriever fallback
            results = self.retriever.retrieve(query=task_input, task_type=plan.task_type)
            self.logger.info(f"ResearcherAgent retrieved {len(results)} local evidence items")
            return results
        except Exception as e:
            self.logger.error(f"ResearcherAgent error, using fallback: {e}")
            return self.retriever.retrieve(query=task_input, task_type=plan.task_type)
