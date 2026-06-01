# backend/routers/knowledge_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import KnowledgeItem, IndustryBenchmark, PainPointPattern

router = APIRouter(prefix="/knowledge", tags=["Shared Knowledge Library"])

class KnowledgeItemCreate(BaseModel):
    title: str
    source_agent: str
    category: str
    content: str
    reuse_permission: Optional[str] = "reusable"

class KnowledgeItemResponse(BaseModel):
    id: int
    title: str
    source_agent: str
    category: str
    content: str
    reuse_permission: str
    created_at: datetime

    class Config:
        from_attributes = True

class IndustryBenchmarkResponse(BaseModel):
    id: int
    industry: str
    dimension: str
    industry_standard: str
    market_leader: str
    recommendation_playbook: Optional[str]

    class Config:
        from_attributes = True

class PainPointPatternResponse(BaseModel):
    id: int
    category: str
    typical_signals: Optional[str]
    diagnostic_questions: Optional[str]
    bedrock_service_fit: str

    class Config:
        from_attributes = True

@router.post("", response_model=KnowledgeItemResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_item(payload: KnowledgeItemCreate, db: Session = Depends(get_db)):
    """Add a validated learning, outline, or playbook to the Shared Knowledge Library."""
    valid_permissions = ["reusable", "confidential", "client_specific_only", "do_not_reuse"]
    if payload.reuse_permission.lower() not in valid_permissions:
        raise HTTPException(status_code=400, detail=f"Invalid reuse_permission. Must be one of {valid_permissions}")

    item = KnowledgeItem(
        title=payload.title,
        source_agent=payload.source_agent,
        category=payload.category.lower(),
        content=payload.content,
        reuse_permission=payload.reuse_permission.lower()
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("", response_model=List[KnowledgeItemResponse])
def list_knowledge_items(
    category: Optional[str] = None, 
    reuse_permission: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """Retrieve shared learnings, playbooks, and templates from the library."""
    query = db.query(KnowledgeItem)
    if category:
        query = query.filter(KnowledgeItem.category == category.lower())
    if reuse_permission:
        query = query.filter(KnowledgeItem.reuse_permission == reuse_permission.lower())
    return query.order_by(KnowledgeItem.created_at.desc()).all()

@router.get("/benchmarks", response_model=List[IndustryBenchmarkResponse])
def get_industry_benchmarks(industry: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieve pre-seeded industry benchmarks for SaaS, Retail, Healthcare, etc."""
    query = db.query(IndustryBenchmark)
    if industry:
        query = query.filter(IndustryBenchmark.industry.ilike(industry))
    return query.all()

@router.get("/pain-points", response_model=List[PainPointPatternResponse])
def get_pain_point_patterns(db: Session = Depends(get_db)):
    """Retrieve pre-seeded pain point categories, web signals, and Bedrock fit mapping."""
    return db.query(PainPointPattern).all()
