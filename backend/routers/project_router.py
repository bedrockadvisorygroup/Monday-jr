from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import os

from ..database import get_db, ProjectStatusEnum
from ..models import ClientProject, ProjectFile, AgentOutput, GeneratedFile
from ..utils import create_project_folders, safe_project_name

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(payload: dict, db: Session = Depends(get_db)):
    """Create a new project and its folder structure.
    Expected payload keys: name, client_name, industry, website_url, location, description, notes
    """
    required = ["name", "client_name", "industry", "location"]
    for key in required:
        if key not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing field {key}")
    project = ClientProject(
        name=payload["name"],
        client_name=payload["client_name"],
        industry=payload["industry"],
        website_url=payload.get("website_url"),
        location=payload["location"],
        description=payload.get("description"),
        notes=payload.get("notes"),
        status=ProjectStatusEnum.DISCOVERY_PENDING.value,
    )
    # create folder hierarchy
    folder_path = create_project_folders(project.name)
    project.project_folder_path = folder_path
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"id": project.id, "folder": folder_path}

@router.get("/", response_model=list)
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(ClientProject).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "client_name": p.client_name,
            "status": p.status,
        }
        for p in projects
    ]

@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ClientProject).filter(ClientProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return {
        "id": project.id,
        "name": project.name,
        "client_name": project.client_name,
        "industry": project.industry,
        "website_url": project.website_url,
        "location": project.location,
        "description": project.description,
        "notes": project.notes,
        "status": project.status,
        "folder": project.project_folder_path,
    }

@router.post("/{project_id}/upload", status_code=status.HTTP_201_CREATED)
def upload_file(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    project = db.query(ClientProject).filter(ClientProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if not project.project_folder_path:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Project folder missing")
    inputs_dir = os.path.join(project.project_folder_path, "inputs")
    os.makedirs(inputs_dir, exist_ok=True)
    file_path = os.path.join(inputs_dir, file.filename)
    with open(file_path, "wb") as out:
        out.write(file.file.read())
    pf = ProjectFile(
        project_id=project.id,
        filename=file.filename,
        file_path=file_path,
        uploaded_at=datetime.utcnow(),
    )
    db.add(pf)
    db.commit()
    db.refresh(pf)
    return {"file_id": pf.id, "filename": pf.filename}

@router.get("/{project_id}/outputs")
def get_project_outputs(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ClientProject).filter(ClientProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    outputs = db.query(AgentOutput).filter(AgentOutput.project_id == project_id).all()
    return [
        {
            "id": o.id,
            "stage": o.stage_name,
            "title": o.output_title,
            "type": o.output_type,
            "created_at": o.created_at,
        }
        for o in outputs
    ]
