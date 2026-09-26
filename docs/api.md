# VerifyAI REST API Specification

This document details the RESTful HTTP API for the VerifyAI Multi-Agent Verification Platform, built on FastAPI.

---

## 1. Overview & Base URL

- **Base URL**: `http://localhost:8000/api/v1`
- **Content-Type**: `application/json`
- **Interactive Documentation**:
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

---

## 2. Authentication

VerifyAI supports two authentication models:
1. **API Key Authentication**: Pass the API key in the `X-API-Key` HTTP header.
   ```http
   X-API-Key: vai_live_7f8a9b2c3d4e5f6a
   ```
2. **Bearer Token (Supabase JWT)**: Pass the user JWT in the `Authorization` header.
   ```http
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

*Note*: For local development and demonstration purposes, authentication can be configured in permissive mode by setting `ENV=development` in `.env`.

---

## 3. Endpoints Specification

### 3.1 Submit Verification Request
Dispatches a user prompt or candidate answer into the multi-agent verification pipeline.

- **Method**: `POST`
- **Path**: `/api/v1/verify`
- **Request Body**:
  ```json
  {
    "input_text": "What is machine learning?",
    "task_type": "factual",
    "context": {
      "candidate_answer": "Machine learning is a field of artificial intelligence focused on building applications that learn from data and improve their accuracy over time without being programmed to do so.",
      "strict_mode": true
    }
  }
  ```
- **Response**: `200 OK` (Synchronous completion) or `202 Accepted` (Async processing)
  ```json
  {
    "task_id": "7d9c6c40-3d84-4b5b-80a2-9b24479352e0",
    "status": "completed",
    "task_type": "factual",
    "decision": "ACCEPT",
    "confidence": 0.96,
    "final_answer": "Machine learning is a branch of artificial intelligence and computer science focused on using data and algorithms to imitate the way that humans learn, gradually improving accuracy.",
    "verification_passport": {
      "passport_id": "9b12a842-8c10-4bf6-b519-86641e7845f1",
      "status": "CERTIFIED",
      "score": 0.96,
      "stamps": {
        "factual_accuracy": "PASS",
        "claim_verification": "PASS",
        "hallucination_detection": "PASS",
        "contradiction_detection": "PASS",
        "code_check": "NOT_APPLICABLE",
        "safety_risk_check": "PASS",
        "ambiguity_completeness_check": "PASS",
        "premise_validation": "PASS",
        "consistency_reasoning_check": "PASS"
      },
      "verified_claims_count": 3,
      "evidence_sources_count": 4,
      "integrity_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "issued_at": "2026-09-25T09:41:20Z"
    }
  }
  ```

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/api/v1/verify" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: vai_live_demo" \
     -d '{
       "input_text": "Explain binary search",
       "task_type": "factual"
     }'
```

---

### 3.2 Get Task Status and Passport
Retrieves the comprehensive execution state and generated verification passport for a given task ID.

- **Method**: `GET`
- **Path**: `/api/v1/tasks/{task_id}`
- **Path Parameters**:
  - `task_id` (UUID, required): The unique identifier of the task.
- **Response**: `200 OK`
  ```json
  {
    "id": "7d9c6c40-3d84-4b5b-80a2-9b24479352e0",
    "input_text": "Explain binary search",
    "task_type": "factual",
    "status": "completed",
    "score": 0.95,
    "plan": {
      "steps": ["QueryClassifier", "EvidenceRetriever", "ClaimExtractor", "VerificationSuite", "PassportSynthesis"],
      "estimated_latency_ms": 1800
    },
    "final_decision": {
      "decision": "ACCEPT",
      "reasoning": "All 4 extracted claims entailed by standard algorithms literature."
    },
    "verification_passport": {
      "passport_id": "9b12a842-8c10-4bf6-b519-86641e7845f1",
      "status": "CERTIFIED",
      "score": 0.95,
      "stamps": {
        "factual_accuracy": "PASS",
        "claim_verification": "PASS",
        "safety_risk_check": "PASS"
      }
    },
    "created_at": "2026-09-25T09:41:18Z",
    "updated_at": "2026-09-25T09:41:20Z"
  }
  ```

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/7d9c6c40-3d84-4b5b-80a2-9b24479352e0" \
     -H "X-API-Key: vai_live_demo"
```

---

### 3.3 List Agent Execution Runs
Fetches telemetry for every agent invoked during the processing of a specific task.

- **Method**: `GET`
- **Path**: `/api/v1/tasks/{task_id}/runs`
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "b182cb05-24e6-4299-a864-1c64eb3e9619",
      "task_id": "7d9c6c40-3d84-4b5b-80a2-9b24479352e0",
      "agent_name": "QueryClassifierAgent",
      "agent_icon": "🔍",
      "action": "Classified input query as factual definition",
      "status": "completed",
      "step_order": 1,
      "input_summary": "Explain binary search",
      "output_summary": "task_type=factual, confidence=0.99",
      "started_at": "2026-09-25T09:41:18.100Z",
      "completed_at": "2026-09-25T09:41:18.250Z",
      "error": null
    },
    {
      "id": "c294db16-35f7-4388-b975-2d75fc4e0728",
      "task_id": "7d9c6c40-3d84-4b5b-80a2-9b24479352e0",
      "agent_name": "EvidenceRetrieverAgent",
      "agent_icon": "📚",
      "action": "Retrieved 3 authoritative CS textbook snippets",
      "status": "completed",
      "step_order": 2,
      "input_summary": "Claims: Binary search O(log n)",
      "output_summary": "Found 3 references from Knuth & Cormen",
      "started_at": "2026-09-25T09:41:18.255Z",
      "completed_at": "2026-09-25T09:41:18.750Z",
      "error": null
    }
  ]
  ```

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/7d9c6c40-3d84-4b5b-80a2-9b24479352e0/runs" \
     -H "X-API-Key: vai_live_demo"
```

---

### 3.4 Get Extracted Claims and Grounding Evidence
Retrieves the atomic propositions extracted by `ClaimExtractorAgent` along with the corroborating evidence snippets.

- **Method**: `GET`
- **Path**: `/api/v1/tasks/{task_id}/claims`
- **Response**: `200 OK`
  ```json
  {
    "task_id": "7d9c6c40-3d84-4b5b-80a2-9b24479352e0",
    "claims": [
      {
        "claim_id": "CLM-001",
        "text": "Binary search requires an array to be sorted prior to execution.",
        "category": "algorithmic",
        "supported": true,
        "confidence": 0.99,
        "evidence_ids": ["EVD-101", "EVD-102"]
      },
      {
        "claim_id": "CLM-002",
        "text": "The worst-case time complexity of binary search is O(log n).",
        "category": "complexity",
        "supported": true,
        "confidence": 0.98,
        "evidence_ids": ["EVD-101"]
      }
    ],
    "evidence": [
      {
        "evidence_id": "EVD-101",
        "source": "Introduction to Algorithms (CLRS), Chapter 2",
        "source_type": "textbook",
        "source_reliability": 1.0,
        "relevance": 0.97,
        "supporting_text": "Binary search works by comparing the target value to the middle element of the sorted array."
      }
    ]
  }
  ```

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/7d9c6c40-3d84-4b5b-80a2-9b24479352e0/claims" \
     -H "X-API-Key: vai_live_demo"
```

---

### 3.5 Get Immutable Audit Log
Retrieves the cryptographic provenance log for compliance, auditing, and debugging.

- **Method**: `GET`
- **Path**: `/api/v1/tasks/{task_id}/audit`
- **Response**: `200 OK`
  ```json
  {
    "task_id": "7d9c6c40-3d84-4b5b-80a2-9b24479352e0",
    "task_type": "factual",
    "iterations": 0,
    "final_decision": "ACCEPT",
    "confidence": 0.96,
    "agents_executed": ["Planner", "QueryClassifier", "EvidenceRetriever", "ClaimExtractor", "FactVerifier", "PassportSynthesis"],
    "verification_scores": {
      "factual_accuracy": 0.98,
      "claim_verification": 0.96,
      "hallucination_detection": 1.0,
      "safety_risk_check": 1.0
    },
    "verification_passport": {
      "passport_id": "9b12a842-8c10-4bf6-b519-86641e7845f1",
      "integrity_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "created_at": "2026-09-25T09:41:20Z"
  }
  ```

---

### 3.6 Run Batch Evaluations
Executes the evaluation suite against pre-defined test categories (`normal`, `ambiguous`, `incomplete`, `conflicting`, `misleading`, `hallucination`, `coding`, `risk`).

- **Method**: `POST`
- **Path**: `/api/v1/evaluate`
- **Request Body**:
  ```json
  {
    "category": "misleading",
    "max_cases": 5
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "category": "misleading",
    "total_cases": 5,
    "passed": 5,
    "failed": 0,
    "accuracy": 1.0,
    "results": [
      {
        "id": "MIS-001",
        "input": "The Great Wall is visible from space...",
        "expected_decision": "CORRECTED",
        "actual_decision": "CORRECTED",
        "status": "PASS"
      }
    ]
  }
  ```

---

### 3.7 Health Check Endpoint
Checks API uptime, background task worker responsiveness, and Supabase connectivity.

- **Method**: `GET`
- **Path**: `/api/v1/health`
- **Response**: `200 OK`
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "version": "1.0.0",
    "uptime_seconds": 86420,
    "active_workers": 4
  }
  ```

---

## 4. HTTP Error Codes & Envelope

All API errors return a standardized JSON error envelope:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Task with ID 7d9c6c40-3d84-4b5b-80a2-9b24479352e0 was not found.",
    "details": {
      "task_id": "7d9c6c40-3d84-4b5b-80a2-9b24479352e0"
    }
  }
}
```

### Standard Status Codes:
| Status Code | Error Code | Description |
| :--- | :--- | :--- |
| `400 Bad Request` | `INVALID_PAYLOAD` | Missing required fields or malformed JSON syntax. |
| `401 Unauthorized` | `AUTHENTICATION_REQUIRED` | Missing or invalid API key / Supabase token. |
| `403 Forbidden` | `ACCESS_DENIED` | Token lacks permissions to inspect target task. |
| `404 Not Found` | `RESOURCE_NOT_FOUND` | Specified task, claim, or audit log does not exist. |
| `422 Unprocessable` | `VALIDATION_ERROR` | Pydantic schema validation failure on request parameters. |
| `500 Internal Error` | `SYSTEM_ERROR` | Unhandled runtime exception in verification pipeline. |
