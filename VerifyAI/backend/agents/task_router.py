from typing import Optional, List
from models.schemas import TaskPlan
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient

class TaskRouter:
    def __init__(self, db_client: SupabaseClient, logger: Optional[AgentLogger] = None):
        self.db_client = db_client
        self.logger = logger or AgentLogger(__name__)

    async def execute(self, plan: TaskPlan, **kwargs) -> List[str]:
        self.logger.info("TaskRouter starting")
        try:
            checkers = []
            if "fact_checker" in plan.required_agents: checkers.append("fact_checker")
            if "logic_checker" in plan.required_agents: checkers.append("logic_checker")
            if "computation_checker" in plan.required_agents: checkers.append("computation_checker")
            if "code_checker" in plan.required_agents: checkers.append("code_checker")
            if "api_checker" in plan.required_agents: checkers.append("api_checker")
            if "contradiction" in plan.required_agents: checkers.append("contradiction")
            if "source_reliability" in plan.required_agents: checkers.append("source_reliability")
            if "risk_detector" in plan.required_agents: checkers.append("risk_detector")

            self.logger.info(f"TaskRouter assigned checkers: {checkers}")
            return checkers
        except Exception as e:
            self.logger.error(f"TaskRouter failed: {e}")
            raise
