import uuid
import re
from datetime import datetime
from typing import List, Dict

def generate_task_id() -> str:
    return str(uuid.uuid4())

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def safe_truncate(text: str, max_len: int = 150) -> str:
    if not text:
        return ""
    return (text[:max_len] + "...") if len(text) > max_len else text

def calculate_weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    total_weight = 0.0
    weighted_sum = 0.0
    for key, score in scores.items():
        weight = weights.get(key, 0.0)
        weighted_sum += score * weight
        total_weight += weight
    return (weighted_sum / total_weight) if total_weight > 0 else 1.0

def split_into_sentences(text: str) -> List[str]:
    if not text:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def extract_claims_from_text(text: str) -> List[str]:
    sentences = split_into_sentences(text)
    claims = []
    for s in sentences:
        if len(s.split()) >= 3:
            claims.append(s)
    return claims or [text]
