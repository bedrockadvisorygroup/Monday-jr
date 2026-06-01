from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db, ProjectStatusEnum
from ..models import ClientProject, AgentOutput
from ..utils import can_run_stage, get_approved_status

router = APIRouter(prefix="/projects", tags=["Approvals"])

class ApprovalPayload(BaseModel):
    stage_name: str
    decision: str
    reviewer_name: str
    reviewer_notes: str

@router.post("/{project_id}/approve", status_code=status.HTTP_200_OK)
def approve_stage(project_id: int, payload: ApprovalPayload, db: Session = Depends(get_db)):
    """Approve a completed stage (e.g., discovery, research)."""
    project = db.query(ClientProject).filter(ClientProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # For now we only handle "approved" decisions
    if payload.decision.lower() != "approved":
        raise HTTPException(status_code=400, detail="Only 'approved' decision is supported")

    # Optional: verify stage can be approved based on current status
    # Allow approval if the requested stage matches the project's pending status
    if not can_run_stage(project.status, payload.stage_name):
        raise HTTPException(status_code=400, detail="Stage cannot be approved at current project status")

    # Update project status to the approved state for the stage
    project.status = get_approved_status(payload.stage_name)
    db.commit()
    db.refresh(project)
    return {
        "project_id": project.id,
        "stage": payload.stage_name,
        "status": project.status,
        "message": f"{payload.stage_name} approved by {payload.reviewer_name}",
    }

@router.get("/{project_id}/approvals")
def list_approvals(project_id: int, db: Session = Depends(get_db)):
    """Return a list of approval AgentOutputs for the project (if any)."""
    outputs = (
        db.query(AgentOutput)
        .filter(AgentOutput.project_id == project_id, AgentOutput.stage_name.in_(["discovery", "research", "analysis"]))
        .order_by(AgentOutput.created_at.desc())
        .all()
    )
    return [
        {
            "stage": out.stage_name,
            "status": out.approved_status,
            "output_title": out.output_title,
            "created_at": out.created_at,
        }
        for out in outputs
    ]
