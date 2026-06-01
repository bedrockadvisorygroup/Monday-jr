# backend/seed_data.py
import sys
from pathlib import Path

# Add project root to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.database import SessionLocal, init_db
from backend.models import IndustryBenchmark, PainPointPattern

BENCHMARK_PRESETS = [
    {
        "industry": "B2B SaaS",
        "dimension": "Digital presence",
        "industry_standard": "Interactive high-converting website, active LinkedIn (2+ posts/week), documented customer reviews.",
        "market_leader": "Interactive product tour on home page, 50k+ LinkedIn followers, daily content, ranked #1 on G2/Capterra.",
        "recommendation_playbook": "Develop an interactive product interactive interactive walkthrough on home page, invest in regular thought-leadership content on LinkedIn, and build a review campaign on high-profile directory websites."
    },
    {
        "industry": "B2B SaaS",
        "dimension": "Customer acquisition",
        "industry_standard": "LTV:CAC ratio of 3:1, Payback period of 12 months, CAC around $100-$300 depending on ACV.",
        "market_leader": "LTV:CAC ratio of 5:1+, Payback period under 6 months, highly optimized inbound PLG model.",
        "recommendation_playbook": "Refine search ads to target high-intent keywords, establish a referral loop program, and implement a self-serve free-trial/freemium intake workflow."
    },
    {
        "industry": "B2B SaaS",
        "dimension": "Retention",
        "industry_standard": "Net Revenue Retention (NRR) of 100-105%, Gross Revenue Retention (GRR) of 85-90%, Gross Churn < 1% monthly.",
        "market_leader": "NRR of 120%+, Gross Churn < 0.5% monthly, highly engaged user community.",
        "recommendation_playbook": "Implement automated onboarding flows, setup high-risk churn alerts based on usage drop-offs, and design customer success expansion playbooks."
    },
    {
        "industry": "B2B SaaS",
        "dimension": "Pricing",
        "industry_standard": "Standard Tiered seat-based pricing or usage-based pricing with annual discount options.",
        "market_leader": "Value-based pricing mapped directly to business value metric (e.g., revenue generated, API calls).",
        "recommendation_playbook": "Conduct a pricing sensitivity study, adjust tiers to align pricing directly with customer value milestones, and launch grandfathering strategies."
    },
    {
        "industry": "B2B SaaS",
        "dimension": "Brand positioning",
        "industry_standard": "Product-centric, feature-rich messaging focusing on utility and software functionalities.",
        "market_leader": "Outcome-centric, category-defining positioning focusing on business transformation and ROI.",
        "recommendation_playbook": "Reframe website copy and sales decks from features to outcomes, publish comprehensive ROI case studies, and declare a category leadership stance."
    },
    {
        "industry": "Retail & E-commerce",
        "dimension": "Digital presence",
        "industry_standard": "Responsive Shopify website, Instagram presence with weekly posts, basic search visibility.",
        "market_leader": "Lightning-fast headless storefront, daily short-form videos (TikTok/Reels), 100k+ organic community base.",
        "recommendation_playbook": "Audit and optimize page load speeds, develop a short-form video strategy focusing on user-generated content, and leverage nano-influencer collaborations."
    },
    {
        "industry": "Retail & E-commerce",
        "dimension": "Customer acquisition",
        "industry_standard": "ROAS (Return on Ad Spend) of 2.0x, blended CAC under $30.",
        "market_leader": "ROAS of 4.0x+, blended CAC under $15, strong organic and referral channel contribution.",
        "recommendation_playbook": "Build automated email acquisition popups, optimize retargeting campaign audience segments, and run viral referral incentives."
    },
    {
        "industry": "Retail & E-commerce",
        "dimension": "Retention",
        "industry_standard": "Repeat customer rate of 20-25%, average customer lifetime value (LTV) span of 12 months.",
        "market_leader": "Repeat customer rate of 40%+, active tiered loyalty program, high subscription tier membership.",
        "recommendation_playbook": "Integrate a personalized loyalty/rewards system, launch custom email flows for replenishment, and implement cross-sell subscription offers."
    },
    {
        "industry": "Healthcare & Biotech",
        "dimension": "Digital presence",
        "industry_standard": "Standard informative website, basic security compliances, static PDF datasheets.",
        "market_leader": "Educational portals, active patient forums, strong authority rankings for clinical search keywords.",
        "recommendation_playbook": "Produce comprehensive SEO-optimized medical educational articles, deploy secure patient consultation booking widgets, and clean up digital listings."
    },
    {
        "industry": "Healthcare & Biotech",
        "dimension": "Customer acquisition",
        "industry_standard": "High reliance on medical rep visits and medical trade shows; online lead gen costs $200+ per lead.",
        "market_leader": "Continuous educational webinars, organic thought leadership campaigns, digital partner referral networks.",
        "recommendation_playbook": "Organize structured, accredited digital webinars for practitioners, deploy targeted search ads, and establish strategic digital affiliate channels."
    }
]

PAIN_POINT_PRESETS = [
    {
        "category": "Weak digital presence",
        "typical_signals": "No recent updates on LinkedIn, website has slow loading speeds, lack of public case studies, poor SEO page ranking.",
        "diagnostic_questions": "How do prospective clients learn about your product before the first sales call? Do you track website drop-offs and page-load metrics?",
        "bedrock_service_fit": "Digital Transformation & Web Optimization"
    },
    {
        "category": "Unclear positioning",
        "typical_signals": "Value proposition on website home page is vague, copy focuses heavily on technical specifications rather than clear business outcomes.",
        "diagnostic_questions": "If you ask five of your team members what exact problem you solve and for whom, do their answers perfectly align?",
        "bedrock_service_fit": "Brand Strategy & Strategic Positioning Workshop"
    },
    {
        "category": "Low customer acquisition efficiency",
        "typical_signals": "High blended CAC, declining paid social ad returns (ROAS < 1.5x), heavy reliance on raw cold outbound without segmentation.",
        "diagnostic_questions": "What is your blended CAC payback period, and what channel is currently your primary growth engine?",
        "bedrock_service_fit": "Growth Marketing Audit & Funnel Optimization"
    },
    {
        "category": "Low retention",
        "typical_signals": "High customer churn rates, low repeat purchase rates, poor post-purchase user engagement metrics.",
        "diagnostic_questions": "At what stage of the customer lifecycle do you observe the highest drop-off, and what post-sale touchpoints exist?",
        "bedrock_service_fit": "Customer Success & Engagement Strategy"
    },
    {
        "category": "Poor profitability",
        "typical_signals": "Low gross margins, high fixed operational overhead, slow net cash accumulation despite revenue growth.",
        "diagnostic_questions": "Which product tier or customer segment yields the highest margins, and where does operational leakage most frequently occur?",
        "bedrock_service_fit": "Cost Transformation & Operational Restructuring"
    },
    {
        "category": "Weak GTM structure",
        "typical_signals": "Product launches are chaotic, lack of documented sales playbooks, sales and marketing teams operate in distinct silos.",
        "diagnostic_questions": "How long does it take for a new sales rep to hit full quota target, and how is leads flow handed off to sales?",
        "bedrock_service_fit": "Go-To-Market (GTM) Enablement"
    },
    {
        "category": "Pricing mismatch",
        "typical_signals": "Competitors command a significant premium for similar features, prospect feedback frequently points to pricing confusion.",
        "diagnostic_questions": "When was the last time you tested or adjusted your price points, and what value metrics dictate your tiers?",
        "bedrock_service_fit": "Value-Based Pricing Restructuring"
    },
    {
        "category": "Weak sales funnel",
        "typical_signals": "Huge drop-off between demo booked and contract proposed, long average sales cycle lengths, low close ratios.",
        "diagnostic_questions": "Where in the sales process do most opportunities stall, and what trigger sequences exist to re-engage dead leads?",
        "bedrock_service_fit": "Sales Operations & Pipeline Acceleration"
    },
    {
        "category": "Low brand trust",
        "typical_signals": "Zero online reviews on major directory sites, lack of trust badges on checkout pages, minimal press coverage.",
        "diagnostic_questions": "How do you leverage testimonials and client reviews during middle-of-funnel validation?",
        "bedrock_service_fit": "Trust Marketing & Authority Positioning"
    },
    {
        "category": "Lack of repeat customer engine",
        "typical_signals": "No loyalty program, minimal email communication after a purchase is completed, zero automated repurchase alerts.",
        "diagnostic_questions": "What incentives or personalized touchpoints exist to invite a one-time buyer to make their second purchase?",
        "bedrock_service_fit": "Retention Marketing & Loyalty Engine Creation"
    },
    {
        "category": "Poor market entry strategy",
        "typical_signals": "Struggling to expand into a new geography or sector, heavy burn on marketing campaigns that fail to convert.",
        "diagnostic_questions": "How was the target profile defined for this new segment, and how does your positioning adjust for local competitors?",
        "bedrock_service_fit": "Market Expansion & Localization Strategy"
    },
    {
        "category": "Low operational scalability",
        "typical_signals": "Onboarding clients requires heavy manual work, processes are undocumented, high rate of errors in daily execution.",
        "diagnostic_questions": "If you doubled your client intake next month, what parts of your delivery would experience immediate failure or bottleneck?",
        "bedrock_service_fit": "Operational Workflow Automation"
    },
    {
        "category": "Weak investor readiness",
        "typical_signals": "Financial forecasts lack structure, pitch deck is unpolished, data room is empty or unstructured.",
        "diagnostic_questions": "How clear is your path to unit economic profitability, and do your strategic plans align with investor mandates?",
        "bedrock_service_fit": "Investor Relations & Pitch Deck Optimization"
    },
    {
        "category": "Weak unit economics",
        "typical_signals": "CAC exceeds LTV, high delivery support costs, gross margin is below industry standard averages.",
        "diagnostic_questions": "What are the primary cost drivers behind your cost of goods sold (COGS) and client support delivery?",
        "bedrock_service_fit": "Unit Economic Restructuring"
    },
    {
        "category": "Poor benchmark performance",
        "typical_signals": "Crucial business metrics (e.g. churn, payback period, margin) are noticeably lagging behind direct competitors.",
        "diagnostic_questions": "Which specific industry benchmark are you most concerned about, and how are you tracking against market leaders today?",
        "bedrock_service_fit": "Strategic Diagnostic & Optimization Plan"
    }
]

def seed():
    init_db()
    db = SessionLocal()
    try:
        # Check if benchmarks already seeded
        if db.query(IndustryBenchmark).count() == 0:
            print("Seeding industry benchmarks...")
            for b in BENCHMARK_PRESETS:
                db.add(IndustryBenchmark(**b))
            db.commit()
            print("Industry benchmarks seeded.")
        else:
            print("Benchmarks already exist. Skipping.")

        # Check if pain patterns already seeded
        if db.query(PainPointPattern).count() == 0:
            print("Seeding pain point patterns...")
            for p in PAIN_POINT_PRESETS:
                db.add(PainPointPattern(**p))
            db.commit()
            print("Pain point patterns seeded.")
        else:
            print("Pain point patterns already exist. Skipping.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
