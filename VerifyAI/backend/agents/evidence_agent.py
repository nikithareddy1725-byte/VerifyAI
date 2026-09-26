import uuid
from typing import Optional, List, Dict, Any
from models.schemas import EvidenceItem
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient

class EvidenceAgent:
    def __init__(self, db_client: SupabaseClient, logger: Optional[AgentLogger] = None):
        self.db_client = db_client
        self.logger = logger or AgentLogger(__name__)

    async def execute(self, raw_research: List[Dict[str, Any]], task_input: str, **kwargs) -> List[EvidenceItem]:
        self.logger.info("EvidenceAgent starting")
        try:
            items = []
            for r in raw_research:
                item = EvidenceItem(
                    evidence_id=str(uuid.uuid4()),
                    claim_supported=True,
                    source=r.get("source", "Reference Documentation"),
                    source_type=r.get("source_type", "documentation"),
                    source_reliability=float(r.get("reliability", 0.9)),
                    relevance=float(r.get("relevance", 0.95)),
                    supporting_text=r.get("text", ""),
                    timestamp="2026-09-25T10:00:00Z"
                )
                items.append(item)
            self.logger.info(f"EvidenceAgent formatted {len(items)} evidence grounding items")
            return items
        except Exception as e:
            self.logger.error(f"EvidenceAgent failed: {e}")
            raise
