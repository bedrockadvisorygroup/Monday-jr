# backend/routers/lead_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from ..database import get_db, ProjectStatusEnum
from ..models import Lead, ClientProject, LeadMagnet
from ..utils import safe_project_name, create_project_folders

router = APIRouter(prefix="/leads", tags=["Leads"])

class LeadCreate(BaseModel):
    name: str
    company_name: str
    industry: str
    stage: str
    geography: str
    website_url: Optional[str] = None
    founder_name: Optional[str] = None

class LeadResponse(BaseModel):
    id: int
    name: str
    company_name: str
    industry: str
    stage: str
    geography: str
    website_url: Optional[str]
    founder_name: Optional[str]
    status: str
    folder_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str

@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    """Create a new qualified lead in Monday Jr."""
    lead = Lead(
        name=payload.name,
        company_name=payload.company_name,
        industry=payload.industry,
        stage=payload.stage,
        geography=payload.geography,
        website_url=payload.website_url,
        founder_name=payload.founder_name,
        status="draft"
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.get("", response_model=List[LeadResponse])
def list_leads(db: Session = Depends(get_db)):
    """List all qualified leads in the system."""
    return db.query(Lead).order_by(Lead.created_at.desc()).all()

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Retrieve details of a single lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.put("/{lead_id}/status", response_model=LeadResponse)
def update_lead_status(lead_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    """Update pipeline status of a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    valid_statuses = ["draft", "needs_review", "approved", "used_in_outreach", "converted", "archived"]
    if payload.status.lower() not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
        
    lead.status = payload.status.lower()
    db.commit()
    db.refresh(lead)
    return lead

@router.post("/{lead_id}/convert")
def convert_lead_to_project(lead_id: int, db: Session = Depends(get_db)):
    """Tuesday Jr Handoff: Convert lead into an active Client Project."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Fetch latest lead magnet for outline details if it exists
    magnet = db.query(LeadMagnet).filter(LeadMagnet.lead_id == lead_id).order_by(LeadMagnet.created_at.desc()).first()

    # Create folder structure using existing backend utilities
    folder_path = create_project_folders(lead.company_name)
    lead.folder_path = folder_path
    lead.status = "converted"

    # Assemble handoff_package.md content (strictly non-overclaiming)
    hook = magnet.opening_hook if magnet else "N/A"
    hypothesis = magnet.problem_hypothesis if magnet else "N/A"
    agenda = magnet.discovery_agenda if magnet else "N/A"

    handoff_content = f"""# Monday Jr to Tuesday Jr Handoff Brief

## 1. Executive Summary
This project was successfully qualified and converted by Monday Jr.
* **Lead Company:** {lead.company_name}
* **Industry:** {lead.industry}
* **Stage:** {lead.stage}
* **Geography:** {lead.geography}
* **Founder Name:** {lead.founder_name or "N/A"}
* **Website:** {lead.website_url or "N/A"}
* **Conversion Time:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

---

## 2. Pre-Meeting Hypotheses (Based on Public Signals)
The following pain-point hypotheses were mapped to Bedrock's solution catalog for this lead:

### Mapped Opportunity Area
{hypothesis}

### Winning Outreach Hook
> "{hook}"

---

## 3. Discovery Meeting Agenda
{agenda}

---

## 4. Tuesday Jr Diagnostics Next Steps
> [!IMPORTANT]
> Tuesday Jr should validate these hypotheses during the Discovery stage, collect private operational benchmarks from the client, and initiate structural financial/operational modeling.
"""

    # Save to inputs/handoff_package.md inside the client's new folder
    inputs_dir = Path(folder_path) / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = inputs_dir / "handoff_package.md"
    file_path.write_text(handoff_content, encoding="utf-8")

    # Instantiate the ClientProject record
    project = ClientProject(
        name=f"Monday Jr Handoff: {lead.company_name}",
        client_name=lead.founder_name or "N/A",
        industry=lead.industry,
        website_url=lead.website_url,
        location=lead.geography,
        description=f"Handoff from Lead Magnet Studio for {lead.company_name}. Initial hypotheses: {hypothesis[:250]}...",
        notes="Lead successfully converted from pre-meeting sales outreach.",
        status=ProjectStatusEnum.DISCOVERY_PENDING.value,
        project_folder_path=folder_path
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "message": f"Lead successfully converted to Client Project",
        "lead_id": lead.id,
        "lead_status": lead.status,
        "project_id": project.id,
        "project_status": project.status,
        "project_folder_path": project.project_folder_path,
        "handoff_package_path": str(file_path)
    }
