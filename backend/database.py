import os
from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database in the project root directory
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./app.db')

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Initialize the database tables (must import models first)
def init_db():
    import backend.models  # ensures all model classes are registered
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI dependency that provides a DB session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProjectStatusEnum(str, Enum):
    """Enum representing project workflow stages."""
    DISCOVERY_PENDING = "discovery_pending"
    DISCOVERY_APPROVED = "discovery_approved"
    RESEARCH_PENDING = "research_pending"
    RESEARCH_APPROVED = "research_approved"
    RESEARCH_COMPLETE = "research_complete"
    ANALYSIS_PENDING = "analysis_pending"
    ANALYSIS_APPROVED = "analysis_approved"
    ANALYSIS_COMPLETE = "analysis_complete"
    RECOMMENDATION_PENDING = "recommendation_pending"
    RECOMMENDATION_APPROVED = "recommendation_approved"
    RECOMMENDATION_COMPLETE = "recommendation_complete"
    DECK_PENDING = "deck_pending"
    DECK_APPROVED = "deck_approved"
    DECK_COMPLETE = "deck_complete"
    FINAL_DELIVERY_PENDING = "final_delivery_pending"
    FINAL_DELIVERY_COMPLETE = "final_delivery_complete"
