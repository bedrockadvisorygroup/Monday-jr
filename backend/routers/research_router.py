# backend/routers/research_router.py

from fastapi import APIRouter, status

router = APIRouter(prefix="/research", tags=["Research"])

@router.post("/{project_id}/run", status_code=status.HTTP_201_CREATED)
def run_research(project_id: int):
    # Placeholder implementation for running research stage
    return {"project_id": project_id, "stage": "research", "message": "research run placeholder"}

@router.get("/{project_id}")
def get_research(project_id: int):
    # Example markdown output using f-string without escaped quotes
    description = "N/A"
    notes = "N/A"
    markdown = f"# Research Output\n\n**Project ID:** {project_id}\n\n**Description:** {description}\n\n**Notes:** {notes}\n"
    return {"project_id": project_id, "stage": "research", "output": markdown}
