import os
import json
from typing import Optional, List, Dict, Any
from utils.logger import AgentLogger

logger = AgentLogger("GeminiService")

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            # Fallback to reading from .env file directly
            env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
            if os.path.exists(env_path):
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.startswith("GEMINI_API_KEY="):
                                key_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                                if key_val:
                                    self.api_key = key_val
                                    break
                except Exception:
                    pass

        self.client = None
        self.is_active = False

        if self.api_key and self.api_key.strip():
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key.strip())
                self.is_active = True
                logger.info("Gemini AI Client initialized successfully!")
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI Client: {e}")

    def research(self, query: str, task_type: str = "general") -> List[Dict[str, Any]]:
        """Conducts live factual research via Gemini model if configured."""
        if not self.is_active or not self.client:
            return []

        prompt = f"""You are an elite Research Agent in VerifyAI.
User Query: "{query}"
Task Type: {task_type}

Conduct factual research. Return 2-4 authoritative evidence points.
Format your response STRICTLY as a JSON array of objects:
[
  {{
    "source": "Name of authoritative source (e.g. Encyclopedia Britannica, Official Documentation, Peer-Reviewed Journal)",
    "text": "Precise factual excerpt or evidence statement directly addressing the query.",
    "reliability": 0.95,
    "relevance": 0.98,
    "source_type": "documentation"
  }}
]
Do not include any markdown fences or preamble. Output raw JSON only."""

        models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
        for model_name in models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

                parsed = json.loads(raw_text)
                if isinstance(parsed, list) and len(parsed) > 0:
                    logger.info(f"Gemini live research retrieved {len(parsed)} sources for '{query[:40]}' using {model_name}")
                    return parsed
            except Exception as e:
                logger.warning(f"Gemini model {model_name} research attempt failed: {e}")

        return []

    def generate(self, task_input: str, task_type: str, evidence_texts: List[str]) -> Optional[Dict[str, Any]]:
        """Generates a preliminary structured answer using Gemini."""
        if not self.is_active or not self.client:
            return None

        evidence_str = "\n".join([f"- {t}" for t in evidence_texts]) if evidence_texts else "None provided."
        prompt = f"""You are the Generator Agent in VerifyAI.
Task: "{task_input}"
Profile: {task_type}
Grounded Evidence:
{evidence_str}

Formulate an accurate, complete, direct answer. You MUST strictly adhere to the principle:
Separate FACT from INFERENCE, ASSUMPTIONS, and UNCERTAINTIES.

Respond STRICTLY in JSON format:
{{
  "answer_text": "Complete comprehensive answer text directly answering the question accurately.",
  "claims": [
    {{"text": "Atomic factual claim 1.", "category": "fact"}},
    {{"text": "Atomic factual claim 2.", "category": "fact"}}
  ],
  "assumptions": ["Any underlying operational assumptions"],
  "uncertainties": ["Any remaining uncertainties if information is incomplete"]
}}
Do not include markdown fences outside the JSON. Output raw JSON only."""

        models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
        for model_name in models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

                parsed = json.loads(raw_text)
                if isinstance(parsed, dict) and "answer_text" in parsed:
                    logger.info(f"Gemini generation created structured answer with {len(parsed.get('claims', []))} claims using {model_name}")
                    return parsed
            except Exception as e:
                logger.warning(f"Gemini model {model_name} generation attempt failed: {e}")

        return None
