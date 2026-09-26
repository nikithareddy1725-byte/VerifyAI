import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database.supabase_client import SupabaseClient
from models.schemas import TaskRequest, PipelineResult
from agents.orchestrator import Orchestrator

app = FastAPI(title="VerifyAI - Multi-Agent Verification Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_client = SupabaseClient()
orchestrator = Orchestrator(db_client=db_client)

@app.post("/api/verify", response_model=PipelineResult)
async def verify_task(request: TaskRequest):
    try:
        input_text = (request.input_text or request.query or "").strip()
        if not input_text:
            raise HTTPException(status_code=400, detail="Please enter a question or task.")
        result = await orchestrator.execute(
            task_input=input_text,
            task_type=request.task_type or "auto",
            gemini_api_key=request.gemini_api_key
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/verify/{task_id}/retry", response_model=PipelineResult)
async def retry_task(task_id: str):
    task = db_client.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        result = await orchestrator.execute(task_input=task.get("input_text", ""), task_type=task.get("task_type", "general"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task/{task_id}")
async def get_task(task_id: str):
    task = db_client.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/api/audit/{task_id}")
async def get_audit(task_id: str):
    audit = db_client.get_audit(task_id)
    if not audit:
        # Fallback to returning agent runs as audit
        runs = db_client.get_agent_runs(task_id)
        if runs:
            return {"task_id": task_id, "agent_runs": runs}
        raise HTTPException(status_code=404, detail="Audit log not found")
    return audit

@app.get("/api/evidence/{task_id}")
async def get_evidence(task_id: str):
    return db_client.get_evidence(task_id)

@app.get("/api/agents/{task_id}")
async def get_agents(task_id: str):
    return db_client.get_agent_runs(task_id)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "VerifyAI Multi-Agent Verification Engine",
        "version": "1.0.0"
    }

@app.get("/api/stats")
async def get_stats():
    return db_client.get_stats()

@app.get("/api/config/gemini")
async def get_gemini_config():
    key = os.getenv("GEMINI_API_KEY", "")
    has_key = bool(key and key.strip())
    preview = f"{key[:6]}...{key[-4:]}" if has_key and len(key) > 10 else ("Configured" if has_key else "None")
    return {
        "configured": has_key,
        "preview": preview,
        "model": "gemini-2.5-flash"
    }

@app.post("/api/config/gemini")
async def set_gemini_config(data: dict):
    new_key = data.get("api_key", "").strip()
    if new_key:
        os.environ["GEMINI_API_KEY"] = new_key
        # Persist to .env
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        try:
            lines = []
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("GEMINI_API_KEY="):
                    lines[i] = f"GEMINI_API_KEY={new_key}\n"
                    updated = True
                    break
            if not updated:
                lines.append(f"GEMINI_API_KEY={new_key}\n")
                
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as e:
            pass
        return {"status": "success", "message": "Gemini API Key activated and persisted!"}
    else:
        os.environ.pop("GEMINI_API_KEY", None)
        return {"status": "cleared", "message": "Gemini API Key cleared. Local engine active."}

# Serve frontend static files directly from port 8000
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if not os.path.exists(os.path.join(frontend_dir, "index.html")):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(frontend_dir) and os.path.exists(os.path.join(frontend_dir, "index.html")):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    @app.get("/")
    async def serve_index():
        response = FileResponse(os.path.join(frontend_dir, "index.html"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

