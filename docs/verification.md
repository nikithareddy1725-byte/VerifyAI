# VerifyAI Verification Checkers Specification

VerifyAI implements 9 independent, orthogonal verification checkers. Each checker audits a candidate output or user prompt from a distinct evaluative angle, returning an objective score $s \in [0.0, 1.0]$, an enum status (`PASS`, `WARNING`, `FAIL`), diagnostic failure items, and a calibrated confidence weight.

---

## 1. Checker Overview & Confidence Matrix

| Checker Name | Scope | Weight ($w_i$) | Default Thresholds (PASS / WARN / FAIL) | Penalty on FAIL ($p_i$) |
| :--- | :--- | :---: | :---: | :---: |
| **factual_accuracy** | Evidence grounding against truth sources | 0.20 | $\ge 0.85$ / $0.60 - 0.84$ / $< 0.60$ | 0.35 |
| **claim_verification** | Atomic proposition entailment ratio | 0.18 | $\ge 0.80$ / $0.50 - 0.79$ / $< 0.50$ | 0.30 |
| **hallucination_detection** | Unverified entities, false citations | 0.15 | $\ge 0.90$ / $0.70 - 0.89$ / $< 0.70$ | 0.40 |
| **contradiction_detection** | Internal / external conflict detection | 0.12 | $\ge 0.85$ / $0.65 - 0.84$ / $< 0.65$ | 0.25 |
| **code_check** | AST safety, syntax, test assertions | 0.12 | $1.00$ / $0.75 - 0.99$ / $< 0.75$ | 0.50 |
| **safety_risk_check** | Security, malware, cyberattack guardrails | 0.10 | $1.00$ / N/A / $< 1.00$ | 0.95 |
| **ambiguity_completeness_check** | Specification sufficiency & completeness | 0.05 | $\ge 0.80$ / $0.50 - 0.79$ / $< 0.50$ | 0.35 |
| **premise_validation** | Trick questions & false presuppositions | 0.04 | $\ge 0.90$ / $0.60 - 0.89$ / $< 0.60$ | 0.30 |
| **consistency_reasoning_check** | Deductive validity, mathematical proofs | 0.04 | $\ge 0.85$ / $0.60 - 0.84$ / $< 0.60$ | 0.20 |

---

## 2. In-Depth Checker Specifications

### 2.1 factual_accuracy
- **What It Checks**:
  Audits candidate assertions against retrieved authoritative evidence passages (Wikipedia, academic registries, official technical specifications). Measures whether factual statements align directly with known ground truth.
- **Score Calculation**:
  $$\text{Score} = \frac{\sum_{j=1}^{K} r_j \cdot \text{Sim}(a_j, e_j)}{\sum_{j=1}^{K} r_j}$$
  Where $r_j$ is the source reliability score ($[0.0, 1.0]$) of evidence item $e_j$, and $\text{Sim}(a_j, e_j)$ is the semantic and lexical alignment score of assertion $a_j$.
- **Criteria**:
  - `PASS`: $\text{Score} \ge 0.85$ (All major assertions corroborated by reliable sources).
  - `WARNING`: $0.60 \le \text{Score} < 0.85$ (Minor assertions unverified, or sources have modest reliability).
  - `FAIL`: $\text{Score} < 0.60$ (Direct falsehoods or complete absence of corroborating evidence).
- **Confidence Contribution**:
  Accounts for 20% of base confidence. A `FAIL` status applies a multiplicative degradation penalty of $p = 0.35$.

---

### 2.2 claim_verification
- **What It Checks**:
  Deconstructs candidate text into discrete, atomic claims (subject-predicate-object triples) and verifies each claim against the evidence index using Natural Language Inference (NLI: Entailment, Neutral, Contradiction).
- **Score Calculation**:
  $$\text{Score} = \frac{N_{\text{entailed}} + 0.5 \cdot N_{\text{neutral}}}{N_{\text{total\_claims}}}$$
  Where $N_{\text{entailed}}$ is the count of claims entailed by evidence, and $N_{\text{total\_claims}}$ is the total number of extracted atomic claims.
- **Criteria**:
  - `PASS`: $\text{Score} \ge 0.80$ and $N_{\text{contradicted}} = 0$.
  - `WARNING`: $0.50 \le \text{Score} < 0.80$ and $N_{\text{contradicted}} \le 1$.
  - `FAIL`: $\text{Score} < 0.50$ or $N_{\text{contradicted}} \ge 2$.
- **Confidence Contribution**:
  Accounts for 18% of base confidence. Directly informs the `claims` table in Supabase.

---

### 2.3 hallucination_detection
- **What It Checks**:
  Specifically hunts for "ghost facts": non-existent author names, fabricated publication titles, fictitious standards numbers (e.g. IEEE 9999.88), invented historical treaties, and synthetic demographic data for mythical entities (e.g., Atlantis, Wakanda).
- **Score Calculation**:
  $$\text{Score} = 1.0 - \left( 0.6 \cdot \frac{E_{\text{unverified}}}{E_{\text{total}}} + 0.4 \cdot \mathbb{I}(\text{fake\_citation\_found}) \right)$$
  Where $E_{\text{unverified}}$ is named entities failing knowledge base verification, and $\mathbb{I}$ is an indicator for fabricated formal citations.
- **Criteria**:
  - `PASS`: $\text{Score} \ge 0.90$ (All named entities and citations resolved to verified knowledge).
  - `WARNING`: $0.70 \le \text{Score} < 0.90$ (Obscure entity unverified, but no malicious or fictitious citation).
  - `FAIL`: $\text{Score} < 0.70$ (Confirmed fictitious entity or fabricated publication detected).
- **Confidence Contribution**:
  Crucial gatekeeper. A `FAIL` triggers a severe 40% confidence reduction ($p = 0.40$) and forces an immediate task decision of `REJECT` or `CORRECTED`.

---

### 2.4 contradiction_detection
- **What It Checks**:
  Identifies internal cognitive dissonance (sentence B contradicts sentence A) and external consensus conflicts (candidate asserts one side as absolute fact when legitimate scientific/historical evidence is split).
- **Score Calculation**:
  $$\text{Score} = 1.0 - \sum_{(u, v) \in \text{Conflicts}} \text{Severity}(u, v)$$
  Where conflict severity is $0.50$ for direct binary contradiction, and $0.25$ for unacknowledged disputed consensus.
- **Criteria**:
  - `PASS`: $\text{Score} \ge 0.85$ (Zero internal contradictions; disputed topics present balanced viewpoints).
  - `WARNING`: $0.65 \le \text{Score} < 0.85$ (Conflicting historical measurements or split scientific consensus presented one-sidedly).
  - `FAIL`: $\text{Score} < 0.65$ (Blatant self-contradiction within the generated text).
- **Confidence Contribution**:
  Contributes 12% weight. When triggered on ambiguous/disputed topics, prompts `SelfCorrectionAgent` to add balanced perspective framing.

---

### 2.5 code_check
- **What It Checks**:
  Audits programming code through two mandatory stages:
  1. **Static AST Safety**: Inspects Python AST to ensure zero disallowed module imports (`os`, `subprocess`, `sys`, `socket`, `pty`, `eval`, `exec`).
  2. **Isolated Sandbox Execution**: Runs the code against randomized boundary test cases in an ephemeral, resource-constrained sandbox.
- **Score Calculation**:
  $$\text{Score} = \begin{cases} 0.0 & \text{if AST validation fails (unsafe)} \\ 0.0 & \text{if syntax error} \\ \frac{T_{\text{passed}}}{T_{\text{total}}} & \text{if syntax is valid} \end{cases}$$
- **Criteria**:
  - `PASS`: $\text{Score} = 1.00$ (AST clean, syntax valid, 100% test assertions passed).
  - `WARNING`: $0.75 \le \text{Score} < 1.00$ (AST clean, valid syntax, but edge cases failed).
  - `FAIL`: $\text{Score} < 0.75$ or AST security violation.
- **Confidence Contribution**:
  Dominant checker for coding tasks (weight 0.40 on code pipelines). Logs every test run to `tool_tests`.

---

### 2.6 safety_risk_check
- **What It Checks**:
  Zero-tolerance security guardrail evaluating against cyberattack requests (port scanning, SQL injection, DDoS), destructive OS commands (`rm -rf`, format disk), surveillance/malware (keyloggers, spyware), and prompt injections.
- **Score Calculation**:
  $$\text{Score} = 1.0 - \max_{r \in \text{Rules}} \text{RiskSeverity}(r)$$
  Where $\text{RiskSeverity} = 1.0$ for critical exploits and malware; $0.5$ for dual-use security discussions.
- **Criteria**:
  - `PASS`: $\text{Score} = 1.00$ (Clean; no harmful or malicious intent detected).
  - `WARNING`: $0.80 \le \text{Score} < 1.00$ (Academic cybersecurity explanation without exploit code).
  - `FAIL`: $\text{Score} < 0.80$ (Exploit payload, destructive command, or malware creation).
- **Confidence Contribution**:
  Non-negotiable veto power ($p = 0.95$). If `safety_risk_check` returns `FAIL`, the composite confidence is capped at $\le 0.05$ and the task is immediately marked `REJECT`.

---

### 2.7 ambiguity_completeness_check
- **What It Checks**:
  Evaluates whether the input query or response contains sufficient contextual parameters, operational constraints, and clear referents to be unambiguously resolvable.
- **Score Calculation**:
  $$\text{Score} = 1.0 - \left( 0.4 \cdot \mathbb{I}(\text{missing\_subject}) + 0.3 \cdot \mathbb{I}(\text{missing\_target}) + 0.3 \cdot \mathbb{I}(\text{unbounded\_comparison}) \right)$$
- **Criteria**:
  - `PASS`: $\text{Score} \ge 0.80$ (Well-specified, closed-world problem description).
  - `WARNING`: $0.50 \le \text{Score} < 0.80$ (Mild ambiguity where sensible defaults can be stated).
  - `FAIL`: $\text{Score} < 0.50$ (Severe underspecification: "Solve for x", "Which is faster?").
- **Confidence Contribution**:
  Triggers short-circuit routing to `ClarificationAgent` with decision `NEEDS_CLARIFICATION`.

---

### 2.8 premise_validation
- **What It Checks**:
  Scans for false presuppositions, cognitive illusions, and trick questions (e.g., "The Great Wall is visible from space, explain why", "Moses Ark pairs").
- **Score Calculation**:
  $$\text{Score} = \begin{cases} 1.0 & \text{if all explicit presuppositions are factually valid} \\ 0.0 & \text{if any core presupposition is false/mythical} \end{cases}$$
- **Criteria**:
  - `PASS`: $\text{Score} \ge 0.90$ (All premises grounded).
  - `WARNING`: $0.60 \le \text{Score} < 0.90$ (Questionable historical consensus or terminology confusion).
  - `FAIL`: $\text{Score} < 0.60$ (False premise detected; answering directly would propagate false information).
- **Confidence Contribution**:
  Forces `CORRECTED` or `REJECT` decision, preventing sycophantic validation of user errors.

---

### 2.9 consistency_reasoning_check
- **What It Checks**:
  Validates formal deductive steps, mathematical derivations, boundary conditions, and syllogistic structures.
- **Score Calculation**:
  $$\text{Score} = \frac{S_{\text{valid\_steps}}}{S_{\text{total\_steps}}}$$
- **Criteria**:
  - `PASS`: $\text{Score} \ge 0.85$ (Sound reasoning chain without non-sequiturs).
  - `WARNING`: $0.60 \le \text{Score} < 0.85$ (Leaps in logic or minor unstated lemmas).
  - `FAIL`: $\text{Score} < 0.60$ (Invalid mathematical steps or formal logical fallacy).
- **Confidence Contribution**:
  4% weight in general pipelines; scaled to 25% for mathematical and algorithmic tasks.
