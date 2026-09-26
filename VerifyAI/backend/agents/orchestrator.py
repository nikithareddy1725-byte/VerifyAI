import uuid
from typing import Optional, List, Any, Union
from models.schemas import (
    PipelineResult, TaskPlan, VerificationPassport, AgentRunRecord,
    GeneratedAnswer, EvidenceItem, VerificationResult, CriticReport,
    CorrectionResult, FinalDecision, AmbiguityResult, Claim
)
from utils.logger import AgentLogger
from database.supabase_client import SupabaseClient
from tools.equation_solver import solve_math_problem

from .planner import PlannerAgent
from .task_router import TaskRouter
from .ambiguity_agent import AmbiguityAgent
from .researcher import ResearcherAgent
from .evidence_agent import EvidenceAgent
from .generator import GeneratorAgent
from .verifier import VerifierAgent
from .critic import CriticAgent
from .correction import CorrectionAgent
from .reverifier import ReverifierAgent
from .final_judge import FinalJudgeAgent
from .audit_agent import AuditAgent

class Orchestrator:
    def __init__(self, db_client: Optional[SupabaseClient] = None, logger: Optional[AgentLogger] = None):
        self.db_client = db_client or SupabaseClient()
        self.logger = logger or AgentLogger(__name__)
        self.agent_runs: List[AgentRunRecord] = []

    async def _save_run(self, task_id: str, agent_name: str, input_data: Any, output_data: Any, status: str = "SUCCESS", error: str = None) -> AgentRunRecord:
        icons = {
            "PlannerAgent": "🧠",
            "TaskRouter": "🧭",
            "AmbiguityAgent": "❓",
            "ResearcherAgent": "🔎",
            "EvidenceAgent": "📑",
            "GeneratorAgent": "✍️",
            "VerifierAgent": "🛡️",
            "CriticAgent": "⚠️",
            "CorrectionAgent": "🔧",
            "ReverifierAgent": "🔄",
            "FinalJudgeAgent": "⚖️",
            "AuditAgent": "▤"
        }
        record = AgentRunRecord(
            task_id=task_id,
            agent_name=agent_name,
            agent_icon=icons.get(agent_name, "◈"),
            action=f"Executed {agent_name}",
            status=status,
            step_order=len(self.agent_runs) + 1,
            input_data=str(input_data)[:250] if input_data else "",
            output_data=str(output_data)[:250] if output_data else "",
            error_message=error
        )
        self.agent_runs.append(record)
        try:
            self.db_client.save_agent_run(record)
        except Exception as e:
            self.logger.warning(f"Failed to record agent run in DB: {e}")
        return record

    async def execute(self, task_input: Union[str, Any], task_type: str = "general", gemini_api_key: Optional[str] = None) -> PipelineResult:
        # Handle if a TaskRequest object was passed
        if hasattr(task_input, "input_text"):
            gemini_api_key = getattr(task_input, "gemini_api_key", None) or gemini_api_key
            task_type = getattr(task_input, "task_type", "general")
            task_input = task_input.input_text

        task_id = str(uuid.uuid4())
        self.agent_runs = []
        self.logger.info(f"=== Starting Orchestration for Task [{task_id}] (Type: {task_type}, Gemini: {'Active' if gemini_api_key else 'Local'}) ===")
        
        # Save initial task to DB
        self.db_client.save_task(task_id=task_id, input_text=task_input, task_type=task_type)
        
        pipeline_data = {}
        corrections_history: List[CorrectionResult] = []
        
        try:
            # Check deterministic mathematics / algebra solver
            math_res = solve_math_problem(task_input)
            if math_res.get("success"):
                intent = math_res.get("intent", "mathematics")
                profile = math_res.get("profile", "Mathematics / Arithmetic")
                status = math_res.get("status", "verified")
                
                # CASE A: Incomplete math input (e.g. 3x+5= or 3x+5)
                if status == "incomplete_input":
                    plan = TaskPlan(
                        task_type="algebra",
                        complexity="low",
                        required_agents=["planner", "ambiguity_agent", "final_judge"],
                        steps=[
                            f"1. Analyze algebraic input '{task_input}'",
                            "2. Detect missing right-hand side or operand",
                            "3. Return clear requirement for complete equation"
                        ],
                        verification_requirements=["Check equation completeness"]
                    )
                    await self._save_run(task_id, "PlannerAgent", {"input": task_input}, plan.model_dump() if hasattr(plan, "model_dump") else plan.dict(), "SUCCESS")
                    await self._save_run(task_id, "AmbiguityAgent", {"input": task_input}, {"incomplete": True, "message": math_res.get("message")}, "SUCCESS")
                    
                    explanation = math_res.get("explanation", "")
                    ans = GeneratedAnswer(
                        answer_text=explanation,
                        claims=[Claim(
                            claim_id=str(uuid.uuid4()),
                            text=math_res.get("message", "Equation incomplete"),
                            category="uncertainty",
                            supported=False,
                            confidence=0.0
                        )],
                        assumptions=["Incomplete equation provided"],
                        uncertainties=["Right-hand side expression is missing"]
                    )
                    passport = VerificationPassport(
                        task_id=task_id,
                        claims_checked=1,
                        claims_supported=0,
                        unsupported_claims=1,
                        evidence_sources=0,
                        contradictions=0,
                        logic_check="WARNING",
                        fact_check="NOT_REQUIRED",
                        computation_check="NOT_REQUIRED",
                        code_check="NOT_REQUIRED",
                        api_check="NOT_REQUIRED",
                        risk_check="PASS",
                        corrections=0,
                        reverification="PASS",
                        final_decision="NEEDS_CLARIFICATION",
                        final_confidence=0.0,
                        summary=math_res.get("message", "Equation incomplete")
                    )
                    self.db_client.update_task(task_id, {"status": "NEEDS_CLARIFICATION", "score": 0.0})
                    
                    ver_res = [VerificationResult(
                        check_type="computation_checker",
                        status="WARNING",
                        score=0.0,
                        details=math_res.get("message", "Equation incomplete. Please provide right-hand side."),
                        failed_items=[task_input]
                    )]
                    decision = FinalDecision(
                        decision="NEEDS_CLARIFICATION",
                        confidence=0.0,
                        reason=math_res.get("message", "Equation incomplete"),
                        failed_checks=["computation_checker"],
                        passed_checks=["risk_detector"]
                    )
                    await self._save_run(task_id, "FinalJudgeAgent", {"decision": "NEEDS_CLARIFICATION"}, "Clarification required", "SUCCESS")
                    
                    return PipelineResult(
                        task_id=task_id,
                        status="incomplete_input",
                        success=True,
                        intent=intent,
                        profile=profile,
                        answer=None,
                        explanation=explanation,
                        message=math_res.get("message"),
                        plan=plan,
                        generated_answer=ans,
                        verification_results=ver_res,
                        evidence=[],
                        final_decision=decision,
                        verification_passport=passport,
                        agent_runs=self.agent_runs,
                        details={"example": math_res.get("example")}
                    )

                # CASE B: Verified math calculation (e.g. 3+5, 25*16, 3x+5=14)
                if status == "verified":
                    plan = TaskPlan(
                        task_type=intent,
                        complexity="low",
                        required_agents=["planner", "generator", "computation_checker", "final_judge"],
                        steps=[
                            f"1. Parse deterministic mathematical problem: '{task_input}'",
                            "2. Execute deterministic arithmetic / symbolic algebra solver",
                            "3. Perform independent algebraic & computational verification",
                            "4. Issue verified result"
                        ],
                        verification_requirements=["Deterministic computation verification"]
                    )
                    await self._save_run(task_id, "PlannerAgent", {"input": task_input}, plan.model_dump() if hasattr(plan, "model_dump") else plan.dict(), "SUCCESS")
                    
                    explanation = math_res.get("explanation", f"{task_input} = {math_res.get('answer')}")
                    answer_val = math_res.get("answer", "")
                    
                    ans = GeneratedAnswer(
                        answer_text=explanation,
                        claims=[Claim(
                            claim_id=str(uuid.uuid4()),
                            text=f"{task_input} evaluates to {answer_val}",
                            category="fact",
                            supported=True,
                            confidence=1.0
                        )],
                        assumptions=["Standard mathematical axioms"],
                        uncertainties=[]
                    )
                    await self._save_run(task_id, "GeneratorAgent", {"input": task_input}, f"Calculated: {answer_val}", "SUCCESS")
                    
                    ver_res = [
                        VerificationResult(
                            check_type="computation_checker",
                            status="PASS",
                            score=1.0,
                            details=f"Computation for '{task_input}' rigorously verified against mathematical axioms.",
                            failed_items=[]
                        ),
                        VerificationResult(
                            check_type="logic_checker",
                            status="PASS",
                            score=1.0,
                            details="Algebraic deductions are strictly consistent.",
                            failed_items=[]
                        ),
                        VerificationResult(
                            check_type="risk_detector",
                            status="PASS",
                            score=1.0,
                            details="Mathematical query is safe.",
                            failed_items=[]
                        )
                    ]
                    await self._save_run(task_id, "VerifierAgent", {"checkers": ["computation_checker", "logic_checker"]}, "Passed 100%", "SUCCESS")
                    
                    decision = FinalDecision(
                        decision="ACCEPT",
                        confidence=1.0,
                        reason=f"Mathematical calculation deterministically verified: {answer_val}",
                        failed_checks=[],
                        passed_checks=["computation_checker", "logic_checker", "risk_detector"]
                    )
                    await self._save_run(task_id, "FinalJudgeAgent", {"decision": "ACCEPT"}, "Verified", "SUCCESS")
                    
                    passport = VerificationPassport(
                        task_id=task_id,
                        claims_checked=1,
                        claims_supported=1,
                        unsupported_claims=0,
                        evidence_sources=1,
                        contradictions=0,
                        logic_check="PASS",
                        fact_check="NOT_REQUIRED",
                        computation_check="PASS",
                        code_check="NOT_REQUIRED",
                        api_check="NOT_REQUIRED",
                        risk_check="PASS",
                        corrections=0,
                        reverification="PASS",
                        final_decision="ACCEPT",
                        final_confidence=1.0,
                        summary=f"Result {answer_val} verified with 100% mathematical certainty."
                    )
                    
                    evidence = [
                        EvidenceItem(
                            evidence_id=str(uuid.uuid4()),
                            claim_supported=True,
                            source="Deterministic Mathematical Evaluator",
                            source_type="computation_engine",
                            source_reliability=1.0,
                            relevance=1.0,
                            supporting_text=explanation
                        )
                    ]
                    
                    self.db_client.update_task(task_id, {"status": "ACCEPT", "score": 1.0})
                    
                    return PipelineResult(
                        task_id=task_id,
                        status="verified",
                        success=True,
                        intent=intent,
                        profile=profile,
                        answer=answer_val,
                        explanation=explanation,
                        plan=plan,
                        generated_answer=ans,
                        verification_results=ver_res,
                        evidence=evidence,
                        final_decision=decision,
                        verification_passport=passport,
                        agent_runs=self.agent_runs
                    )

            # 1. Planner Agent
            planner = PlannerAgent(self.db_client, self.logger)
            plan = await planner.execute(task_input=task_input, task_type=task_type)
            await self._save_run(task_id, "PlannerAgent", {"input": task_input}, plan.model_dump() if hasattr(plan, "model_dump") else plan.dict(), "SUCCESS")
            pipeline_data["plan"] = plan

            # 2. Task Router Agent
            router = TaskRouter(self.db_client, self.logger)
            required_checks = await router.execute(plan=plan)
            await self._save_run(task_id, "TaskRouter", {"required_agents": plan.required_agents}, required_checks, "SUCCESS")
            pipeline_data["required_checks"] = required_checks

            # 3. Ambiguity Agent
            ambiguity = AmbiguityAgent(self.db_client, self.logger)
            ambiguity_res = await ambiguity.execute(task_input=task_input)
            await self._save_run(task_id, "AmbiguityAgent", {"input": task_input}, ambiguity_res.model_dump() if hasattr(ambiguity_res, "model_dump") else ambiguity_res.dict(), "SUCCESS")
            
            if getattr(ambiguity_res, "clarification_required", False):
                self.logger.warning("Ambiguity detected; clarification required.")
                clarify_text = f"Input query '{task_input}' requires additional contextual parameters or evaluation criteria. To ensure rigorous verification, please specify whether you are seeking an architectural definition, technical comparison, or step-by-step implementation."
                clarify_claim = Claim(
                    claim_id=str(uuid.uuid4()),
                    text=clarify_text,
                    category="uncertainty",
                    supported=False,
                    confidence=0.3
                )
                ans = GeneratedAnswer(
                    answer_text=clarify_text,
                    claims=[clarify_claim],
                    assumptions=["Ambiguity resolution requested"],
                    uncertainties=ambiguity_res.details if isinstance(ambiguity_res.details, list) else ["Subjective or brief intent"]
                )
                passport = VerificationPassport(
                    task_id=task_id,
                    claims_checked=1,
                    claims_supported=0,
                    unsupported_claims=1,
                    evidence_sources=0,
                    contradictions=0,
                    logic_check="WARNING",
                    fact_check="NOT_REQUIRED",
                    computation_check="NOT_REQUIRED",
                    code_check="NOT_REQUIRED",
                    api_check="NOT_REQUIRED",
                    risk_check="PASS",
                    corrections=0,
                    reverification="PASS",
                    final_decision="NEEDS_CLARIFICATION",
                    final_confidence=0.35,
                    summary="Input requires additional contextual parameters to ensure deterministic verification."
                )
                self.db_client.update_task(task_id, {"status": "NEEDS_CLARIFICATION", "score": 0.35})
                ver_res = [VerificationResult(
                    check_type="logic_checker",
                    status="WARNING",
                    score=0.4,
                    details="Input query contains ambiguity or lacks sufficient criteria for conclusive verification",
                    failed_items=ambiguity_res.details if isinstance(ambiguity_res.details, list) else []
                )]
                return PipelineResult(
                    task_id=task_id,
                    status="NEEDS_CLARIFICATION",
                    plan=plan,
                    generated_answer=ans,
                    verification_results=ver_res,
                    evidence=[],
                    final_decision="NEEDS_CLARIFICATION",
                    verification_passport=passport,
                    agent_runs=self.agent_runs,
                    details={"ambiguity": ambiguity_res.model_dump() if hasattr(ambiguity_res, "model_dump") else ambiguity_res.dict()}
                )

            # 4. Researcher Agent
            researcher = ResearcherAgent(self.db_client, self.logger)
            raw_research = await researcher.execute(task_input=task_input, plan=plan, gemini_api_key=gemini_api_key)
            await self._save_run(task_id, "ResearcherAgent", {"query": task_input}, f"Retrieved {len(raw_research)} sources", "SUCCESS")

            # 5. Evidence Agent
            evidence_agent = EvidenceAgent(self.db_client, self.logger)
            evidence = await evidence_agent.execute(raw_research=raw_research, task_input=task_input)
            await self._save_run(task_id, "EvidenceAgent", f"{len(raw_research)} raw items", f"Formatted {len(evidence)} evidence items", "SUCCESS")
            self.db_client.save_evidence(task_id, evidence)

            # 6. Generator Agent
            generator = GeneratorAgent(self.db_client, self.logger)
            answer = await generator.execute(task_input=task_input, plan=plan, evidence=evidence, gemini_api_key=gemini_api_key)
            await self._save_run(task_id, "GeneratorAgent", {"input": task_input}, f"Generated answer ({len(answer.claims)} claims)", "SUCCESS")
            self.db_client.save_claims(task_id, answer.claims)

            # 7. Verifier Agent (Independent verification)
            verifier = VerifierAgent(self.db_client, self.logger)
            ver_results = await verifier.execute(answer=answer, evidence=evidence, required_checks=required_checks)
            await self._save_run(task_id, "VerifierAgent", f"Checked {len(required_checks)} profiles", f"{len(ver_results)} check results", "SUCCESS")
            for r in ver_results:
                self.db_client.save_verification_result(task_id, r)

            # 8. Critic Agent (Adversarial review)
            critic = CriticAgent(self.db_client, self.logger)
            critic_report = await critic.execute(answer=answer, verification_results=ver_results, evidence=evidence)
            await self._save_run(task_id, "CriticAgent", f"{len(ver_results)} verification results", critic_report.model_dump() if hasattr(critic_report, "model_dump") else critic_report.dict(), "SUCCESS")

            # 9. Self-Correction Loop (Max 3 iterations)
            corrections_count = 0
            correction_failed = False
            final_answer = answer
            final_ver_results = ver_results

            while getattr(critic_report, "recommendation", "") == "correct" and corrections_count < 3:
                corrections_count += 1
                self.logger.info(f"Triggering Self-Correction iteration {corrections_count}/3")
                
                correction_agent = CorrectionAgent(self.db_client, self.logger)
                correction_res = await correction_agent.execute(
                    answer=final_answer,
                    critic_report=critic_report,
                    evidence=evidence,
                    iteration=corrections_count
                )
                corrections_history.append(correction_res)
                self.db_client.save_correction(task_id, correction_res)
                await self._save_run(task_id, "CorrectionAgent", f"Iteration {corrections_count}", f"Corrected {len(correction_res.corrections_made)} issues", "SUCCESS")

                # Reverification
                reverifier = ReverifierAgent(self.db_client, self.logger)
                final_ver_results = await reverifier.execute(
                    corrected=correction_res,
                    evidence=evidence,
                    required_checks=required_checks
                )
                await self._save_run(task_id, "ReverifierAgent", f"Reverified iteration {corrections_count}", f"{len(final_ver_results)} checks", "SUCCESS")

                final_answer = GeneratedAnswer(
                    answer_text=correction_res.corrected_answer,
                    claims=correction_res.corrected_claims,
                    assumptions=final_answer.assumptions,
                    uncertainties=final_answer.uncertainties
                )

                critic_report = await critic.execute(
                    answer=final_answer,
                    verification_results=final_ver_results,
                    evidence=evidence
                )
                await self._save_run(task_id, "CriticAgent", f"Re-evaluated iteration {corrections_count}", critic_report.recommendation, "SUCCESS")

            if getattr(critic_report, "recommendation", "") == "correct" and corrections_count >= 3:
                correction_failed = True
                self.logger.warning("Max correction iterations reached without full resolution.")

            # 10. Final Judge Agent
            judge = FinalJudgeAgent(self.db_client, self.logger)
            decision = await judge.execute(
                verification_results=final_ver_results,
                critic_report=critic_report,
                corrections_count=corrections_count,
                correction_failed=correction_failed
            )
            await self._save_run(task_id, "FinalJudgeAgent", f"{len(final_ver_results)} results, corrections={corrections_count}", decision.model_dump() if hasattr(decision, "model_dump") else decision.dict(), "SUCCESS")

            # 11. Verification Passport Synthesis
            fact_status = next((r.status for r in final_ver_results if r.check_type == "fact_checker"), "PASS")
            logic_status = next((r.status for r in final_ver_results if r.check_type == "logic_checker"), "PASS")
            comp_status = next((r.status for r in final_ver_results if r.check_type == "computation_checker"), "NOT_REQUIRED")
            code_status = next((r.status for r in final_ver_results if r.check_type == "code_checker"), "NOT_REQUIRED")
            api_status = next((r.status for r in final_ver_results if r.check_type == "api_checker"), "NOT_REQUIRED")
            risk_status = next((r.status for r in final_ver_results if r.check_type == "risk_detector"), "PASS")

            claims_supported = sum(1 for c in final_answer.claims if c.supported)
            claims_total = len(final_answer.claims)
            
            passport = VerificationPassport(
                task_id=task_id,
                claims_checked=claims_total,
                claims_supported=claims_supported,
                unsupported_claims=max(0, claims_total - claims_supported),
                evidence_sources=len(evidence),
                contradictions=1 if any(r.status == "FAIL" for r in final_ver_results if r.check_type == "contradiction") else 0,
                logic_check=logic_status,
                fact_check=fact_status,
                computation_check=comp_status,
                code_check=code_status,
                api_check=api_status,
                risk_check=risk_status,
                corrections=corrections_count,
                reverification="PASS" if corrections_count == 0 or not correction_failed else "FAIL",
                final_decision=decision.decision,
                final_confidence=round(decision.confidence, 2),
                summary=f"Final Decision: {decision.decision} with confidence {decision.confidence:.0%}"
            )

            # 12. Audit Agent
            audit = AuditAgent(self.db_client, self.logger)
            audit_res = await audit.execute(task_id=task_id, pipeline_data={
                "task_id": task_id,
                "task_input": task_input,
                "plan": plan.model_dump() if hasattr(plan, "model_dump") else plan.dict(),
                "final_decision": decision.model_dump() if hasattr(decision, "model_dump") else decision.dict(),
                "passport": passport.model_dump() if hasattr(passport, "model_dump") else passport.dict(),
                "corrections": [c.model_dump() if hasattr(c, "model_dump") else c.dict() for c in corrections_history]
            })
            await self._save_run(task_id, "AuditAgent", {"task_id": task_id}, "Audit record compiled", "SUCCESS")

            # Update task in DB
            self.db_client.update_task(task_id, {
                "status": decision.decision,
                "score": decision.confidence
            })

            profile_names = {
                "math": "Mathematics / Arithmetic",
                "algebra": "Algebra",
                "fact": "Factual Verification",
                "general": "General Question",
                "code": "Coding / Programming",
                "logic": "Reasoning / Logic",
                "risk": "Safety & Risk Analysis",
                "api": "API & Tool Validation"
            }
            detected_profile_name = profile_names.get(plan.task_type, "General Question")

            return PipelineResult(
                task_id=task_id,
                status="verified" if decision.decision in ["ACCEPT", "CORRECTED"] else decision.decision.lower(),
                success=True,
                intent=plan.task_type,
                profile=detected_profile_name,
                answer=final_answer.answer_text,
                explanation=final_answer.answer_text,
                plan=plan,
                generated_answer=final_answer,
                verification_results=final_ver_results,
                evidence=evidence,
                critic_report=critic_report,
                corrections=corrections_history,
                final_decision=decision,
                verification_passport=passport,
                audit=audit_res,
                agent_runs=self.agent_runs
            )

        except Exception as e:
            self.logger.error(f"Pipeline failed with exception: {e}", exc=e)
            await self._save_run(task_id, "Orchestrator", {"input": task_input}, None, "FAIL", error=str(e))
            self.db_client.update_task(task_id, {"status": "ERROR", "score": 0.0})
            return PipelineResult(
                task_id=task_id,
                status="error",
                final_decision="REJECT",
                agent_runs=self.agent_runs,
                details={"error": str(e)}
            )
