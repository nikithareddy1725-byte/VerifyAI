from typing import Any, Dict

TASKS_TABLE = "tasks"
AGENT_RUNS_TABLE = "agent_runs"
EVIDENCE_TABLE = "evidence"
CLAIMS_TABLE = "claims"
VERIFICATION_RESULTS_TABLE = "verification_results"
CORRECTIONS_TABLE = "corrections"
AUDIT_LOG_TABLE = "audit_log"
TOOL_TESTS_TABLE = "tool_tests"

def to_dict(obj: Any) -> Dict[str, Any]:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        return obj.dict()
    elif isinstance(obj, dict):
        return obj
    return {"data": str(obj)}
