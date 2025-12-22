import os
import json
import sys
from typing import Dict
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.gap_analysis import gap_analysis_node
from evaluation.metrics import evaluate_gap_quality

# Test cases
TOURISM_CASE = {
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
            "Social media marketing drives 60% of tourism bookings",
            "Influencer partnerships show 3x ROI for travel companies"
        ],
        "competitor_analysis": [
            {"competitor": "EgyptExplorer", "strengths": ["Instagram 50k followers", "Email automation"]},
            {"competitor": "PyramidAdventures", "strengths": ["SEO #1 ranking", "Paid Google Ads"]}
        ],
        "best_practices": ["Tourism businesses allocate 20-30% revenue to marketing"],
        "industry_benchmarks": {"avg_social_media_followers": 30000}
    },
    "user_goal": "Launch a 3-month marketing campaign to increase bookings by 50%"
}

FINTECH_CASE = {
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
            "B2B fintech requires SOC2 compliance",
            "Automated KYC/AML reduces onboarding from 5 days to 1 hour"
        ],
        "competitor_analysis": [
            {"competitor": "Stripe", "strengths": ["SOC2 certified", "Self-serve onboarding", "99.99% uptime"]},
            {"competitor": "PayMob", "strengths": ["Local bank partnerships", "Mobile wallet integration"]}
        ],
        "best_practices": ["Developer documentation reduces support tickets by 70%"],
        "industry_benchmarks": {"time_to_first_transaction": "1 hour", "uptime_sla": 0.999}
    },
    "user_goal": "Onboard 10 pilot customers in 2 months"
}

def run_experiment(provider: str, test_case: Dict, case_name: str) -> Dict:
    """Run gap analysis with specific LLM and evaluate"""
    print(f"\n{'='*60}")
    print(f"Testing: {provider.upper()} on {case_name}")
    print(f"{'='*60}")
    
    # Set provider
    os.environ["LLM_PROVIDER"] = provider
    
    # Run agent
    result = gap_analysis_node(test_case.copy())
    
    # Evaluate
    metrics = evaluate_gap_quality(
        gaps_output={
            "internal_gaps": result["internal_gaps"],
            "market_gaps": result["market_gaps"]
        },
        input_data=test_case
    )
    
    # Display results
    print(f"\n Results:")
    print(f"   Total Gaps: {metrics['total_gaps']}")
    print(f"   Overall Score: {metrics['overall_score']:.3f}")
    print(f"\n   Hallucination Rate: {metrics['hallucination']['hallucination_rate']:.2%}")
    print(f"   Factual Grounding: {metrics['grounding']['grounding_rate']:.2%}")
    print(f"   Relevance: {metrics['relevance']['relevance_score']:.2%}")
    print(f"   Coverage: {metrics['coverage']['coverage_score']:.2%}")
    print(f"   Severity Calibration: {metrics['severity_calibration']['calibration_score']:.2%}")
    
    print(f"\n   Sample Gaps:")
    for gap in (result["internal_gaps"] + result["market_gaps"])[:3]:
        print(f"   - [{gap['severity'].upper()}] {gap['description'][:70]}...")
    
    return {
        "provider": provider,
        "case": case_name,
        "metrics": metrics,
        "gaps": result["internal_gaps"] + result["market_gaps"]
    }

def compare_llms():
    """Compare multiple LLMs on same test cases"""
    providers = ["gemini", "sonar", "mock"]  # Add "openai" if you have key
    test_cases = [
        (TOURISM_CASE, "Tourism"),
        (FINTECH_CASE, "Fintech")
    ]
    
    results = []
    
    for provider in providers:
        for test_case, case_name in test_cases:
            try:
                result = run_experiment(provider, test_case, case_name)
                results.append(result)
            except Exception as e:
                print(f" {provider} failed on {case_name}: {e}")
    
    # Summary comparison
    print(f"\n\n{'='*80}")
    print("COMPARISON SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"{'Provider':<15} {'Case':<10} {'Overall':<10} {'Halluc':<10} {'Ground':<10} {'Relev':<10}")
    print("-" * 80)
    
    for r in results:
        m = r["metrics"]
        print(f"{r['provider']:<15} {r['case']:<10} "
              f"{m['overall_score']:<10.3f} "
              f"{(1-m['hallucination']['hallucination_rate']):<10.3f} "
              f"{m['grounding']['grounding_rate']:<10.3f} "
              f"{m['relevance']['relevance_score']:<10.3f}")
    
    # Save results
    with open("experiments/llm_comparison_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to experiments/llm_comparison_results.json")

if __name__ == "__main__":
    compare_llms()
