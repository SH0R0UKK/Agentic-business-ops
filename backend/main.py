from dotenv import load_dotenv
load_dotenv()

from agents.gap_analysis import gap_analysis_node

def demo_tourism():
    print("\n Tourism Marketing Campaign Gap Analysis \n")
    
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
                "Social media marketing drives 60% of tourism bookings",
                "Influencer partnerships show 3x ROI"
            ],
            "competitor_analysis": [
                {
                    "competitor": "EgyptExplorer",
                    "strengths": ["Instagram 50k followers", "Email automation"]
                }
            ],
            "best_practices": [
                "Tourism businesses allocate 20-30% revenue to marketing"
            ],
            "industry_benchmarks": {
                "avg_social_media_followers": 30000
            }
        },
        "user_goal": "Launch a 3-month marketing campaign to increase bookings by 50%"
    }
    
    result = gap_analysis_node(state)
    
    print(f"Total Gaps Found: {result['gap_analysis_metadata']['total_gaps_identified']}")
    print(f" Critical Gaps: {result['gap_analysis_metadata']['critical_gaps_count']}\n")
    
    print(" INTERNAL GAPS:")
    for gap in result["internal_gaps"]:
        print(f"  [{gap['severity'].upper()}] {gap['description']}")
        print(f"    Confidence: {gap['confidence']:.2f} | Goal-blocking: {gap['related_to_goal']}")
        print(f"    Reasoning: {gap['reasoning']}\n")
    
    print(" MARKET GAPS:")
    for gap in result["market_gaps"]:
        print(f"  [{gap['severity'].upper()}] {gap['description']}")
        print(f"    Threat: {gap.get('competitive_threat', 'N/A')}")
        print(f"    Confidence: {gap['confidence']:.2f}\n")

if __name__ == "__main__":
    demo_tourism()
