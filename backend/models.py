from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, ProjectStatusEnum
from datetime import datetime

class ClientProject(Base):
    __tablename__ = "client_projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    client_name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    website_url = Column(String, nullable=True)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String, default=ProjectStatusEnum.DISCOVERY_PENDING.value)
    project_folder_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")
    outputs = relationship("AgentOutput", back_populates="project", cascade="all, delete-orphan")
    generated_files = relationship("GeneratedFile", back_populates="project", cascade="all, delete-orphan")

class ProjectFile(Base):
    __tablename__ = "project_files"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("client_projects.id"), nullable=False)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=False)
    project = relationship("ClientProject", back_populates="files")

class AgentOutput(Base):
    __tablename__ = "agent_outputs"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("client_projects.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    stage_name = Column(String, nullable=False)
    output_title = Column(String, nullable=False)
    output_type = Column(String, nullable=False)
    markdown_output = Column(Text, nullable=True)
    assumptions = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    sources_used = Column(Text, nullable=True)
    confidence_level = Column(String, nullable=True)
    approved_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    project = relationship("ClientProject", back_populates="outputs")

class GeneratedFile(Base):
    __tablename__ = "generated_files"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("client_projects.id"), nullable=False)
    stage_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_by_agent = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    project = relationship("ClientProject", back_populates="generated_files")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    geography = Column(String, nullable=False)
    website_url = Column(String, nullable=True)
    founder_name = Column(String, nullable=True)
    status = Column(String, default="draft")  # draft, needs_review, approved, used_in_outreach, converted, archived
    folder_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lead_magnets = relationship("LeadMagnet", back_populates="lead", cascade="all, delete-orphan")

class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source_agent = Column(String, nullable=False)  # monday_jr, tuesday_jr, etc.
    category = Column(String, nullable=False)  # pain_point, benchmark, outreach_message, proposal_teaser, case_example
    content = Column(Text, nullable=False)  # Markdown or JSON string
    reuse_permission = Column(String, default="reusable")  # reusable, confidential, client_specific_only, do_not_reuse
    created_at = Column(DateTime, default=datetime.utcnow)

class IndustryBenchmark(Base):
    __tablename__ = "industry_benchmarks"
    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, nullable=False)
    dimension = Column(String, nullable=False)  # Digital presence, CAC, Retention, Pricing, etc.
    industry_standard = Column(String, nullable=False)
    market_leader = Column(String, nullable=False)
    recommendation_playbook = Column(Text, nullable=True)

class PainPointPattern(Base):
    __tablename__ = "pain_point_patterns"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)  # Unclear Positioning, Weak Digital Presence, etc.
    typical_signals = Column(Text, nullable=True)  # typical public/web signals
    diagnostic_questions = Column(Text, nullable=True)  # questions for discovery call
    bedrock_service_fit = Column(String, nullable=False)

class LeadMagnet(Base):
    __tablename__ = "lead_magnets"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    opening_hook = Column(Text, nullable=True)
    problem_hypothesis = Column(Text, nullable=True)
    suggested_offer = Column(Text, nullable=True)
    outreach_message = Column(Text, nullable=True)
    pre_meeting_one_pager = Column(Text, nullable=True)
    ppt_outline = Column(Text, nullable=True)  # JSON string representing the 11 slides
    discovery_agenda = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lead = relationship("Lead", back_populates="lead_magnets")

