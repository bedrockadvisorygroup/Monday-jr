# backend/utils.py
import os
import re
from pathlib import Path
from typing import List

from .database import ProjectStatusEnum

def safe_project_name(project_name: str) -> str:
    """Convert a project name into a safe filesystem folder name.

    Steps:
    - Lowercase
    - Replace whitespace/hyphens with underscores
    - Remove non‑alphanumeric characters
    - Collapse multiple underscores
    - Strip leading/trailing underscores
    """
    name = project_name.strip().lower()
    name = re.sub(r"[\s\-]+", "_", name)
    name = re.sub(r"[^a-z0-9_]+", "", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")

def create_project_folders(project_name: str) -> str:
    """Create the folder hierarchy for a new project.

    Returns the absolute path to the root project folder.
    """
    safe_name = safe_project_name(project_name)
    base_dir = Path(__file__).resolve().parent.parent / "clients" / safe_name
    subfolders = [
        "inputs",
        "discovery",
        "research",
        "analysis",
        "charts",
        "valuation",
        "recommendations",
        "decks",
        "validation",
        "final_delivery",
    ]
    for folder in subfolders:
        (base_dir / folder).mkdir(parents=True, exist_ok=True)
    return str(base_dir)

def can_run_stage(current_status: str, requested_stage: str) -> bool:
    """Determine if a stage can be executed given the current project status."""
    allowed_transitions = {
        "discovery": {ProjectStatusEnum.DISCOVERY_PENDING.value},
        "research": {ProjectStatusEnum.DISCOVERY_APPROVED.value, ProjectStatusEnum.RESEARCH_PENDING.value},
        "analysis": {ProjectStatusEnum.RESEARCH_APPROVED.value, ProjectStatusEnum.ANALYSIS_PENDING.value},
        "recommendation": {ProjectStatusEnum.ANALYSIS_COMPLETE.value, ProjectStatusEnum.RECOMMENDATION_PENDING.value},
        "deck": {ProjectStatusEnum.RECOMMENDATION_COMPLETE.value, ProjectStatusEnum.DECK_PENDING.value},
        "final_delivery": {ProjectStatusEnum.DECK_COMPLETE.value, ProjectStatusEnum.FINAL_DELIVERY_PENDING.value},
    }
    allowed = allowed_transitions.get(requested_stage.lower())
    return bool(allowed and current_status in allowed)

def get_next_pending_status(stage_name: str) -> str:
    """Return the pending status constant for a given stage name."""
    mapping = {
        "discovery": ProjectStatusEnum.DISCOVERY_PENDING.value,
        "research": ProjectStatusEnum.RESEARCH_PENDING.value,
        "analysis": ProjectStatusEnum.ANALYSIS_PENDING.value,
        "recommendation": ProjectStatusEnum.RECOMMENDATION_PENDING.value,
        "deck": ProjectStatusEnum.DECK_PENDING.value,
        "final_delivery": ProjectStatusEnum.FINAL_DELIVERY_PENDING.value,
    }
    return mapping.get(stage_name.lower(), "")

def get_approved_status(stage_name: str) -> str:
    """Return the approved status constant for a given stage name."""
    mapping = {
        "discovery": ProjectStatusEnum.DISCOVERY_APPROVED.value,
        "research": ProjectStatusEnum.RESEARCH_APPROVED.value,
        "analysis": ProjectStatusEnum.ANALYSIS_APPROVED.value,
        "recommendation": ProjectStatusEnum.RECOMMENDATION_APPROVED.value,
        "deck": ProjectStatusEnum.DECK_APPROVED.value,
        "final_delivery": ProjectStatusEnum.FINAL_DELIVERY_COMPLETE.value,
    }
    return mapping.get(stage_name.lower(), "")
