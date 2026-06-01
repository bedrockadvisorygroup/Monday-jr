from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path

from ..database import get_db, ProjectStatusEnum
from ..models import ClientProject, AgentOutput, GeneratedFile
from ..utils import can_run_stage

router = APIRouter(prefix="/analysis", tags=["Analysis"])

# Placeholder analysis markdown template
ANALYSIS_TEMPLATE = """# Analysis Brief

## 1. Executive Summary

*Placeholder content*

## 2. Key Findings from Research

*Placeholder content*

## 3. Problem Diagnosis

*Placeholder content*

## 4. Market / Business Implications

*Placeholder content*

## 5. SWOT Snapshot

*Placeholder content*

## 6. Financial / Operational Considerations

*Placeholder content*

## 7. Strategic Options

*Placeholder content*

## 8. Risks

*Placeholder content*

## 9. Assumptions

*Placeholder content*

## 10. Limitations

*Placeholder content*

## 11. Recommended Next Step

*Placeholder content*
"""

@router.post("/{project_id}/run", status_code=status.HTTP_201_CREATED)
def run_analysis(project_id: int, db: Session = Depends(get_db)):
    """Run the analysis stage for a project after research approval."""
    # Fetch project
    project = db.query(ClientProject).filter(ClientProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Stage gate check
    if not can_run_stage(project.status, "analysis"):
        raise HTTPException(status_code=400, detail="Analysis stage cannot be run at current project status")

    # Ensure there is a research output (latest)
    research_output = (
        db.query(AgentOutput)
        .filter(AgentOutput.project_id == project_id, AgentOutput.stage_name == "research")
        .order_by(AgentOutput.created_at.desc())
        .first()
    )
    if not research_output:
        raise HTTPException(status_code=404, detail="Research output not found for analysis")

    # Generate markdown output (placeholder)
    markdown_output = ANALYSIS_TEMPLATE

    # Save markdown file
    analysis_dir = Path(project.project_folder_path) / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    file_name = "analysis_brief.md"
    file_path = analysis_dir / file_name
    file_path.write_text(markdown_output, encoding="utf-8")

    # Create AgentOutput record
    agent_output = AgentOutput(
        project_id=project.id,
        agent_name="tuesday_analysis_agent",
        stage_name="analysis",
        output_title="Analysis Brief",
        output_type="markdown",
        markdown_output=markdown_output,
        assumptions="",
        limitations="",
        sources_used="Research output",
        confidence_level="medium",
        approved_status="pending",
    )
    db.add(agent_output)

    # Create GeneratedFile record
    generated_file = GeneratedFile(
        project_id=project.id,
        stage_name="analysis",
        file_type="markdown",
        file_name=file_name,
        file_path=str(file_path),
        created_by_agent="tuesday_analysis_agent",
    )
    db.add(generated_file)

    # Update project status
    project.status = ProjectStatusEnum.ANALYSIS_PENDING
    db.commit()
    db.refresh(agent_output)
    return {
        "project_id": project.id,
        "stage": "analysis",
        "output_title": agent_output.output_title,
        "markdown_output": agent_output.markdown_output,
    }

@router.get("/{project_id}")
def get_latest_analysis(project_id: int, db: Session = Depends(get_db)):
    """Retrieve the latest analysis output for a project."""
    output = (
        db.query(AgentOutput)
        .filter(AgentOutput.project_id == project_id, AgentOutput.stage_name == "analysis")
        .order_by(AgentOutput.created_at.desc())
        .first()
    )
    if not output:
        raise HTTPException(status_code=404, detail="Analysis output not found")
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
