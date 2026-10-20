from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import uuid
from agent.core.agent import RemediationAgent
from agent.audit.audit_logger import AuditLogger

app = FastAPI(title="OmniRoute AIOps Control Plane")
agent_engine = RemediationAgent()
logger = AuditLogger()

# In-memory store for pending approvals (In production, use Redis/Postgres)
pending_remediations = {}

class AlertRequest(BaseModel):
    alert_id: str
    cluster_id: str = "default-cluster"

class ApprovalRequest(BaseModel):
    request_id: str
    action: str # "approve" or "reject"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "active"}

@app.post("/trigger-diagnosis")
async def trigger_diagnosis(request: AlertRequest, background_tasks: BackgroundTasks):
    """Starts the AI diagnosis process."""
    request_id = str(uuid.uuid4())

    # Start the agent in the background
    background_tasks.add_task(run_agent_pipeline, request_id, request.alert_id)

    return {"request_id": request_id, "status": "Diagnosis started"}

async def run_agent_pipeline(request_id: str, alert_id: str):
    """Runs the LangGraph pipeline and stores the result for approval."""
    # We modify the agent to stop at the 'decision' phase and wait for approval
    # For the demo, we simulate the state progression
    result = agent_engine.run(alert_id)

    # Store the suggested fix for the UI to display
    pending_remediations[request_id] = {
        "alert_id": alert_id,
        "context": result.get("context"),
        "suggested_fix": result.get("suggested_fix"),
        "decision": result.get("decision"),
        "status": "pending_approval"
    }
    logger.log_action(alert_id, result)

@app.get("/pending-approvals")
async def get_approvals():
    """Returns all fixes awaiting human approval."""
    return pending_remediations

@app.post("/approve-remediation")
async def approve_remediation(request: ApprovalRequest):
    """Approves the AI fix and triggers the GitOps push."""
    if request.request_id not in pending_remediations:
        raise HTTPException(status_code=404, detail="Request not found")

    item = pending_remediations[request.request_id]

    if request.action == "approve":
        # Trigger the actual fix
        result = agent_engine.execute_remediation({"suggested_fix": item["suggested_fix"]})
        item["status"] = "executed"
        item["action_result"] = result
    else:
        item["status"] = "rejected"

    return {"status": "success", "final_state": item["status"]}
