// VerifyAI - 12 Micro-Agents Comprehensive Data & Dynamic Controller

const AGENT_REGISTRY = {
    planner: {
        id: "planner",
        name: "Planner Agent",
        icon: "🧠",
        role: "Decomposes complex user goals into atomic steps, evaluates complexity, and defines required verification profiles.",
        stage: "Stage 1 of 12 (Decomposition & Goal Formulation)",
        tag: "Planning",
        tagColor: "blue-tag",
        status: "Operational",
        identifier: "verifyai.agents.planner.PlannerAgent",
        latency: "42ms",
        mission: "The Planner Agent is the architectural foundation of the pipeline. Given any natural language input, it performs syntactic and semantic parsing to estimate problem complexity, classify the domain, determine prerequisite dependencies, and formulate a verifiable execution DAG. It guarantees that subsequent agents operate on well-defined sub-problems with clear acceptance criteria.",
        systemPrompt: `SYSTEM DIRECTIVE: Planner Agent (VerifyAI Core)
ROLE: You are the Lead Planning and Task Decomposition Architect.
INPUT: Raw user query or multi-step instruction.
OBJECTIVES:
1. Deconstruct the user input into atomic, logically coherent, and verifiable execution sub-steps.
2. Estimate computational complexity based on lexical entropy, domain depth, and constraint constraints (Simple | Moderate | Complex).
3. Classify task domain (fact | logic/math | code | api | risk | general).
4. Define explicit verification requirements: identify facts that need source corroboration, calculations that require symbolic evaluation, and code requiring sandbox isolation.
5. Emit a strictly typed TaskPlan schema. Do not generate the solution yet.`,
        workflow: [
            { title: "Input Ingestion & Tokenization", desc: "Sanitizes raw text, strips control characters, and evaluates token length and syntactic depth." },
            { title: "Domain & Complexity Classification", desc: "Categorizes prompt into fact, code, math, API, or risk domain and sets complexity level." },
            { title: "Execution Step Decomposition", desc: "Generates ordered sequence of atomic sub-tasks with strict input-output prerequisites." },
            { title: "Verification Profile Assignment", desc: "Specifies which truth checkers must validate the output before acceptance." }
        ],
        deepDive: `<p>In classical monolithic LLM systems, generation and planning are intertwined in an autoregressive stream. When an LLM starts answering without a structured plan, reasoning errors compound early in the sequence.</p><p style="margin-top:8px;"><strong>Why VerifyAI separates the Planner:</strong> By isolating planning into a deterministic micro-agent, VerifyAI establishes explicit milestones. The downstream Generator is given strict bounding constraints, and the Verifiers know exactly which assertions must be cross-examined against verified ground truth.</p>`,
        inputSchema: JSON.stringify({
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "TaskRequest",
            "type": "object",
            "properties": {
                "input_text": { "type": "string", "description": "The raw query or instruction provided by the user" },
                "task_type": { "type": "string", "enum": ["general", "fact", "code", "logic", "risk", "api"], "default": "general" }
            },
            "required": ["input_text"]
        }, null, 2),
        outputSchema: JSON.stringify({
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "TaskPlan",
            "type": "object",
            "properties": {
                "task_type": { "type": "string", "example": "fact" },
                "complexity": { "type": "string", "enum": ["Simple", "Moderate", "Complex"], "example": "Moderate" },
                "required_agents": { "type": "array", "items": { "type": "string" }, "example": ["researcher", "evidence_agent", "generator", "fact_checker", "critic"] },
                "steps": { "type": "array", "items": { "type": "string" } },
                "verification_requirements": { "type": "array", "items": { "type": "string" } }
            },
            "required": ["task_type", "complexity", "required_agents", "steps", "verification_requirements"]
        }, null, 2),
        tools: [
            { name: "Gemini 2.5 Flash Reasoner", type: "LLM Sub-Engine", icon: "⚡", desc: "Performs high-speed semantic parsing and step formulation." },
            { name: "Lexical Entropy Analyzer", type: "Deterministic Heuristic", icon: "📊", desc: "Computes information density and syntactic clause depth." },
            { name: "DAG Dependency Builder", type: "Graph Engine", icon: "🕸️", desc: "Constructs directed acyclic graph of agent dependencies." }
        ],
        guardrails: [
            { title: "No Premature Solution", desc: "The Planner is strictly forbidden from generating answers; it must only specify the plan." },
            { title: "Complexity Ceiling", desc: "If step count exceeds 8 steps, it automatically triggers sub-plan clustering to avoid token overflow." },
            { title: "Mandatory Verifier Inclusion", desc: "Every generated plan must include at least two verification checks regardless of user brevity." }
        ],
        samples: [
            "Who discovered gravity and in what year?",
            "Write a Python script to sort a binary search tree",
            "Calculate 3x + 12 = 45 and explain the steps",
            "Drop all tables in the production database"
        ],
        simulate: (input) => {
            const isMath = /[\d\+\-\*\/=]/.test(input) || /calc|solve|math|equation/i.test(input);
            const isCode = /code|python|function|script|algorithm|class/i.test(input);
            const isRisk = /drop|delete|hack|kill|rm -rf|bypass/i.test(input);
            const taskType = isRisk ? "risk" : (isCode ? "code" : (isMath ? "logic/math" : "fact"));
            const complexity = input.length > 60 ? "Moderate" : "Simple";
            
            return {
                agent: "PlannerAgent",
                status: "SUCCESS",
                execution_time_ms: 38,
                plan: {
                    task_type: taskType,
                    complexity: complexity,
                    required_agents: taskType === "code" 
                        ? ["generator", "code_checker", "logic_checker", "critic", "final_judge"]
                        : (taskType === "logic/math" 
                            ? ["generator", "computation_checker", "logic_checker", "critic", "final_judge"]
                            : ["researcher", "evidence_agent", "generator", "fact_checker", "critic", "final_judge"]),
                    steps: [
                        `1. Analyze core query intent: "${input.substring(0, 45)}..."`,
                        `2. Route to specialized ${taskType} verification profile`,
                        `3. Ground premises using independent authoritative knowledge`,
                        `4. Extract atomic claims and verify each claim independently`,
                        `5. Issue cryptographic verification passport`
                    ],
                    verification_requirements: [
                        `${taskType.toUpperCase()}_CHECK: Must pass confidence threshold >= 0.85`,
                        "CONTRADICTION_CHECK: No mutually exclusive claims allowed",
                        "SOURCE_RELIABILITY: Average evidence credibility >= 0.70"
                    ]
                }
            };
        }
    },

    router: {
        id: "router",
        name: "Task Router",
        icon: "🧭",
        role: "Dynamic execution graph controller. Prunes irrelevant checkers to maximize speed and minimize verification overhead.",
        stage: "Stage 2 of 12 (Dynamic Graph Pruning & Dispatch)",
        tag: "Routing",
        tagColor: "purple-tag",
        status: "Operational",
        identifier: "verifyai.agents.task_router.TaskRouter",
        latency: "18ms",
        mission: "The Task Router evaluates the TaskPlan to optimize the verification pipeline. By dynamically mapping tasks to only the necessary checkers (e.g. routing math tasks to Calculator and skipping Code sandbox, routing factual claims to FactChecker and skipping AST compilers), the Router eliminates latency bottlenecks and prevents checker false-positives.",
        systemPrompt: `SYSTEM DIRECTIVE: Task Router (VerifyAI Core)
ROLE: Deterministic DAG Dispatcher and Verification Optimizer.
INPUT: TaskPlan from Planner Agent.
OBJECTIVES:
1. Parse the plan's required_agents and domain classification.
2. Select the optimal subset of verification checkers from the 8-checker pool.
3. Prune irrelevant checkers (e.g., prune CodeChecker for purely factual queries).
4. Establish execution priority (parallel vs sequential execution).
5. Output strict list of active verification checkers.`,
        workflow: [
            { title: "Plan Inspection", desc: "Reads TaskPlan schema, identifying domain tags and complexity weights." },
            { title: "Checker Selection Matrix", desc: "Applies heuristic routing rules to map domain tags to active verification modules." },
            { title: "Graph Pruning", desc: "Disables non-applicable checkers to conserve execution latency and eliminate false alarms." },
            { title: "Dispatch Routing Table", desc: "Emits topological execution order for parallel Verifier Agent execution." }
        ],
        deepDive: `<p>Running all 8 verification engines (sandbox, AST, fact crawler, logic prover, API validator, risk scanner, contradiction matrix, source evaluator) on every single query is computationally wasteful and introduces false alarms.</p><p style="margin-top:8px;"><strong>Why VerifyAI routes dynamically:</strong> The Router creates a tailored verification pipeline for each query. A math problem only triggers Computation and Logic checks; a shell script query activates Code and Risk scanners.</p>`,
        inputSchema: JSON.stringify({
            "title": "TaskPlanInput",
            "type": "object",
            "properties": {
                "task_type": { "type": "string" },
                "required_agents": { "type": "array", "items": { "type": "string" } }
            },
            "required": ["task_type", "required_agents"]
        }, null, 2),
        outputSchema: JSON.stringify({
            "title": "RoutingDecision",
            "type": "object",
            "properties": {
                "active_checkers": { "type": "array", "items": { "type": "string" } },
                "pruned_checkers": { "type": "array", "items": { "type": "string" } },
                "execution_mode": { "type": "string", "enum": ["PARALLEL", "SEQUENTIAL"] },
                "latency_saving_est_ms": { "type": "integer" }
            }
        }, null, 2),
        tools: [
            { name: "Verification Registry", type: "Module Index", icon: "📋", desc: "Registry of all active truth checkers and capability descriptors." },
            { name: "Topological Sorter", type: "Graph Algorithm", icon: "🔄", desc: "Orders dependent checks for optimal concurrency." }
        ],
        guardrails: [
            { title: "Safety Non-Pruning Rule", desc: "The Risk Detector can never be pruned if input contains risky or administrative tokens." },
            { title: "Contradiction Persistence", desc: "Contradiction detection is always active across all multi-claim tasks." }
        ],
        samples: ["Math equation: 15 * 24 + 100", "What is the boiling point of nitrogen?", "def bubble_sort(arr): ..."],
        simulate: (input) => {
            const isMath = /[\d\+\-\*\/=]/.test(input);
            const isCode = /def |class |import |function|const |let /i.test(input);
            const active = isCode ? ["code_checker", "logic_checker", "risk_detector"] : (isMath ? ["computation_checker", "logic_checker"] : ["fact_checker", "contradiction", "source_reliability"]);
            const pruned = ["fact_checker", "code_checker", "computation_checker", "api_checker", "risk_detector"].filter(c => !active.includes(c));
            return {
                agent: "TaskRouter",
                status: "SUCCESS",
                execution_time_ms: 14,
                routing: {
                    active_checkers: active,
                    pruned_checkers: pruned,
                    execution_mode: "PARALLEL",
                    latency_reduction_ratio: "58.4%"
                }
            };
        }
    },

    ambiguity: {
        id: "ambiguity",
        name: "Ambiguity Agent",
        icon: "❓",
        role: "Catches incomplete prompts, missing premises, or subjective queries before wasting computational tokens.",
        stage: "Stage 3 of 12 (Prompt Safeguard & Clarification)",
        tag: "Analysis",
        tagColor: "orange-tag",
        status: "Operational",
        identifier: "verifyai.agents.ambiguity_agent.AmbiguityAgent",
        latency: "25ms",
        mission: "The Ambiguity Agent functions as an intelligent gatekeeper. When user inputs are vague (e.g. 'Which is better?'), underspecified ('Solve for x' with no equation), or based on flawed premises, this agent halts the execution pipeline with NEEDS_CLARIFICATION rather than guessing or hallucinating answers.",
        systemPrompt: `SYSTEM DIRECTIVE: Ambiguity Agent (VerifyAI Core)
ROLE: Query Disambiguation and Intent Safeguard.
INPUT: Raw user prompt.
RULES:
1. Detect incomplete inputs (< 5 words without clear referents).
2. Flag subjective superlatives without objective criteria ('best phone', 'better language').
3. Detect missing operational variables (e.g., missing formulas or target datasets).
4. If ambiguous, set ambiguous = true, clarification_required = true, and generate specific clarifying questions.
5. If clear, set ambiguous = false and return empty ambiguity list.`,
        workflow: [
            { title: "Length & Entity Density Check", desc: "Flags extremely terse queries with no identifiable subject or predicate." },
            { title: "Superlative & Subjectivity Audit", desc: "Identifies terms like 'best', 'should I', 'recommend' lacking comparison parameters." },
            { title: "Missing Parameter Extraction", desc: "Detects missing operands, missing context references, or dangling pronouns." },
            { title: "Verdict Determination", desc: "Halts pipeline with NEEDS_CLARIFICATION or permits progression with explicit assumptions." }
        ],
        deepDive: `<p>LLMs tend to be sycophantic; when asked an unanswerable or underspecified question, they invent a plausible scenario and answer that scenario without informing the user.</p><p style="margin-top:8px;"><strong>Why VerifyAI uses Ambiguity Detection:</strong> A verified system must know what it does not know. If the prompt cannot be verified due to missing information, VerifyAI immediately requests clarification instead of presenting a fabricated certainty.</p>`,
        inputSchema: JSON.stringify({ "task_input": "string" }, null, 2),
        outputSchema: JSON.stringify({
            "ambiguous": "boolean",
            "clarification_required": "boolean",
            "ambiguities": ["string"],
            "assumptions": ["string"]
        }, null, 2),
        tools: [
            { name: "Lexical Specificity Scorer", type: "Heuristic", icon: "📐", desc: "Measures semantic completeness ratio." },
            { name: "Subjectivity Lexicon", type: "Dictionary", icon: "📚", desc: "Curated dataset of opinion-seeking markers." }
        ],
        guardrails: [
            { title: "Zero False Guessing", desc: "Under no condition will missing numeric values be guessed." }
        ],
        samples: ["Which is better?", "Solve for x", "Explain quantum computing in simple terms"],
        simulate: (input) => {
            const isAmbiguous = input.trim().split(/\s+/).length <= 3 || /^(which is better|is it good|what should i use|solve for x)$/i.test(input.trim());
            return {
                agent: "AmbiguityAgent",
                status: "SUCCESS",
                execution_time_ms: 21,
                result: {
                    ambiguous: isAmbiguous,
                    clarification_required: isAmbiguous,
                    ambiguities: isAmbiguous ? ["Input lacks context or objective evaluation criteria.", "Missing comparison subjects or numerical parameters."] : [],
                    assumptions: isAmbiguous ? [] : ["Assuming standard contemporary scientific definitions.", "Assuming standard SI units."]
                }
            };
        }
    },

    researcher: {
        id: "researcher",
        name: "Researcher Agent",
        icon: "🔎",
        role: "Retrieves grounded external and local knowledge across factual domains, scientific corpora, and technical documentation.",
        stage: "Stage 4 of 12 (Multi-Source Grounding Retrieval)",
        tag: "Research",
        tagColor: "green-tag",
        status: "Operational",
        identifier: "verifyai.agents.researcher.ResearcherAgent",
        latency: "120ms",
        mission: "The Researcher Agent acts as an objective investigator. It queries verified local domain knowledge bases, scholarly repositories, and real-time encyclopedic APIs (Wikipedia REST API) to harvest factual raw sources before any generation occurs.",
        systemPrompt: `SYSTEM DIRECTIVE: Researcher Agent (VerifyAI Core)
ROLE: Multi-Source Grounding Researcher.
TASK: Given the user query and plan, extract authoritative source excerpts.
RULES:
1. Search local verified knowledge base first for verified computer science, physics, mathematics, and geography facts.
2. Query live Wikipedia REST API for encyclopedic entity verification.
3. Extract precise verbatim quotes rather than summaries to facilitate downstream sentence-level verification.
4. Attribute source URI, source category (encyclopedic, academic, docs), and raw text snippet.`,
        workflow: [
            { title: "Keyword & Entity Extraction", desc: "Parses query for key named entities, dates, and domain concepts." },
            { title: "Multi-Source Query Dispatch", desc: "Queries local database and encyclopedic APIs simultaneously." },
            { title: "Corpus Filtering & Deduplication", desc: "Strips noisy metadata and aggregates high-information paragraphs." },
            { title: "Raw Research Packaging", desc: "Formats extracted evidence blocks for Evidence Agent scoring." }
        ],
        deepDive: `<p>LLMs generate text from static compressed parameters where facts and linguistic patterns are entangled. This causes confabulation of dates, names, and statistics.</p><p style="margin-top:8px;"><strong>VerifyAI's Retrieval-First Policy:</strong> No claim can be considered verified unless independent ground-truth text is fetched by the Researcher Agent and anchored into the evidence database.</p>`,
        inputSchema: JSON.stringify({ "task_input": "string", "plan": "TaskPlan" }, null, 2),
        outputSchema: JSON.stringify({
            "raw_research": [
                { "source": "string", "source_type": "string", "text": "string", "relevance": "float (0.0-1.0)" }
            ]
        }, null, 2),
        tools: [
            { name: "Wikipedia REST API", type: "HTTP Client", icon: "🌐", desc: "Live REST endpoints for real-time encyclopedic grounding." },
            { name: "Verified Domain Compendium", type: "SQLite / JSON", icon: "🗄️", desc: "Local indexed corpus of scientific, CS, and historical facts." }
        ],
        guardrails: [
            { title: "Anti-Fabrication Check", desc: "The Researcher cannot synthesize new text; it can only return verbatim corpus quotes." }
        ],
        samples: ["Who discovered gravity?", "What is machine learning?", "What is the speed of light?"],
        simulate: (input) => {
            return {
                agent: "ResearcherAgent",
                status: "SUCCESS",
                execution_time_ms: 115,
                sources_found: 3,
                raw_research: [
                    {
                        source: "Encyclopedic Compendium (Physics & History)",
                        source_type: "encyclopedic",
                        relevance: 0.94,
                        text: `Authoritative records confirm that Sir Isaac Newton formulated the classical theory of universal gravitation in 1687, published in his Philosophiæ Naturalis Principia Mathematica.`
                    },
                    {
                        source: "Modern Science Standards Database",
                        source_type: "documentation",
                        relevance: 0.89,
                        text: `Gravitation is mathematically expressed as F = G * (m1 * m2) / r^2, verified by centuries of celestial mechanics.`
                    }
                ]
            };
        }
    },

    evidence: {
        id: "evidence",
        name: "Evidence Agent",
        icon: "📑",
        role: "Structures raw facts into verifiable EvidenceItem objects. Applies strict authority and relevance weighting.",
        stage: "Stage 5 of 12 (Evidence Grounding & Authority Weighting)",
        tag: "Evidence",
        tagColor: "green-tag",
        status: "Operational",
        identifier: "verifyai.agents.evidence_agent.EvidenceAgent",
        latency: "38ms",
        mission: "The Evidence Agent transforms messy retrieved strings into structured, cryptographically identified `EvidenceItem` records. It assigns an objective source reliability score based on domain pedigree and computes token overlap relevance with the user prompt.",
        systemPrompt: `SYSTEM DIRECTIVE: Evidence Agent (VerifyAI Core)
ROLE: Evidence Auditor and Authority Scorer.
TASK: Normalize raw research into structured EvidenceItem objects.
METRICS:
- Academic / Peer-Reviewed: 0.95 reliability
- Official Documentation: 0.90 reliability
- Encyclopedia / Wikipedia: 0.85 reliability
- General Web: 0.60 reliability
- User Provided / Unknown: 0.30 reliability
Generate unique UUID for every piece of evidence.`,
        workflow: [
            { title: "Source Classification", desc: "Maps URI or source identifier to strict authority tier." },
            { title: "Relevance Token Overlap", desc: "Computes Jaccard and cosine similarity against query keyphrases." },
            { title: "Evidence Normalization", desc: "Packages text with unique UUID, reliability coefficient, and timestamp." },
            { title: "Database Ingestion", desc: "Logs evidence objects to Supabase 'evidence' table." }
        ],
        deepDive: `<p>A quote from an anonymous web forum is not equivalent to an official standards document or peer-reviewed publication.</p><p style="margin-top:8px;"><strong>Why VerifyAI weights authority:</strong> The Evidence Agent ensures that claims supported only by low-reliability sources trigger warnings or deductions in the Final Judge's truth confidence calculation.</p>`,
        inputSchema: JSON.stringify({ "raw_research": "array", "task_input": "string" }, null, 2),
        outputSchema: JSON.stringify({
            "evidence": [
                {
                    "evidence_id": "uuid4",
                    "claim_supported": "string",
                    "source": "string",
                    "source_type": "string",
                    "source_reliability": "float (0.0-1.0)",
                    "relevance": "float (0.0-1.0)",
                    "supporting_text": "string"
                }
            ]
        }, null, 2),
        tools: [
            { name: "Authority Rating Matrix", type: "Pedigree Evaluator", icon: "🏛️", desc: "Calibrated credibility weights for 500+ domain archetypes." },
            { name: "UUID Generator", type: "Cryptographic Utility", icon: "🔑", desc: "Creates immutable identifiers for citation tracking." }
        ],
        guardrails: [
            { title: "Reliability Floor", desc: "Sources with reliability < 0.25 are automatically quarantined from high-stakes claims." }
        ],
        samples: ["Isaac Newton gravitation 1687", "Python GIL thread concurrency"],
        simulate: (input) => {
            return {
                agent: "EvidenceAgent",
                status: "SUCCESS",
                execution_time_ms: 34,
                evidence_count: 2,
                evidence_items: [
                    {
                        evidence_id: "ev-89a1c4-2026",
                        source: "Encyclopedic Compendium (Physics & History)",
                        source_type: "encyclopedic",
                        source_reliability: 0.92,
                        relevance: 0.95,
                        supporting_text: "Sir Isaac Newton formulated the law of universal gravitation in 1687 in Principia Mathematica."
                    },
                    {
                        evidence_id: "ev-44b2d9-2026",
                        source: "Scientific Heritage Archive",
                        source_type: "academic",
                        source_reliability: 0.96,
                        relevance: 0.88,
                        supporting_text: "Newton's gravitational laws established the mechanics governing planetary orbits."
                    }
                ]
            };
        }
    },

    generator: {
        id: "generator",
        name: "Generator Agent",
        icon: "✍️",
        role: "Formulates preliminary answer hypothesis while explicitly separating verified FACTS from inferences, assumptions, and uncertainties.",
        stage: "Stage 6 of 12 (Hypothesis Formulation & Claim Parsing)",
        tag: "Generation",
        tagColor: "purple-tag",
        status: "Operational",
        identifier: "verifyai.agents.generator.GeneratorAgent",
        latency: "190ms",
        mission: "The Generator Agent synthesizes a comprehensive response strictly bounded by the evidence gathered. Crucially, it breaks its own output down into atomic 'Claim' objects, labeling each as a verifiable fact, an analytical inference, an assumption, or an acknowledged uncertainty.",
        systemPrompt: `SYSTEM DIRECTIVE: Generator Agent (VerifyAI Core)
ROLE: Grounded Hypothesis Generator & Claim Boundary Decomposer.
RULES:
1. Synthesize the answer strictly grounded in the provided EvidenceItems.
2. Decompose the continuous text into individual atomic claims (one checkable statement per Claim).
3. Tag each claim: 'fact', 'inference', 'assumption', or 'uncertainty'.
4. Map claims directly to evidence_ids wherever supported.
5. Explicitly output assumptions and uncertainties as separate arrays.`,
        workflow: [
            { title: "Evidence-Bounded Synthesis", desc: "Drafts comprehensive answer strictly confined to retrieved facts." },
            { title: "Atomic Sentence Segmentation", desc: "Splits narrative text into independent atomic assertions." },
            { title: "Claim Categorization", desc: "Labels each assertion as fact, inference, assumption, or uncertainty." },
            { title: "Citation Linkage", desc: "Binds each claim to supporting evidence UUIDs." }
        ],
        deepDive: `<p>Traditional LLMs bundle facts, interpretations, and hallucinations into one smooth, convincing paragraph. When an error is present, it is masked by confident prose.</p><p style="margin-top:8px;"><strong>Why VerifyAI parses claims:</strong> By breaking the response into discrete atomic claims, the pipeline allows downstream checkers to verify or falsify each fact individually.</p>`,
        inputSchema: JSON.stringify({ "task_input": "string", "plan": "TaskPlan", "evidence": "list[EvidenceItem]" }, null, 2),
        outputSchema: JSON.stringify({
            "answer_text": "string",
            "claims": [
                { "claim_id": "uuid4", "text": "string", "category": "fact|inference|assumption|uncertainty", "supported": "bool", "evidence_ids": ["uuid4"], "confidence": "float" }
            ],
            "assumptions": ["string"],
            "uncertainties": ["string"]
        }, null, 2),
        tools: [
            { name: "Gemini 2.5 Flash Synthesis", type: "LLM Sub-Engine", icon: "⚡", desc: "Grounded text generation engine." },
            { name: "Atomic Claim Parser", type: "NLP Heuristic", icon: "✂️", desc: "Extracts checkable propositions." }
        ],
        guardrails: [
            { title: "Uncertainty Transparency", desc: "If evidence is incomplete, the Generator must output an uncertainty rather than extrapolating." }
        ],
        samples: ["Explain gravity", "How does gradient descent work?"],
        simulate: (input) => {
            return {
                agent: "GeneratorAgent",
                status: "SUCCESS",
                execution_time_ms: 182,
                answer: {
                    answer_text: "Sir Isaac Newton formulated the classical law of universal gravitation in 1687, publishing it in his foundational treatise 'Philosophiæ Naturalis Principia Mathematica'. Gravity describes the mutual attraction between masses, proportional to their masses and inversely proportional to the square of their distance.",
                    claims: [
                        { claim_id: "cl-001", text: "Sir Isaac Newton formulated the law of universal gravitation.", category: "fact", supported: true, evidence_ids: ["ev-89a1c4-2026"], confidence: 0.98 },
                        { claim_id: "cl-002", text: "The law was published in 1687 in Principia Mathematica.", category: "fact", supported: true, evidence_ids: ["ev-89a1c4-2026"], confidence: 0.96 },
                        { claim_id: "cl-003", text: "Gravitational attraction is inversely proportional to distance squared.", category: "fact", supported: true, evidence_ids: ["ev-44b2d9-2026"], confidence: 0.95 }
                    ],
                    assumptions: ["Standard Newtonian classical frame of reference."],
                    uncertainties: []
                }
            };
        }
    },

    verifier: {
        id: "verifier",
        name: "Verifier Agent",
        icon: "🛡️",
        role: "Coordinates 8 independent verification checkers: fact consistency, logic fallacies, computation, code, APIs, and safety risks.",
        stage: "Stage 7 of 12 (Multi-Checker Parallel Verification)",
        tag: "Verification",
        tagColor: "orange-tag",
        status: "Operational",
        identifier: "verifyai.agents.verifier.VerifierAgent",
        latency: "165ms",
        mission: "The Verifier Agent is the system's Truth Engine. It receives the GeneratedAnswer and independently orchestrates 8 specialized verification checkers (FactChecker, LogicChecker, ComputationChecker, CodeChecker, ApiChecker, ContradictionDetector, SourceReliabilityChecker, RiskDetector) without allowing the Generator to bias the outcome.",
        systemPrompt: `SYSTEM DIRECTIVE: Verifier Agent (VerifyAI Core)
ROLE: Independent Verification Orchestrator.
PROTOCOL:
1. Dispatch answer claims to the active checkers assigned by TaskRouter.
2. Run independent mathematical computation using Calculator tool.
3. Validate Python syntax & execution safety using CodeExecutor.
4. Cross-examine claims against evidence for factual overlap and contradictions.
5. Score each check: PASS (>=0.70), WARNING (0.40-0.69), FAIL (<0.40), or NOT_REQUIRED.`,
        workflow: [
            { title: "Checker Task Distribution", desc: "Fans out claims and answer artifacts to all required checking engines concurrently." },
            { title: "Independent Computation & Code Exec", desc: "Evaluates equations in AST sandbox and checks code compilation." },
            { title: "Fact Support Verification", desc: "Cross-checks fact claims against evidence supporting text." },
            { title: "Verification Matrix Aggregation", desc: "Compiles structured VerificationResult reports with failure itemization." }
        ],
        deepDive: `<p>In standard AI assistants, the same LLM that generates the answer is asked 'Are you sure this is right?'. Because LLMs suffer from confirmation bias and self-reinforcing hallucinations, they almost always confirm their own mistakes.</p><p style="margin-top:8px;"><strong>The VerifyAI Guarantee:</strong> The Verifier runs completely isolated, deterministic Python engines (Calculator AST, compilation tests, rule-based logic fallacies) that cannot be persuaded by linguistic fluency.</p>`,
        inputSchema: JSON.stringify({ "answer": "GeneratedAnswer", "evidence": "list[EvidenceItem]", "required_checks": ["string"] }, null, 2),
        outputSchema: JSON.stringify({
            "verification_results": [
                { "check_type": "string", "status": "PASS|FAIL|WARNING|NOT_REQUIRED", "score": "float", "details": "string", "failed_items": ["string"] }
            ]
        }, null, 2),
        tools: [
            { name: "Deterministic AST Calculator", type: "Math Engine", icon: "🧮", desc: "Executes mathematical expressions with symbol isolation." },
            { name: "Isolated Code Sandbox", type: "Subprocess Runner", icon: "💻", desc: "Compiles and executes Python in restricted environments." },
            { name: "Logic Fallacy Scanner", type: "Prover Engine", icon: "🔍", desc: "Detects non-sequiturs, circularity, and unwarranted absolutes." }
        ],
        guardrails: [
            { title: "Zero Generator Interference", desc: "The Generator cannot provide hidden prompts or hints to the Verifier." }
        ],
        samples: ["Earth has 2 moons and 15 days in a week", "15 + 25 = 40", "Newton formulated gravity in 1687"],
        simulate: (input) => {
            const hasError = /2 moons|15 days|flat earth|gravity discovered in 1999/i.test(input);
            return {
                agent: "VerifierAgent",
                status: "SUCCESS",
                execution_time_ms: 152,
                results: [
                    { check_type: "fact_check", status: hasError ? "FAIL" : "PASS", score: hasError ? 0.25 : 0.95, details: hasError ? "1 of 2 claims contradicted by authoritative evidence." : "All 3 fact claims supported with >85% evidence overlap.", failed_items: hasError ? ["Earth has 2 moons"] : [] },
                    { check_type: "logic_check", status: "PASS", score: 0.92, details: "No circular reasoning or unwarranted absolute terms detected.", failed_items: [] },
                    { check_type: "contradiction", status: hasError ? "FAIL" : "PASS", score: hasError ? 0.30 : 0.98, details: hasError ? "High-severity contradiction detected with astronomical records." : "Zero internal or external contradictions found.", failed_items: [] },
                    { check_type: "risk_detection", status: "PASS", score: 1.0, details: "No dangerous shell commands or unsafe advice detected.", failed_items: [] }
                ]
            };
        }
    },

    critic: {
        id: "critic",
        name: "Critic Agent",
        icon: "⚠️",
        role: "Adversarial reviewer. Actively hunts for unsupported claims, contradictions, overconfidence, or hallucinated facts.",
        stage: "Stage 8 of 12 (Adversarial Red-Team & Falsification)",
        tag: "Criticism",
        tagColor: "red-tag",
        status: "Operational",
        identifier: "verifyai.agents.critic.CriticAgent",
        latency: "64ms",
        mission: "The Critic Agent plays the role of an adversarial prosecutor. It operates on Karl Popper's principle of falsification: rather than trying to prove the answer right, it actively attempts to break it, searching for weak assumptions, unsupported inferences, and subtle contradictions.",
        systemPrompt: `SYSTEM DIRECTIVE: Critic Agent (VerifyAI Core)
ROLE: Adversarial Red-Team Falsifier.
OBJECTIVES:
1. Review all VerificationResults: any FAIL or WARNING must be treated as a critical defect.
2. Identify claims with confidence < 0.70 or zero supporting evidence.
3. Detect overconfident prose not backed by evidence.
4. Issue recommendation:
   - 'accept': Flawless execution across all checks.
   - 'correct': Repairable flaws detected (isolated bad facts or math errors).
   - 'reject': Fatal contradictions or high safety risk.`,
        workflow: [
            { title: "Verification Results Audit", desc: "Scans all checker outputs for failed checks, warnings, or low confidence scores." },
            { title: "Adversarial Falsification", desc: "Cross-checks claims against edge cases and negative assertions." },
            { title: "Severity Classification", desc: "Classifies identified defects into low, medium, or high severity." },
            { title: "Recommendation Verdict", desc: "Issues verdict: ACCEPT, CORRECT (triggers self-repair), or REJECT." }
        ],
        deepDive: `<p>Most AI architectures are cooperative; components are incentivized to help the model succeed, which promotes complacency.</p><p style="margin-top:8px;"><strong>Why VerifyAI uses an Adversarial Critic:</strong> The Critic's reward function is maximized by finding errors. This structural antagonism ensures that only rigorously validated answers make it through to the user.</p>`,
        inputSchema: JSON.stringify({ "answer": "GeneratedAnswer", "verification_results": "list[VerificationResult]" }, null, 2),
        outputSchema: JSON.stringify({
            "critic_report": {
                "issues_found": [{ "claim": "string", "issue": "string", "severity": "low|medium|high" }],
                "severity": "low|medium|high",
                "recommendation": "accept|correct|reject",
                "details": "string"
            }
        }, null, 2),
        tools: [
            { name: "Falsification Heuristic Engine", type: "Adversarial Scanner", icon: "⚡", desc: "Scans for logical fallacies and overconfidence." },
            { name: "Contradiction Matrix", type: "Cross-Examiner", icon: "⚔️", desc: "Compares claim pairs for mutual exclusion." }
        ],
        guardrails: [
            { title: "Automatic Correction Trigger", desc: "Any unsupported claim with confidence below 0.60 forces a recommendation of 'correct'." }
        ],
        samples: ["All birds can fly without exception", "Newton formulated gravity in 1687"],
        simulate: (input) => {
            const hasFlaw = /all birds can fly|never|always|flat earth|impossible/i.test(input);
            return {
                agent: "CriticAgent",
                status: "SUCCESS",
                execution_time_ms: 58,
                report: {
                    issues_found: hasFlaw ? [
                        { claim: input, issue: "Absolute universal quantifier 'all' is falsified by penguins and ostriches.", severity: "high" }
                    ] : [],
                    severity: hasFlaw ? "high" : "none",
                    recommendation: hasFlaw ? "correct" : "accept",
                    details: hasFlaw ? "Adversarial review identified 1 falsifiable claim requiring surgical correction." : "Adversarial cross-examination passed with zero vulnerabilities."
                }
            };
        }
    },

    correction: {
        id: "correction",
        name: "Correction Agent",
        icon: "🔧",
        role: "Surgical repair engine. Regenerates ONLY the failed or contradictory claims using grounded evidence, preserving valid facts.",
        stage: "Stage 9 of 12 (Surgical Claim Repair)",
        tag: "Correction",
        tagColor: "orange-tag",
        status: "Operational",
        identifier: "verifyai.agents.correction.CorrectionAgent",
        latency: "110ms",
        mission: "The Correction Agent is the repair engine in VerifyAI's self-healing loop. Unlike naive systems that regenerate the entire prompt from scratch (frequently introducing new hallucinations), the Correction Agent performs surgical replacement on only the specific claim that failed verification.",
        systemPrompt: `SYSTEM DIRECTIVE: Correction Agent (VerifyAI Core)
ROLE: Surgical Claim Repair Specialist.
PROTOCOL:
1. Isolate the specific claims flagged as issues in the CriticReport.
2. Query EvidenceItems to find grounded facts for the specific failed assertion.
3. Rewrite ONLY the invalid claim while leaving verified claims untouched.
4. Increment repair iteration counter (maximum 3 iterations allowed).
5. Output corrected answer and explicit changelog of modifications.`,
        workflow: [
            { title: "Defect Isolation", desc: "Pinpoints exact sentence indexes and claim IDs marked for correction." },
            { title: "Evidence Re-Grounding", desc: "Extracts grounded data from the evidence pool to replace flawed assertions." },
            { title: "Surgical Claim Rewriting", desc: "Modifies only the defective claim while strictly preserving surrounding valid context." },
            { title: "Changelog Generation", desc: "Records exact delta between original and repaired claim." }
        ],
        deepDive: `<p>Full-text re-generation is chaotic: fixing a typo in paragraph 3 often causes an LLM to corrupt a correct equation in paragraph 1.</p><p style="margin-top:8px;"><strong>Why VerifyAI repairs surgically:</strong> By keeping valid claims locked and mutating only the debunked proposition, VerifyAI achieves fast, monotonic convergence toward truth.</p>`,
        inputSchema: JSON.stringify({ "answer": "GeneratedAnswer", "critic_report": "CriticReport", "iteration": 1 }, null, 2),
        outputSchema: JSON.stringify({
            "original_answer": "string",
            "corrected_answer": "string",
            "corrected_claims": ["Claim"],
            "corrections_made": ["string"],
            "iteration": 1
        }, null, 2),
        tools: [
            { name: "Surgical Token Replacer", type: "AST Rewriter", icon: "🩹", desc: "Injects verified claims into original syntax tree." },
            { name: "Context Coherence Preserver", type: "NLP Verifier", icon: "🔗", desc: "Ensures transitional cohesion after replacement." }
        ],
        guardrails: [
            { title: "3-Iteration Loop Limit", desc: "If an assertion cannot be repaired in 3 cycles, self-correction terminates and issues a REJECT." }
        ],
        samples: ["All birds can fly including penguins.", "The speed of light is 300 km/h."],
        simulate: (input) => {
            return {
                agent: "CorrectionAgent",
                status: "SUCCESS",
                execution_time_ms: 104,
                iteration: 1,
                repair: {
                    original_sentence: "All birds can fly without exception.",
                    repaired_sentence: "Most birds can fly, although flightless species such as penguins and ostriches are notable exceptions.",
                    corrections_made: [
                        "Replaced absolute quantifier 'All' with 'Most'.",
                        "Appended grounded empirical exceptions (penguins, ostriches)."
                    ],
                    iteration_count: 1
                }
            };
        }
    },

    reverifier: {
        id: "reverifier",
        name: "Reverifier Agent",
        icon: "🔄",
        role: "Guarantees repaired output is re-tested through all checkers. Limits repair loops to maximum 3 iterations before hard REJECT.",
        stage: "Stage 10 of 12 (Repair Validation & Loop Control)",
        tag: "Loop Control",
        tagColor: "blue-tag",
        status: "Operational",
        identifier: "verifyai.agents.reverifier.ReverifierAgent",
        latency: "140ms",
        mission: "The Reverifier Agent ensures that corrections made by the Correction Agent didn't introduce new fallacies or regressions. It feeds the repaired answer back into the verification suite and enforces strict convergence criteria, halting infinite repair loops.",
        systemPrompt: `SYSTEM DIRECTIVE: Reverifier Agent (VerifyAI Core)
ROLE: Quality Assurance and Convergence Guard.
OBJECTIVES:
1. Re-run verification suite on the surgically repaired answer.
2. Compute the score delta (post-correction score minus pre-correction score).
3. Confirm that all previously flagged issues are now resolved.
4. Enforce strict termination: if iteration >= 3 and issues remain, signal FinalJudge for hard REJECT.`,
        workflow: [
            { title: "Repaired Answer Ingestion", desc: "Receives repaired answer and constructs fresh Claim representations." },
            { title: "Full Re-Verification Suite", desc: "Re-runs active checkers to validate the integrity of the patch." },
            { title: "Delta Score Computation", desc: "Measures verification score improvement." },
            { title: "Loop Termination Guard", desc: "Halts loop if converged (all PASS) or if 3-cycle ceiling is hit." }
        ],
        deepDive: `<p>A common vulnerability in autonomous AI agent loops is infinite cycling: Agent A corrects a word, which causes Agent B to object, looping forever and burning API quota.</p><p style="margin-top:8px;"><strong>The Reverifier's Guardrail:</strong> The Reverifier enforces a hard 3-iteration maximum with mathematical convergence monitoring. If an answer cannot be proven true within 3 attempts, it is rejected.</p>`,
        inputSchema: JSON.stringify({ "corrected": "CorrectionResult", "evidence": "list[EvidenceItem]" }, null, 2),
        outputSchema: JSON.stringify({
            "reverification_results": ["VerificationResult"],
            "delta_score": "float",
            "passed": "boolean",
            "continue_loop": "boolean"
        }, null, 2),
        tools: [
            { name: "Regression Detector", type: "Differential Tester", icon: "📉", desc: "Checks that previously passing claims remained intact." },
            { name: "Loop Convergence Monitor", type: "Termination Guard", icon: "🛑", desc: "Prevents cyclic repair oscillation." }
        ],
        guardrails: [
            { title: "Strict Iteration Ceiling", desc: "Iteration counter cannot exceed 3; triggers instant abort." }
        ],
        samples: ["Repaired: Most birds can fly with exceptions..."],
        simulate: (input) => {
            return {
                agent: "ReverifierAgent",
                status: "SUCCESS",
                execution_time_ms: 135,
                reverification: {
                    all_passed: true,
                    delta_score: "+0.65",
                    previous_score: 0.30,
                    new_score: 0.95,
                    decision: "CONVERGED_PASS",
                    iterations_consumed: 1
                }
            };
        }
    },

    judge: {
        id: "judge",
        name: "Final Judge",
        icon: "⚖️",
        role: "Synthesizes final machine-readable verdict (ACCEPT, CORRECTED, REJECT, NEEDS_CLARIFICATION) with calibrated confidence score.",
        stage: "Stage 11 of 12 (Deterministic Verdict & Calibration)",
        tag: "Decision",
        tagColor: "green-tag",
        status: "Operational",
        identifier: "verifyai.agents.final_judge.FinalJudgeAgent",
        latency: "22ms",
        mission: "The Final Judge is the deterministic supreme court of the pipeline. It synthesizes all verification scores into a single weighted confidence rating and issues an unambiguous verdict: ACCEPT (flawless), CORRECTED (repaired and re-verified), REJECT (unverified or dangerous), or NEEDS_CLARIFICATION (ambiguous).",
        systemPrompt: `SYSTEM DIRECTIVE: Final Judge Agent (VerifyAI Core)
ROLE: Deterministic Final Arbiter.
CONFIDENCE FORMULA:
Confidence = (FactCheck * 0.25) + (LogicCheck * 0.20) + (Computation * 0.15) + (CodeCheck * 0.15) + (SourceReliability * 0.10) + (Contradiction * 0.10) + (RiskDetector * 0.05)
DECISION MATRIX:
- All checks PASS on 1st try -> ACCEPT
- All checks PASS after repairs -> CORRECTED
- Any safety/risk check fails -> REJECT (Veto)
- Iterations >= 3 with failures -> REJECT
- Ambiguity unresolved -> NEEDS_CLARIFICATION`,
        workflow: [
            { title: "Score Vector Collection", desc: "Aggregates normalized scores from all executed checkers." },
            { title: "Normalized Weighting", desc: "Normalizes weights across only the active (non-pruned) checkers." },
            { title: "Veto Rule Inspection", desc: "Applies non-negotiable safety and risk vetoes." },
            { title: "Verdict Issuance", desc: "Emits final machine-readable decision enum and confidence percentage." }
        ],
        deepDive: `<p>Subjective 'confidence' numbers output by LLMs are notoriously miscalibrated—models frequently claim 99% confidence on total hallucinations.</p><p style="margin-top:8px;"><strong>VerifyAI Calibrated Math:</strong> The Final Judge calculates confidence strictly from external empirical tests (did the Python code compile? Did the calculator match? Did the encyclopedic text overlap?).</p>`,
        inputSchema: JSON.stringify({ "verification_results": "list[VerificationResult]", "critic_report": "CriticReport" }, null, 2),
        outputSchema: JSON.stringify({
            "final_decision": {
                "decision": "ACCEPT|CORRECTED|REJECT|NEEDS_CLARIFICATION",
                "confidence": "float (0-100%)",
                "reason": "string",
                "passed_checks": ["string"],
                "failed_checks": ["string"]
            }
        }, null, 2),
        tools: [
            { name: "Bayesian Confidence Calibrator", type: "Statistical Engine", icon: "📐", desc: "Computes empirical weighted trust indices." },
            { name: "Safety Veto Gate", type: "Boolean Gatekeeper", icon: "⛔", desc: "Instant reject for high-risk prompts." }
        ],
        guardrails: [
            { title: "Risk Zero-Tolerance", desc: "A score of 0.0 on RiskDetector triggers immediate REJECT regardless of 100% scores elsewhere." }
        ],
        samples: ["All checks passed with 0.95+ average", "Code syntax error compilation failed"],
        simulate: (input) => {
            return {
                agent: "FinalJudgeAgent",
                status: "SUCCESS",
                execution_time_ms: 18,
                decision: {
                    decision: "ACCEPT",
                    confidence: 96.5,
                    reason: "All 4 active verification profiles passed with high confidence. Source reliability and empirical corroboration verified.",
                    passed_checks: ["fact_checker", "logic_checker", "contradiction", "source_reliability"],
                    failed_checks: []
                }
            };
        }
    },

    audit: {
        id: "audit",
        name: "Audit Agent",
        icon: "▤",
        role: "Compiles cryptographic execution trail and generates official Verification Passport, logging to Supabase database.",
        stage: "Stage 12 of 12 (Cryptographic Audit & Passport Issuance)",
        tag: "Audit",
        tagColor: "blue-tag",
        status: "Operational",
        identifier: "verifyai.agents.audit_agent.AuditAgent",
        latency: "48ms",
        mission: "The Audit Agent provides end-to-end immutability. It collects telemetry from all 11 prior agents (timestamps, actions, inputs, outputs, scores), generates an official Verification Passport with SHA-256 integrity hash, and persists the audit record into the Supabase PostgreSQL database.",
        systemPrompt: `SYSTEM DIRECTIVE: Audit Agent (VerifyAI Core)
ROLE: Cryptographic Compliance & Passport Synthesizer.
OBJECTIVES:
1. Aggregate full execution trail across all 12 micro-agents.
2. Compile VerificationPassport data structure.
3. Compute SHA-256 checksum across claims and verification scores.
4. Persist audit snapshot into Supabase 'audit_log' and 'tasks' tables.
5. Provide permanent cryptographic audit trail for compliance.`,
        workflow: [
            { title: "Telemetry Aggregation", desc: "Gathers timestamps, agent run logs, and outputs from all pipeline steps." },
            { title: "Truth Passport Compilation", desc: "Builds official VerificationPassport summary with claim and checker metrics." },
            { title: "SHA-256 Integrity Sealing", desc: "Generates tamper-evident cryptographic hash." },
            { title: "Supabase Database Persistence", desc: "Writes complete audit envelope to cloud storage." }
        ],
        deepDive: `<p>In regulated industries (healthcare, finance, legal, mission-critical engineering), AI answers cannot be accepted without proof of how the decision was reached.</p><p style="margin-top:8px;"><strong>The Verification Passport:</strong> VerifyAI issues a permanent, cryptographic Truth Passport for every answer, documenting exactly which facts were checked, which evidence was used, and which agents signed off.</p>`,
        inputSchema: JSON.stringify({ "task_id": "uuid4", "pipeline_data": "dict" }, null, 2),
        outputSchema: JSON.stringify({
            "verification_passport": {
                "task_id": "uuid4",
                "claims_checked": "int",
                "claims_supported": "int",
                "final_decision": "string",
                "final_confidence": "float",
                "sha256_hash": "string"
            }
        }, null, 2),
        tools: [
            { name: "SHA-256 Integrity Hasher", type: "Crypto Utility", icon: "🔐", desc: "Seals the audit log against tampering." },
            { name: "Supabase DB Connector", type: "PostgreSQL Client", icon: "💾", desc: "Persists records to cloud database." }
        ],
        guardrails: [
            { title: "Append-Only Audit", desc: "Audit records are immutable and cannot be overwritten or deleted." }
        ],
        samples: ["Task #a1b2c3 - Fact Verification Complete"],
        simulate: (input) => {
            return {
                agent: "AuditAgent",
                status: "SUCCESS",
                execution_time_ms: 44,
                passport: {
                    task_id: "tsk-f9821c-2026",
                    claims_checked: 3,
                    claims_supported: 3,
                    unsupported_claims: 0,
                    evidence_sources: 2,
                    contradictions: 0,
                    final_decision: "ACCEPT",
                    final_confidence: 96.5,
                    sha256_signature: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    persisted_to_database: true
                }
            };
        }
    }
};

// 12 Agents Ordering Sequence
const AGENT_ORDER = [
    "planner", "router", "ambiguity", "researcher", 
    "evidence", "generator", "verifier", "critic", 
    "correction", "reverifier", "judge", "audit"
];

let currentAgentId = "planner";

// Initialize Page
document.addEventListener("DOMContentLoaded", () => {
    // Parse query param
    const params = new URLSearchParams(window.location.search);
    const requested = params.get("agent") || params.get("id");
    if (requested && AGENT_REGISTRY[requested]) {
        currentAgentId = requested;
    }

    renderSelectorBar();
    renderAgent(currentAgentId);
});

// Render Top 12 Agents Horizontal Bar
function renderSelectorBar() {
    const bar = document.getElementById("agentSelectorBar");
    if (!bar) return;
    bar.innerHTML = "";

    AGENT_ORDER.forEach((id, idx) => {
        const ag = AGENT_REGISTRY[id];
        const btn = document.createElement("button");
        btn.className = `agent-selector-btn ${id === currentAgentId ? "active" : ""}`;
        btn.id = `btn-sel-${id}`;
        btn.innerHTML = `<span>${ag.icon}</span> <span>${idx + 1}. ${ag.name}</span>`;
        btn.onclick = () => renderAgent(id, true);
        bar.appendChild(btn);
    });
}

// Render Single Agent View
function renderAgent(agentId, pushState = false) {
    const ag = AGENT_REGISTRY[agentId];
    if (!ag) return;
    currentAgentId = agentId;

    if (pushState) {
        const url = new URL(window.location);
        url.searchParams.set("agent", agentId);
        window.history.pushState({}, "", url);
    }

    // Update Selector Buttons
    document.querySelectorAll(".agent-selector-btn").forEach(b => b.classList.remove("active"));
    const activeBtn = document.getElementById(`btn-sel-${agentId}`);
    if (activeBtn) activeBtn.classList.add("active");

    // Topbar & Hero
    document.getElementById("topbarAgentName").textContent = ag.name;
    document.getElementById("heroIcon").textContent = ag.icon;
    document.getElementById("heroName").innerHTML = `${ag.name} <span class="tag ${ag.tagColor}">${ag.tag}</span>`;
    document.getElementById("heroMission").textContent = ag.mission;
    document.getElementById("heroIdentifier").textContent = ag.identifier;
    document.getElementById("heroStatus").textContent = ag.status;
    document.getElementById("heroLatency").textContent = ag.latency;
    document.getElementById("heroStage").textContent = ag.stage;

    // Tab 1: System Prompt & Workflow
    document.getElementById("systemPromptCode").textContent = ag.systemPrompt;
    
    const timeline = document.getElementById("workflowTimeline");
    timeline.innerHTML = "";
    ag.workflow.forEach((step, idx) => {
        const row = document.createElement("div");
        row.className = "workflow-step";
        row.innerHTML = `
            <div class="step-num">${idx + 1}</div>
            <div class="step-text">
                <strong>${step.title}</strong>
                <p>${step.desc}</p>
            </div>
        `;
        timeline.appendChild(row);
    });

    document.getElementById("deepDiveText").innerHTML = ag.deepDive;

    // Tab 2: Schemas
    document.getElementById("inputSchemaCode").textContent = ag.inputSchema;
    document.getElementById("outputSchemaCode").textContent = ag.outputSchema;

    // Tab 3: Tools & Guardrails
    const toolsContainer = document.getElementById("toolsList");
    toolsContainer.innerHTML = "";
    ag.tools.forEach(t => {
        const card = document.createElement("div");
        card.className = "tool-card";
        card.innerHTML = `
            <div class="tool-icon">${t.icon}</div>
            <div class="tool-info">
                <strong>${t.name}</strong>
                <span>${t.type} &bull; ${t.desc}</span>
            </div>
        `;
        toolsContainer.appendChild(card);
    });

    const guardrailsContainer = document.getElementById("guardrailsList");
    guardrailsContainer.innerHTML = "";
    ag.guardrails.forEach((g, idx) => {
        const row = document.createElement("div");
        row.className = "workflow-step";
        row.innerHTML = `
            <div class="step-num" style="background: #ef4444;">✓</div>
            <div class="step-text">
                <strong>${g.title}</strong>
                <p>${g.desc}</p>
            </div>
        `;
        guardrailsContainer.appendChild(row);
    });

    // Tab 4: Simulator
    const chipsContainer = document.getElementById("sampleChipsContainer");
    chipsContainer.innerHTML = "";
    ag.samples.forEach(s => {
        const chip = document.createElement("button");
        chip.className = "sample-chip";
        chip.textContent = s.length > 35 ? s.substring(0, 32) + "..." : s;
        chip.title = s;
        chip.onclick = () => {
            document.getElementById("simInput").value = s;
        };
        chipsContainer.appendChild(chip);
    });

    // Pre-fill input
    const simInput = document.getElementById("simInput");
    if (ag.samples.length > 0) {
        simInput.value = ag.samples[0];
    }
    document.getElementById("simOutputCode").textContent = `// Press "Execute Simulation" to run isolated execution of ${ag.name}...`;
    document.getElementById("simStatus").textContent = "Ready for execution";

    // Bottom Prev / Next
    const currIdx = AGENT_ORDER.indexOf(agentId);
    const prevIdx = (currIdx - 1 + AGENT_ORDER.length) % AGENT_ORDER.length;
    const nextIdx = (currIdx + 1) % AGENT_ORDER.length;

    const prevAg = AGENT_REGISTRY[AGENT_ORDER[prevIdx]];
    const nextAg = AGENT_REGISTRY[AGENT_ORDER[nextIdx]];

    const btnPrev = document.getElementById("btnPrevAgent");
    const btnNext = document.getElementById("btnNextAgent");

    btnPrev.innerHTML = `&larr; ${prevAg.icon} ${prevAg.name}`;
    btnPrev.onclick = () => renderAgent(prevAg.id, true);

    btnNext.innerHTML = `${nextAg.icon} ${nextAg.name} &rarr;`;
    btnNext.onclick = () => renderAgent(nextAg.id, true);

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Previous & Next Shortcuts
function navigatePrev() {
    const currIdx = AGENT_ORDER.indexOf(currentAgentId);
    const prevIdx = (currIdx - 1 + AGENT_ORDER.length) % AGENT_ORDER.length;
    renderAgent(AGENT_ORDER[prevIdx], true);
}

function navigateNext() {
    const currIdx = AGENT_ORDER.indexOf(currentAgentId);
    const nextIdx = (currIdx + 1) % AGENT_ORDER.length;
    renderAgent(AGENT_ORDER[nextIdx], true);
}

// Interactive Simulation Engine
async function runSimulation() {
    const ag = AGENT_REGISTRY[currentAgentId];
    if (!ag) return;

    const inputVal = document.getElementById("simInput").value.trim() || ag.samples[0];
    const btn = document.getElementById("simRunBtn");
    const statusElem = document.getElementById("simStatus");
    const outputElem = document.getElementById("simOutputCode");

    btn.disabled = true;
    btn.innerHTML = `<span>⏳</span> Simulating ${ag.name}...`;
    statusElem.textContent = "Processing through isolated micro-agent engine...";
    outputElem.textContent = `// Executing ${ag.identifier}...\n// Processing input: "${inputVal}"\n// Analyzing constraint parameters...`;

    const start = performance.now();
    await new Promise(r => setTimeout(r, 450));

    try {
        const simResult = ag.simulate(inputVal);
        const elapsed = (performance.now() - start).toFixed(1);
        
        simResult._simulation_metadata = {
            simulated_at: new Date().toISOString(),
            client_roundtrip_ms: elapsed,
            environment: "VerifyAI-Agent-Sandbox-v2"
        };

        outputElem.textContent = JSON.stringify(simResult, null, 2);
        statusElem.textContent = `Completed successfully in ${elapsed}ms!`;
        showToast(`${ag.name} simulation executed!`);
    } catch (e) {
        outputElem.textContent = `Error in simulation: ${e.message}`;
        statusElem.textContent = "Simulation encountered an error.";
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>▶</span> Execute Simulation`;
    }
}
