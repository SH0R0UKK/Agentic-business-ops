import os
from backend.agents.gap_analysis.agent import gap_analysis_node

def test_tourism_case():
    os.environ["LLM_PROVIDER"] = "mock"  # run offline
    state = {
        "startup_profile": {
            "company_name": "NileCruise Tours",
            "sector": "tourism",
            "stage": "seed",
            "team_size": 5,
            "current_capabilities": ["tour booking", "customer support"],
            "has_mvp": True,
            "monthly_revenue": 15000
        },
        "research_summary": {
            "market_trends": [
                "Social media marketing drives tourism bookings",
                "Influencer partnerships show strong ROI"
            ],
            "competitor_analysis": [
                {"competitor": "EgyptExplorer", "strengths": ["Instagram 50k", "Email automation"]},
                {"competitor": "PyramidAdventures", "strengths": ["SEO #1", "Google Ads"]}
            ],
            "best_practices": ["Allocate 20-30% revenue to marketing"],
            "industry_benchmarks": {"avg_social_media_followers": 30000}
        },
        "user_goal": "Launch a 3-month marketing campaign to increase bookings by 50%"
    }
    out = gap_analysis_node(state)
    assert out["gap_analysis_metadata"]["total_gaps_identified"] > 0
    assert all(g["confidence"] >= 0.5 for g in out["internal_gaps"] + out["market_gaps"])
    assert any(g["severity"] == "critical" for g in out["internal_gaps"] + out["market_gaps"])

def test_fintech_case():
    os.environ["LLM_PROVIDER"] = "mock"
    state = {
        "startup_profile": {
            "company_name": "PayFlow",
            "sector": "fintech",
            "stage": "pre-seed",
            "team_size": 3,
            "current_capabilities": ["payment API", "manual onboarding"],
            "has_mvp": True,
            "monthly_revenue": 0
        },
        "research_summary": {
            "market_trends": [
                "SOC2 compliance expected for B2B",
                "Automated KYC/AML reduces onboarding time"
            ],
            "competitor_analysis": [
                {"competitor": "Stripe", "strengths": ["SOC2", "Self-serve onboarding", "99.99% uptime"]},
                {"competitor": "PayMob", "strengths": ["Local integrations"]}
            ],
            "best_practices": ["Developer docs reduce support by 70%"],
            "industry_benchmarks": {"uptime_sla": 0.999}
        },
        "user_goal": "Onboard 10 pilot customers in 2 months"
    }
    out = gap_analysis_node(state)
    assert out["gap_analysis_metadata"]["total_gaps_identified"] > 0
    # expect at least one compliance-related gap
    assert any("compliance" in g["description"].lower() for g in out["internal_gaps"])
