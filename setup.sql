-- =============================================================================
-- VerifyAI: Complete Supabase PostgreSQL Schema
-- =============================================================================
-- This schema provisions all tables, constraints, indexes, triggers,
-- and Row Level Security (RLS) policies for the VerifyAI Multi-Agent Verification Platform.
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- Clean up existing tables in reverse dependency order
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS tool_tests CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS corrections CASCADE;
DROP TABLE IF EXISTS verification_results CASCADE;
DROP TABLE IF EXISTS claims CASCADE;
DROP TABLE IF EXISTS evidence CASCADE;
DROP TABLE IF EXISTS agent_runs CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;

-- -----------------------------------------------------------------------------
-- 1. TABLE: tasks
-- Central task record storing the user query, workflow status, planning,
-- final decisions, and the generated Verification Passport.
-- -----------------------------------------------------------------------------
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    input_text TEXT NOT NULL,
    task_type VARCHAR(50) DEFAULT 'general',
    status VARCHAR(50) DEFAULT 'pending',
    score FLOAT,
    plan JSONB,
    final_decision JSONB,
    verification_passport JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 2. TABLE: agent_runs
-- Detailed telemetry for each agent invoked during the verification workflow.
-- -----------------------------------------------------------------------------
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    agent_icon VARCHAR(10),
    action TEXT,
    status VARCHAR(50),
    step_order INT,
    input_summary TEXT DEFAULT '',
    output_summary TEXT DEFAULT '',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error TEXT
);

-- -----------------------------------------------------------------------------
-- 3. TABLE: evidence
-- Corpus of evidence snippets retrieved by retriever agents or tools.
-- -----------------------------------------------------------------------------
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    evidence_id VARCHAR(100) NOT NULL,
    claim_supported TEXT,
    source TEXT,
    source_type VARCHAR(50),
    source_reliability FLOAT DEFAULT 1.0,
    relevance FLOAT DEFAULT 1.0,
    supporting_text TEXT,
    timestamp VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 4. TABLE: claims
-- Atomic fact claims extracted from candidate responses and their verification status.
-- -----------------------------------------------------------------------------
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    claim_id VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    category VARCHAR(50),
    supported BOOLEAN DEFAULT false,
    evidence_ids JSONB DEFAULT '[]'::jsonb,
    confidence FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 5. TABLE: verification_results
-- Granular scores and outcome breakdowns for each of the 9 verification checkers.
-- -----------------------------------------------------------------------------
CREATE TABLE verification_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    check_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    score FLOAT DEFAULT 0.0,
    details TEXT,
    failed_items JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 6. TABLE: corrections
-- Tracking iterations of the self-correction engine when verifiers flag issues.
-- -----------------------------------------------------------------------------
CREATE TABLE corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    original_answer TEXT,
    corrected_answer TEXT,
    corrections_made JSONB DEFAULT '[]'::jsonb,
    iteration INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 7. TABLE: audit_log
-- Immutable end-to-end provenance log preserving the entire run trace.
-- -----------------------------------------------------------------------------
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    task_type VARCHAR(50),
    plan JSONB,
    agents_executed JSONB DEFAULT '[]'::jsonb,
    agent_outputs JSONB DEFAULT '{}'::jsonb,
    evidence JSONB DEFAULT '[]'::jsonb,
    claims_data JSONB DEFAULT '[]'::jsonb,
    verification_scores JSONB DEFAULT '{}'::jsonb,
    contradictions JSONB DEFAULT '[]'::jsonb,
    corrections JSONB DEFAULT '[]'::jsonb,
    iterations INT DEFAULT 0,
    final_decision VARCHAR(50),
    confidence FLOAT DEFAULT 0.0,
    rejection_reason TEXT,
    timestamps JSONB DEFAULT '{}'::jsonb,
    tool_tests JSONB DEFAULT '[]'::jsonb,
    verification_passport JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 8. TABLE: tool_tests
-- Execution results from code sandbox executions, AST audits, and tool calls.
-- -----------------------------------------------------------------------------
CREATE TABLE tool_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL,
    input TEXT,
    expected_output TEXT,
    actual_output TEXT,
    passed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Indexes for High Performance Queries
-- -----------------------------------------------------------------------------
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_status ON tasks(status);

CREATE INDEX idx_agent_runs_task_id ON agent_runs(task_id);
CREATE INDEX idx_agent_runs_created_at ON agent_runs(started_at DESC);

CREATE INDEX idx_evidence_task_id ON evidence(task_id);
CREATE INDEX idx_evidence_created_at ON evidence(created_at DESC);

CREATE INDEX idx_claims_task_id ON claims(task_id);
CREATE INDEX idx_claims_created_at ON claims(created_at DESC);

CREATE INDEX idx_verification_results_task_id ON verification_results(task_id);
CREATE INDEX idx_verification_results_created_at ON verification_results(created_at DESC);

CREATE INDEX idx_corrections_task_id ON corrections(task_id);
CREATE INDEX idx_corrections_created_at ON corrections(created_at DESC);

CREATE INDEX idx_audit_log_task_id ON audit_log(task_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC);

CREATE INDEX idx_tool_tests_task_id ON tool_tests(task_id);
CREATE INDEX idx_tool_tests_created_at ON tool_tests(created_at DESC);

-- -----------------------------------------------------------------------------
-- Updated_At Trigger Function
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION set_updated_at_timestamp();

-- -----------------------------------------------------------------------------
-- Row Level Security (RLS) Configuration
-- Enable RLS and define permissive policies for public client & server access.
-- -----------------------------------------------------------------------------
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE corrections ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_tests ENABLE ROW LEVEL SECURITY;

-- 1. Tasks Policies
CREATE POLICY "Public full access on tasks"
ON tasks FOR ALL
USING (true)
WITH CHECK (true);

-- 2. Agent Runs Policies
CREATE POLICY "Public full access on agent_runs"
ON agent_runs FOR ALL
USING (true)
WITH CHECK (true);

-- 3. Evidence Policies
CREATE POLICY "Public full access on evidence"
ON evidence FOR ALL
USING (true)
WITH CHECK (true);

-- 4. Claims Policies
CREATE POLICY "Public full access on claims"
ON claims FOR ALL
USING (true)
WITH CHECK (true);

-- 5. Verification Results Policies
CREATE POLICY "Public full access on verification_results"
ON verification_results FOR ALL
USING (true)
WITH CHECK (true);

-- 6. Corrections Policies
CREATE POLICY "Public full access on corrections"
ON corrections FOR ALL
USING (true)
WITH CHECK (true);

-- 7. Audit Log Policies
CREATE POLICY "Public full access on audit_log"
ON audit_log FOR ALL
USING (true)
WITH CHECK (true);

-- 8. Tool Tests Policies
CREATE POLICY "Public full access on tool_tests"
ON tool_tests FOR ALL
USING (true)
WITH CHECK (true);
