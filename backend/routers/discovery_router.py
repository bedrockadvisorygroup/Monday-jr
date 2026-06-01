from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime

from ..database import get_db, ProjectStatusEnum
from ..models import ClientProject, AgentOutput, GeneratedFile
from ..utils import can_run_stage, get_next_pending_status

router = APIRouter(prefix="/discovery", tags=["Discovery"])

# Placeholder discovery markdown template
DISCOVERY_TEMPLATE = """# Discovery & Scoping Brief

## 1. Client Background

*Placeholder content*

## 2. Initial Problem Statement

*Placeholder content*

## 3. Business Context

*Placeholder content*

## 4. Key Pain Points

*Placeholder content*

## 5. Proposed Workstreams

*Placeholder content*

## 6. Data Required

*Placeholder content*

## 7. Risks and Assumptions

*Placeholder content*

## 8. Recommended Next Step

*Placeholder content*

## 9. Limitations

*Placeholder content*
"""

@router.post("/{project_id}/run", status_code=status.HTTP_201_CREATED)
def run_discovery(project_id: int, db: Session = Depends(get_db)):
    # Fetch project
    project = db.query(ClientProject).filter(ClientProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Stage gate check
    if not can_run_stage(project.status, "discovery"):
        raise HTTPException(status_code=400, detail="Discovery stage cannot be run at current project status")

    # Generate markdown output
    markdown_output = DISCOVERY_TEMPLATE

    # Save markdown file to project folder
    discovery_dir = Path(project.project_folder_path) / "discovery"
    discovery_dir.mkdir(parents=True, exist_ok=True)
    file_name = "discovery_brief.md"
    file_path = discovery_dir / file_name
    file_path.write_text(markdown_output, encoding="utf-8")

    # Create AgentOutput record
    agent_output = AgentOutput(
        project_id=project.id,
        agent_name="thursday_discovery_agent",
        stage_name="discovery",
        output_title="Discovery & Scoping Brief",
        output_type="markdown",
        markdown_output=markdown_output,
        assumptions="",
        limitations="",
        sources_used="",
        confidence_level="medium",
        approved_status="pending",
    )
    db.add(agent_output)

    # Create GeneratedFile record
    generated_file = GeneratedFile(
        project_id=project.id,
        stage_name="discovery",
        file_type="markdown",
        file_name=file_name,
        file_path=str(file_path),
        created_by_agent="thursday_discovery_agent",
    )
    db.add(generated_file)

    # Update project status
    project.status = ProjectStatusEnum.DISCOVERY_PENDING.value
    db.commit()
    db.refresh(agent_output)
    return {
        "project_id": project.id,
        "stage": "discovery",
        "output_title": agent_output.output_title,
        "markdown_output": agent_output.markdown_output,
    }

@router.get("/{project_id}")
def get_latest_discovery(project_id: int, db: Session = Depends(get_db)):

    output = (
        db.query(AgentOutput)
        .filter(AgentOutput.project_id == project_id, AgentOutput.stage_name == "discovery")
        .order_by(AgentOutput.created_at.desc())
        .first()
    )
    if not output:
        raise HTTPException(status_code=404, detail="Discovery output not found")
    return {
        "project_id": output.project_id,
        "stage": output.stage_name,
        "output_title": output.output_title,
        "markdown_output": output.markdown_output,
        "assumptions": output.assumptions,
        "limitations": output.limitations,
        "sources_used": output.sources_used,
        "confidence_level": output.confidence_level,
        "approved_status": output.approved_status,
    }
