# VerifyAI Multi-Agent System Specification

VerifyAI coordinates a specialized collective of 15 autonomous micro-agents. Each agent is responsible for an isolated, testable stage of the verification lifecycle, exchanging strongly-typed Pydantic payloads and operating with deterministic local fallbacks.

---

## 1. Agent Directory Summary

| Agent Name | Role | Icon | Activation Condition |
| :--- | :--- | :---: | :--- |
| **PlannerAgent** | Dynamic DAG Orchestration | 🧭 | All requests (Lifecycle root) |
| **QueryClassifierAgent** | Intent & Task Classification | 🔍 | All requests |
| **ClarificationAgent** | Ambiguity & Underspecification | ❓ | Ambiguous or incomplete inputs |
| **PremiseValidatorAgent** | Trick Question & False Premise Detection | 🕵️ | Misleading inputs, false presuppositions |
| **EvidenceRetrieverAgent** | Multi-Source Knowledge Retrieval | 📚 | Factual, conflicting, and research tasks |
| **ClaimExtractorAgent** | Atomic Proposition Extraction | 🔬 | When candidate text requires claim audit |
| **FactVerifierAgent** | Claim-to-Evidence Grounding | ✅ | When atomic claims are extracted |
| **ContradictionDetectorAgent** | Conflict & Opposing View Detection | ⚡ | Multi-source claims & contested facts |
| **HallucinationDetectorAgent** | Fabricated Citations & Fictional Entities | 👻 | Unverified entities, speculative claims |
| **CodeSandboxAgent** | Python AST & Isolated Execution | 💻 | Tasks containing code generation/debugging |
| **SafetyRiskAgent** | Cyberattack & Threat Guardrail | 🛡️ | High-risk prompts, destructive commands |
| **ConsistencyReasoningAgent** | Deductive Validity & Proof Checker | 🧠 | Multi-step mathematical or logical claims |
| **SelfCorrectionAgent** | Autonomous Refinement & Patching | 🔄 | When verification score fails threshold |
| **PassportSynthesisAgent** | Cryptographic Passport Generation | 🛂 | Task finalization |
| **AuditLoggerAgent** | Telemetry & Database Persistence | 📝 | Continuous async logging |

---

## 2. Detailed Agent Specifications

### 2.1 PlannerAgent
- **Icon**: 🧭
- **Role**: Constructs the dynamic execution Directed Acyclic Graph (DAG), schedules parallel checker tasks, tracks execution milestones, and handles global execution timeouts.
- **Input Types**: `TaskRequest(id: UUID, input_text: str, context: Optional[dict])`
- **Output Types**: `ExecutionPlan(task_id: UUID, steps: List[ExecutionStep], timeout_seconds: int)`
- **Core Logic**:
  1. Inspects the classification emitted by `QueryClassifierAgent`.
  2. Dynamically prunes unnecessary pipeline stages (e.g. bypasses code execution for factual queries; bypasses evidence search for code).
  3. Maps dependency relationships and parallel execution groups.
  4. Dispatches asynchronous worker jobs to the execution queue.
- **Activation**: Mandatory. Activated at Step 0 of every incoming verification request.

---

### 2.2 QueryClassifierAgent
- **Icon**: 🔍
- **Role**: Performs deep semantic analysis, detecting user intent, domain category, entity density, and vulnerability surface.
- **Input Types**: `QueryInput(text: str)`
- **Output Types**: `ClassificationResult(task_type: TaskType, confidence: float, features: QueryFeatures)`
- **Core Logic**:
  1. Analyzes grammatical completeness, subject presence, and interrogative focus.
  2. Applies pattern classifiers for programming languages, dangerous keywords (e.g., `rm -rf`, `DROP TABLE`), and comparative queries.
  3. Assigns one of eight primary categories: `factual`, `ambiguous`, `incomplete`, `conflicting`, `misleading`, `hallucination`, `coding`, or `security_risk`.
- **Activation**: Mandatory. Invoked immediately following task ingestion.

---

### 2.3 ClarificationAgent
- **Icon**: ❓
- **Role**: Intercepts underspecified, vague, or missing-variable prompts, preventing the system from guessing or fabricating missing context.
- **Input Types**: `AmbiguityContext(text: str, detected_gaps: List[str])`
- **Output Types**: `ClarificationResponse(needs_clarification: bool, clarification_questions: List[str], missing_parameters: List[str])`
- **Core Logic**:
  1. Detects missing mathematical equations (e.g. "Solve for x"), undefined software stacks ("Fix the bug"), or missing benchmark targets ("Which is faster?").
  2. Generates structured, numbered questions specifying exactly what variables the user must provide.
  3. Short-circuits the pipeline with a `NEEDS_CLARIFICATION` final decision, saving tokens and compute.
- **Activation**: Activated whenever `QueryClassifierAgent` tags task as `ambiguous` or `incomplete`.

---

### 2.4 PremiseValidatorAgent
- **Icon**: 🕵️
- **Role**: Scrutinizes input queries and generated text for false presuppositions, counter-factual assumptions, and trick questions (e.g. "Moses illusion").
- **Input Types**: `PremiseInput(query: str, proposed_answer: Optional[str])`
- **Output Types**: `PremiseValidationResult(is_valid: bool, flawed_premises: List[str], corrective_context: str)`
- **Core Logic**:
  1. Extracts underlying presuppositions ($P \implies Q$).
  2. Cross-references assumptions against common myth corpora and ground truth facts (e.g., "Great Wall visible from space" $\to$ False; "Humans use 10% of brain" $\to$ False).
  3. If flawed, instructs the pipeline to reject the presupposition and provide the factual correction rather than answering under the false premise.
- **Activation**: Activated for tasks categorized as `misleading`, trick questions, or common myth queries.

---

### 2.5 EvidenceRetrieverAgent
- **Icon**: 📚
- **Role**: Multi-source knowledge retrieval orchestrator that gathers authoritative corroborating and refuting evidence snippets.
- **Input Types**: `RetrievalQuery(claims: List[str], max_sources: int = 5)`
- **Output Types**: `EvidenceCollection(evidence_items: List[EvidenceItem])`
- **Core Logic**:
  1. Formulates optimized search queries and boolean keyword operators.
  2. Queries Wikipedia API, academic indices, and curated offline knowledge bases.
  3. Evaluates source reliability scores (e.g., peer-reviewed / official docs = 1.0, general web = 0.7, unverified blog = 0.3).
  4. Returns text passages with exact citation timestamps and URLs.
- **Activation**: Activated for all `factual`, `conflicting`, and research-oriented verification workflows.

---

### 2.6 ClaimExtractorAgent
- **Icon**: 🔬
- **Role**: Deconstructs complex synthetic text into atomic, falsifiable propositions that can be verified in isolation.
- **Input Types**: `TextPayload(text: str)`
- **Output Types**: `ClaimsManifest(claims: List[AtomicClaim])`
- **Core Logic**:
  1. Breaks text down using dependency parsing and discourse parsing.
  2. Converts complex compound sentences into simple independent propositions (Subject, Predicate, Object, Temporal/Spatial anchors).
  3. Assigns unique identifiers (`CLM-001`, `CLM-002`, etc.) and tags categories (`numerical`, `historical`, `scientific`, `definitional`).
- **Activation**: Activated prior to verification checkers whenever a candidate answer requires validation.

---

### 2.7 FactVerifierAgent
- **Icon**: ✅
- **Role**: Matches extracted atomic claims against retrieved evidence to compute probabilistic truth support.
- **Input Types**: `VerificationBatch(claims: List[AtomicClaim], evidence: List[EvidenceItem])`
- **Output Types**: `VerificationReport(results: List[ClaimVerificationResult], aggregate_factual_score: float)`
- **Core Logic**:
  1. Computes Natural Language Inference (NLI) entailment between each claim and relevant evidence passages.
  2. Labels each claim as `SUPPORTED`, `CONTRADICTED`, or `UNVERIFIED`.
  3. Weights claims based on centrality to the overall text.
- **Activation**: Core verification agent. Activated whenever claims and evidence are present.

---

### 2.8 ContradictionDetectorAgent
- **Icon**: ⚡
- **Role**: Detects direct factual contradictions between multiple external sources or internal logical conflicts within the candidate answer.
- **Input Types**: `ContradictionInput(claims: List[AtomicClaim], evidence: List[EvidenceItem])`
- **Output Types**: `ContradictionReport(has_contradiction: bool, conflicting_pairs: List[ConflictPair], severity: str)`
- **Core Logic**:
  1. Compares mutual compatibility between pairs of claims ($C_i \land \neg C_j$).
  2. Analyzes disputed topics where scientific consensus is split or historical measurement methodologies diverged (e.g. Everest height pre-2020).
  3. Flags issues as `WARNING` or triggers `SelfCorrectionAgent` to present both perspectives neutrally.
- **Activation**: Activated for tasks tagged as `conflicting` or when multi-source evidence divergence exceeds 30%.

---

### 2.9 HallucinationDetectorAgent
- **Icon**: 👻
- **Role**: Specialized entity hunter that catches non-existent individuals, invented citations, fictitious standards, or anachronistic events.
- **Input Types**: `CandidateVerificationInput(text: str, named_entities: List[str])`
- **Output Types**: `HallucinationReport(hallucination_detected: bool, fabricated_entities: List[str], confidence_penalty: float)`
- **Core Logic**:
  1. Extracts all named entities (Persons, Organizations, Standards, Publications, Dates).
  2. Validates entities against entity registries (Crossref, DOI, IEEE, Wikidata).
  3. Detects anachronistic claims (e.g., Einstein publishing in 1968) and nonexistent standards (e.g. IEEE 9999.88).
  4. Imposes immediate 40% confidence degradation penalty if hallucinations are ungrounded.
- **Activation**: Activated for all high-risk generation and queries flagged as hallucination-prone.

---

### 2.10 CodeSandboxAgent
- **Icon**: 💻
- **Role**: Static AST analyzer and secure runtime sandbox for programmatic verification of code snippets.
- **Input Types**: `CodeVerificationRequest(code: str, language: str, test_assertions: List[str])`
- **Output Types**: `CodeExecutionResult(syntax_valid: bool, security_cleared: bool, tests_passed: int, total_tests: int, stdout: str, stderr: str)`
- **Core Logic**:
  1. **Static AST Analysis**: Walks the Python Abstract Syntax Tree to block dangerous imports (`os.system`, `subprocess`, `ctypes`, `shutil.rmtree`, `socket`).
  2. **Isolated Execution**: Executes code in an ephemeral subprocess with CPU time limits (3s max) and memory ceilings (128MB).
  3. **Assertion Verification**: Appends and executes unit tests (e.g. edge cases, empty arrays, zero inputs) and records outcomes to `tool_tests`.
- **Activation**: Mandatory for tasks with `task_type == "coding"` or snippets containing executable scripts.

---

### 2.11 SafetyRiskAgent
- **Icon**: 🛡️
- **Role**: Enforces non-negotiable security guardrails, blocking malware generation, destructive sysadmin commands, injection exploits, and cyberattacks.
- **Input Types**: `SafetyScanRequest(input_text: str, candidate_output: str)`
- **Output Types**: `SafetyScanResult(is_safe: bool, risk_level: str, violation_categories: List[str], mitigation_action: str)`
- **Core Logic**:
  1. Scans against OWASP Top 10 for LLMs, MITRE ATT&CK patterns, and destructive command regexes.
  2. Identifies dangerous payloads such as `rm -rf /`, `DROP DATABASE`, ransomware routines, and password-stealing keyloggers.
  3. Instantly marks the task for `REJECT` decision and prevents downstream execution.
- **Activation**: Activated at pre-flight and post-generation for all tasks.

---

### 2.12 ConsistencyReasoningAgent
- **Icon**: 🧠
- **Role**: Validates formal deductive reasoning, step-by-step mathematical proofs, and logical transitions.
- **Input Types**: `ReasoningTrace(steps: List[str])`
- **Output Types**: `ReasoningAuditResult(is_sound: bool, invalid_steps: List[int], explanation: str)`
- **Core Logic**:
  1. Evaluates each deduction step against propositional logic axioms.
  2. Verifies intermediate mathematical calculations (arithmetic, linear algebra, combinatorial bounds).
  3. Detects non-sequiturs, circular reasoning, and mathematical hallucination.
- **Activation**: Activated for complex mathematical, algorithmic, and analytical reasoning queries.

---

### 2.13 SelfCorrectionAgent
- **Icon**: 🔄
- **Role**: Autonomous refinement engine that repairs responses failing verification criteria without human intervention.
- **Input Types**: `CorrectionRequest(original_answer: str, failed_checks: List[VerificationResult], evidence: List[EvidenceItem], iteration: int)`
- **Output Types**: `CorrectionResponse(corrected_answer: str, changes_applied: List[str], converged: bool)`
- **Core Logic**:
  1. Strips ungrounded claims and replaces them with evidence-backed formulations.
  2. Replaces false premises with factual historical/scientific context.
  3. Inserts nuancing disclaimers for conflicting evidence topics.
  4. Saves refinement diff to `corrections` table and triggers re-verification.
- **Activation**: Activated dynamically when aggregate verification score $S < 0.85$ and iteration count $< 3$.

---

### 2.14 PassportSynthesisAgent
- **Icon**: 🛂
- **Role**: Assembles the immutable, cryptographically verifiable Verification Passport documenting the final decision, claim scores, checker outcomes, and provenance stamps.
- **Input Types**: `PassportAssemblyInput(task_id: UUID, final_text: str, all_results: List[VerificationResult], claims: List[AtomicClaim])`
- **Output Types**: `VerificationPassport(passport_id: UUID, decision: DecisionEnum, confidence: float, passport_hash: str, stamps: dict)`
- **Core Logic**:
  1. Compiles all checker status badges (`PASS`, `WARNING`, `FAIL`).
  2. Computes the final confidence score and decision badge (`ACCEPT`, `CORRECTED`, `WARNING`, `NEEDS_CLARIFICATION`, `REJECT`).
  3. Computes a SHA-256 integrity hash across input, output, evidence IDs, and checker outcomes.
  4. Formats passport JSON for client rendering.
- **Activation**: Terminal stage. Executed for every successfully finalized task.

---

### 2.15 AuditLoggerAgent
- **Icon**: 📝
- **Role**: Persists all intermediate states, tool test logs, agent run timings, and provenance events to Supabase PostgreSQL.
- **Input Types**: `AuditRecord(task_id: UUID, payload: dict)`
- **Output Types**: `AuditConfirmation(success: bool, record_id: UUID)`
- **Core Logic**:
  1. Captures timestamped events for every agent start and finish.
  2. Writes normalized JSONB payloads into `agent_runs`, `audit_log`, `claims`, and `verification_results`.
  3. Ensures complete compliance with auditability standards.
- **Activation**: Continuous background listener across the pipeline lifecycle.
