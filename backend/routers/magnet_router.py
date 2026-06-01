# backend/routers/magnet_router.py
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import Lead, LeadMagnet, IndustryBenchmark, PainPointPattern

router = APIRouter(prefix="/magnet", tags=["Lead Magnet Studio"])

class GenerateMagnetPayload(BaseModel):
    lead_id: int
    selected_pain_points: List[str]  # e.g. ["Weak digital presence", "Low retention"]
    custom_signals: Optional[str] = ""

class Slide(BaseModel):
    slide_number: int
    title: str
    content: List[str]

class LeadMagnetResponse(BaseModel):
    id: int
    lead_id: int
    opening_hook: str
    problem_hypothesis: str
    suggested_offer: str
    outreach_message: str
    pre_meeting_one_pager: str
    ppt_outline: str  # JSON representation of List[Slide]
    discovery_agenda: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/generate", response_model=LeadMagnetResponse, status_code=status.HTTP_201_CREATED)
def generate_lead_magnet(payload: GenerateMagnetPayload, db: Session = Depends(get_db)):
    """Generate a qualified Lead Magnet package using non-overclaiming consulting guardrails."""
    # 1. Fetch Lead
    lead = db.query(Lead).filter(Lead.id == payload.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # 2. Fetch selected pain point details
    pains = db.query(PainPointPattern).filter(PainPointPattern.category.in_(payload.selected_pain_points)).all()
    if not pains:
        raise HTTPException(status_code=400, detail="No valid pain point categories selected")

    # 3. Fetch industry benchmarks
    benchmarks = db.query(IndustryBenchmark).filter(IndustryBenchmark.industry == lead.industry).all()
    
    # 4. Generate Opening Hook (Non-Overclaiming)
    primary_pain = pains[0].category.lower()
    hook = (
        f"Noticed {payload.custom_signals or 'some interesting growth benchmarks in your segment'}. "
        f"In similar {lead.industry} businesses at the {lead.stage} stage, we often see teams working to align their "
        f"{primary_pain}. We put together a brief benchmark snapshot comparing where {lead.company_name} "
        f"likely stands today against segment standard indicators. Might be worth checking out?"
    )

    # 5. Generate Problem Hypothesis
    pain_hypotheses = []
    bedrock_solutions = []
    for p in pains:
        pain_hypotheses.append(
            f"* **Hypothesis - {p.category}:** Based on public digital signals, there may be an opportunity to optimize your "
            f"{p.category.lower()}. Common challenges we see here include: {p.typical_signals or 'efficiency gaps'}."
        )
        bedrock_solutions.append(f"* **{p.bedrock_service_fit}:** Custom playbook to address {p.category.lower()}.")

    pain_hypotheses_str = "\n".join(pain_hypotheses)
    bedrock_solutions_str = "\n".join(bedrock_solutions)

    hypothesis_block = f"""### Core Diagnostic Hypothesis for {lead.company_name}
> [!NOTE]
> These hypotheses are formulated strictly using public indicators and public competitor performance data. They represent potential opportunity areas to validate during our live discovery meeting.

{pain_hypotheses_str}
"""

    # 6. Generate Suggested Offer
    suggested_offer = (
        f"We suggest a focused 30-minute diagnostic session to run our Startup Health & Scalability Framework. "
        f"This will validate these hypotheses against your private metrics, calibrate your CAC and LTV benchmarks, "
        f"and deliver a zero-obligation operational roadmap."
    )

    # 7. Generate Multi-channel Outreach Messaging
    linkedin_msg = (
        f"Hi {lead.founder_name or 'there'},\n\n"
        f"Noticed {lead.company_name} is growing in {lead.geography}. For {lead.stage} startups in the "
        f"{lead.industry} space, a common challenge is scaling {primary_pain} efficiently.\n\n"
        f"We put together a quick, non-intrusive 1-page benchmark dashboard comparing your public signals "
        f"to segment leaders. We've mapped out some potential opportunity areas that could save CAC or boost retention.\n\n"
        f"Would you be open to a brief review? No sales pitches - just benchmarks.\n\n"
        f"Best,\n[Your Name]"
    )

    email_msg = (
        f"Subject: Benchmarking {lead.company_name} against {lead.industry} Segment Leaders\n\n"
        f"Hi {lead.founder_name or 'there'},\n\n"
        f"I've been reviewing digital signals and customer acquisition trends in the {lead.industry} sector. "
        f"For companies in the {lead.stage} stage, optimizing {primary_pain} is often a key growth priority.\n\n"
        f"Based on public signals, we mapped out a hypothetical gap analysis for {lead.company_name}. "
        f"This compares standard segment averages against market leaders on dimensions like CAC, retention, and digital presence.\n\n"
        f"I've attached our diagnostic overview and a short 11-slide pre-meeting deck. Here is what we've identified as likely opportunity areas:\n"
        f"{', '.join(payload.selected_pain_points)}\n\n"
        f"Would you be open to a 15-minute call next Tuesday to validate these assumptions?\n\n"
        f"Best regards,\n[Your Name]\nBedrock Consulting"
    )

    whatsapp_msg = (
        f"Hi {lead.founder_name or 'there'} - put together a quick segment diagnostic for {lead.company_name} "
        f"comparing public signals against {lead.industry} standards. Mapped out a few hypothetical "
        f"improvement areas for {primary_pain}. Open to a quick look?"
    )

    outreach_payload = {
        "linkedin": linkedin_msg,
        "email": email_msg,
        "whatsapp": whatsapp_msg
    }
    outreach_message = json.dumps(outreach_payload)

    # 8. Generate One-Page Business Diagnostic
    benchmark_rows = []
    if benchmarks:
        for b in benchmarks:
            benchmark_rows.append(
                f"| {b.dimension} | {b.industry_standard} | {b.market_leader} | "
                f"Likely Gap in {lead.stage} phase | We can support via {b.recommendation_playbook or 'custom audit'} |"
            )
    else:
        benchmark_rows.append(
            f"| Digital Presence | Standard Website | Unified Portal | Likely Gap | Web Audit & Optimization |"
        )
    
    benchmark_table = "\n".join(benchmark_rows)

    one_pager = f"""# Business Diagnostic Overview: {lead.company_name}

## 1. Context & Benchmarks
This diagnostic compares public indicators of {lead.company_name} with sector benchmarks in the {lead.industry} ({lead.stage}) space.

| Dimension | Industry Standard | Market Leader | Estimated Lead Position | Bedrock Service Alignment |
|---|---|---|---|---|
{benchmark_table}

---

## 2. Strategic Hypotheses to Validate
Based on sector trends, we have established the following problem hypotheses to explore:
{pain_hypotheses_str}

---

## 3. Bedrock Solution Fit
To help {lead.company_name} transition from industry averages toward market leadership, we align the following solutions:
{bedrock_solutions_str}
"""

    # 9. Generate PPT Outline (11 Slides JSON)
    slides = [
        {
            "slide_number": 1,
            "title": f"Growth Opportunity Snapshot for {lead.company_name}",
            "content": [
                f"Prepared for: {lead.founder_name or 'Management Team'}",
                f"Focus: Tactical Opportunity Scan in {lead.industry} ({lead.stage})",
                "Bedrock Consulting: Strategy meets scale"
            ]
        },
        {
            "slide_number": 2,
            "title": "Why We Looked at This Business",
            "content": [
                f"Observed exciting market trajectory for {lead.company_name} in {lead.geography}",
                f"Identified {primary_pain} as a crucial lever for {lead.stage} startups looking to scale",
                "Goal: Identify structural levers to accelerate efficiency before your next growth push"
            ]
        },
        {
            "slide_number": 3,
            "title": f"Industry Context: {lead.industry} Segment",
            "content": [
                f"Sector margins are tightening; CAC acquisition efficiency has become the primary battleground",
                "Customer lifetime value demands rapid expansion and high Net Revenue Retention (NRR)",
                "Leaders are separating themselves via continuous automated digital operations"
            ]
        },
        {
            "slide_number": 4,
            "title": "Market & Segment Benchmarks",
            "content": [
                f"Industry standards dictate baseline performance; leaders operate with 2-3x higher efficiencies",
                "We track 10 core dimensions: Presence, Acquisition, Retention, Pricing, and scale factors",
                "Our models indicate high ROI for teams shifting from average standards to leader levels"
            ]
        },
        {
            "slide_number": 5,
            "title": "Likely Current Position (Estimated)",
            "content": [
                f"Based on public signals, {lead.company_name} exhibits strong foundation markers",
                f"We estimate current performance sits near sector averages for {primary_pain}",
                "Validation target: Quantify your private metrics to determine the exact optimization headroom"
            ]
        },
        {
            "slide_number": 6,
            "title": "Possible Pain Points (Hypotheses)",
            "content": [
                f"Hypothesis 1: Potential drag on growth due to {primary_pain} friction",
                f"Hypothesis 2: Untapped expansion channels that could support user retention",
                "Hypothesis 3: High cost of delivery manual tasks limiting long-term gross margin"
            ]
        },
        {
            "slide_number": 7,
            "title": "Opportunity Areas",
            "content": [
                f"Area A: Establish automated marketing funnels to reduce customer acquisition friction",
                f"Area B: Redefine product pricing models to maximize customer wallet share",
                "Area C: Implement structured tracking metrics to flag client churn threats early"
            ]
        },
        {
            "slide_number": 8,
            "title": "How Bedrock Can Help",
            "content": [
                "Deploy our modular diagnostic framework to identify efficiency leaks in 7 days",
                "Provide customizable, action-ready playbooks tailored to your industry stage",
                "Integrate hands-on growth advisory to steer your GTM execution"
            ]
        },
        {
            "slide_number": 9,
            "title": "Suggested Engagement Scope",
            "content": [
                "Phase 1: 2-week Operational Assessment (Full internal metrics review)",
                "Phase 2: Custom Playbook Creation (GTM positioning and pricing redesign)",
                "Phase 3: Ongoing Growth Retainer (Weekly audit checks and team coaching)"
            ]
        },
        {
            "slide_number": 10,
            "title": "Discovery Meeting Agenda",
            "content": [
                "1. Brief introductions & context (5 mins)",
                "2. Review and validate public-signal hypotheses (10 mins)",
                "3. Deep dive into your primary operational bottlenecks (10 mins)",
                "4. Align on diagnostic scope and outline next steps (5 mins)"
            ]
        },
        {
            "slide_number": 11,
            "title": "Next Steps",
            "content": [
                "Select a convenient slot on our team calendar for the diagnostic session",
                "Complete our brief 5-question pre-meeting survey to optimize our discussion",
                "Contact: team@bedrock.com"
            ]
        }
    ]
    ppt_outline = json.dumps(slides)

    # 10. Generate Discovery Agenda
    discovery_agenda = f"""### Discovery Meeting Agenda
1. **Introductions & Background** (5 minutes): Align on Bedrock framework and {lead.company_name} history.
2. **Signal & Hypothesis Validation** (10 minutes): Review the public-data hypotheses. Compare estimated ranges with your true operational averages.
3. **Operational Deep Dive** (10 minutes): Unpack bottlenecks within {primary_pain}.
4. **Scoping & Roadmap** (5 minutes): Map next steps for a detailed operational assessment.
"""

    # 11. Create and Save LeadMagnet record
    magnet = LeadMagnet(
        lead_id=payload.lead_id,
        opening_hook=hook,
        problem_hypothesis=hypothesis_block,
        suggested_offer=suggested_offer,
        outreach_message=outreach_message,
        pre_meeting_one_pager=one_pager,
        ppt_outline=ppt_outline,
        discovery_agenda=discovery_agenda
    )
    db.add(magnet)
    
    # Update lead status to needs_review
    lead.status = "needs_review"
    
    db.commit()
    db.refresh(magnet)
    return magnet

@router.get("/{lead_id}")
def get_latest_magnet(lead_id: int, db: Session = Depends(get_db)):
    """Retrieve the latest generated lead magnet for a lead."""
    magnet = db.query(LeadMagnet).filter(LeadMagnet.lead_id == lead_id).order_by(LeadMagnet.created_at.desc()).first()
    if not magnet:
        raise HTTPException(status_code=404, detail="Lead magnet not found for this lead")
    return magnet
