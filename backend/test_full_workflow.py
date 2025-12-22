"""
Full Workflow Integration Test
==============================
This test simulates a complete business advisory session:
1. Egyptian fintech startup seeking Series A funding
2. Pre-built gap analysis identifying key challenges
3. Research agent gathers market intel (offline + online)
4. Planner creates actionable roadmap
5. Final plan exported to text file
"""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from agents.orchestrator.orchestrator import master_app

# ============================================================================
# TEST DATA: Egyptian FinTech Startup Seeking Series A
# ============================================================================

STARTUP_PROFILE = {
    "business_name": "PayMasry",
    "business_type": "FinTech - Mobile Payments & Digital Wallet",
    "stage": "Seed (seeking Series A)",
    "founded": "2023",
    "location": "Cairo, Egypt",
    "team_size": 12,
    "current_funding": "$500,000 (seed round from Flat6Labs)",
    "monthly_revenue": "$15,000 MRR",
    "users": "25,000 registered users",
    "goals": "Raise $2-3M Series A within 6 months to expand across Egypt and enter Saudi market",
    "sector": "fintech",
    "target_market": "Underbanked population in Egypt (60M+ adults)",
    "competitors": ["Fawry", "Paymob", "ValU", "Kashier"],
    "unique_value": "Focus on rural/semi-urban areas with agent network model",
}

GAP_ANALYSIS = {
    "status": "completed",
    "timestamp": datetime.now().isoformat(),
    "critical_gaps": [
        {
            "area": "Regulatory Compliance",
            "gap": "Missing CBE (Central Bank of Egypt) e-money license",
            "impact": "HIGH - Cannot legally scale payment operations",
            "recommendation": "Prioritize CBE license application immediately"
        },
        {
            "area": "Unit Economics",
            "gap": "Customer acquisition cost ($8) exceeds first-year LTV ($5)",
            "impact": "HIGH - Unsustainable growth model",
            "recommendation": "Focus on retention and agent referral programs"
        },
        {
            "area": "Technology Infrastructure",
            "gap": "Current architecture handles 100 TPS, need 1000+ for scale",
            "impact": "MEDIUM - Will hit ceiling at 100K users",
            "recommendation": "Plan infrastructure upgrade before Series A close"
        },
        {
            "area": "Team",
            "gap": "No dedicated CFO or Head of Compliance",
            "impact": "MEDIUM - Investors will question financial controls",
            "recommendation": "Hire experienced CFO before fundraising roadshow"
        },
        {
            "area": "Market Expansion",
            "gap": "No Saudi market entry strategy or local partnerships",
            "impact": "MEDIUM - Saudi expansion claim is unsubstantiated",
            "recommendation": "Secure at least one Saudi partnership LOI"
        }
    ],
    "strengths": [
        "Strong agent network (500+ agents in rural areas)",
        "Low fraud rate (0.1% vs industry 0.5%)",
        "Experienced founders (ex-Vodafone Cash, ex-Fawry)",
        "Growing MRR (40% MoM growth)"
    ],
    "investor_readiness_score": 6.5,  # out of 10
    "summary": "PayMasry has strong fundamentals but critical gaps in regulatory compliance and unit economics must be addressed before Series A. Recommend 3-month sprint to close gaps before investor outreach."
}

USER_REQUEST = """
I'm the CEO of PayMasry. We're a Cairo-based fintech startup with a mobile wallet focused on 
underbanked Egyptians in rural areas. We raised $500K seed from Flat6Labs and now want to 
raise Series A ($2-3M) to expand across Egypt and enter Saudi Arabia.

Based on the gap analysis, I need you to:
1. Research the current Egyptian fintech funding landscape and successful Series A examples
2. Research what investors are looking for in Egyptian fintech startups
3. Create a 90-day action plan to close our gaps and prepare for fundraising
4. Include specific milestones, responsible parties, and success metrics

Please be specific and actionable - we have limited runway (8 months) and need to move fast.
"""


def run_full_workflow_test():
    """Run the complete workflow test."""
    
    print("\n" + "=" * 80)
    print("🚀 FULL WORKFLOW INTEGRATION TEST")
    print("=" * 80)
    
    print("\n📋 STARTUP PROFILE:")
    print("-" * 40)
    for key, value in STARTUP_PROFILE.items():
        if isinstance(value, list):
            print(f"  {key}: {', '.join(value)}")
        else:
            print(f"  {key}: {value}")
    
    print("\n🔍 PRE-BUILT GAP ANALYSIS:")
    print("-" * 40)
    print(f"  Investor Readiness Score: {GAP_ANALYSIS['investor_readiness_score']}/10")
    print(f"  Critical Gaps: {len(GAP_ANALYSIS['critical_gaps'])}")
    for gap in GAP_ANALYSIS['critical_gaps']:
        print(f"    - [{gap['impact']}] {gap['area']}: {gap['gap'][:50]}...")
    print(f"  Strengths: {len(GAP_ANALYSIS['strengths'])}")
    
    print("\n💬 USER REQUEST:")
    print("-" * 40)
    print(f"  {USER_REQUEST[:200]}...")
    
    # Build initial state
    initial_state = {
        "messages": [HumanMessage(content=USER_REQUEST)],
        "user_context": STARTUP_PROFILE,
        "gap_analysis": GAP_ANALYSIS,  # Pre-populated gap analysis
        "action": None,
        "next_agent": None,
        "search_query": None,
        "task_type": None,
        "final_plan": None,
        "research_data": None,
        "rag_data": None,
        "research_offline": None,
        "research_online": None,
        "final_reply": None,
    }
    
    print("\n" + "=" * 80)
    print("🔄 RUNNING ORCHESTRATOR...")
    print("=" * 80)
    
    try:
        # Run the orchestrator
        final_state = master_app.invoke(initial_state)
        
        print("\n" + "=" * 80)
        print("📊 WORKFLOW RESULTS")
        print("=" * 80)
        
        # Collect all results for the output file
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append("PAYMASRY SERIES A PREPARATION PLAN")
        output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        # 1. Research Results
        output_lines.append("SECTION 1: MARKET RESEARCH FINDINGS")
        output_lines.append("-" * 40)
        
        if final_state.get("research_offline"):
            offline = final_state["research_offline"]
            print("\n✅ OFFLINE RESEARCH (Knowledge Base):")
            print(f"   Status: {offline.get('status')}")
            print(f"   Claims: {len(offline.get('claims', []))}")
            
            output_lines.append("\n1.1 Internal Knowledge Base Findings:")
            output_lines.append(f"Summary: {offline.get('summary', 'N/A')}")
            output_lines.append("\nKey Claims:")
            for i, claim in enumerate(offline.get('claims', []), 1):
                claim_text = claim.get('claim', claim) if isinstance(claim, dict) else str(claim)
                output_lines.append(f"  {i}. {claim_text}")
            
            if offline.get('missing_info'):
                output_lines.append("\nInformation Gaps:")
                for gap in offline.get('missing_info', []):
                    output_lines.append(f"  - {gap}")
        else:
            print("\n⚠️ No offline research results")
            output_lines.append("\n1.1 Internal Knowledge Base: No results")
        
        if final_state.get("research_online"):
            online = final_state["research_online"]
            print("\n✅ ONLINE RESEARCH (Web Search):")
            print(f"   Status: {online.get('status')}")
            print(f"   Findings: {len(online.get('findings', []))}")
            
            output_lines.append("\n1.2 Live Market Research (Web):")
            output_lines.append(f"Summary: {online.get('summary', 'N/A')}")
            output_lines.append("\nKey Findings:")
            for i, finding in enumerate(online.get('findings', []), 1):
                if isinstance(finding, dict):
                    output_lines.append(f"  {i}. {finding.get('finding', finding)}")
                    if finding.get('source'):
                        output_lines.append(f"     Source: {finding.get('source')}")
                else:
                    output_lines.append(f"  {i}. {finding}")
            
            if online.get('assumptions'):
                output_lines.append("\nAssumptions/Caveats:")
                for assumption in online.get('assumptions', []):
                    output_lines.append(f"  ⚠️ {assumption}")
        else:
            print("\n⚠️ No online research results")
            output_lines.append("\n1.2 Live Market Research: No results")
        
        output_lines.append("")
        output_lines.append("")
        
        # 2. Gap Analysis (Pre-populated)
        output_lines.append("SECTION 2: GAP ANALYSIS (PRE-ASSESSMENT)")
        output_lines.append("-" * 40)
        output_lines.append(f"\nInvestor Readiness Score: {GAP_ANALYSIS['investor_readiness_score']}/10")
        output_lines.append(f"Assessment Summary: {GAP_ANALYSIS['summary']}")
        output_lines.append("\nCritical Gaps to Address:")
        for i, gap in enumerate(GAP_ANALYSIS['critical_gaps'], 1):
            output_lines.append(f"\n  Gap {i}: {gap['area']}")
            output_lines.append(f"  Issue: {gap['gap']}")
            output_lines.append(f"  Impact: {gap['impact']}")
            output_lines.append(f"  Recommendation: {gap['recommendation']}")
        
        output_lines.append("\nCompany Strengths:")
        for strength in GAP_ANALYSIS['strengths']:
            output_lines.append(f"  ✓ {strength}")
        
        output_lines.append("")
        output_lines.append("")
        
        # 3. Action Plan from Planner
        output_lines.append("SECTION 3: 90-DAY ACTION PLAN")
        output_lines.append("-" * 40)
        
        if final_state.get("final_plan"):
            plan = final_state["final_plan"]
            print("\n✅ PLANNER OUTPUT:")
            print(f"   Task Type: {plan.get('task_type', 'N/A')}")
            
            if plan.get('chat_summary'):
                output_lines.append(f"\n{plan['chat_summary']}")
            
            if plan.get('timeline'):
                output_lines.append("\nDetailed Timeline:")
                output_lines.append(plan['timeline'])
            
            if plan.get('advisory'):
                output_lines.append("\nStrategic Advisory:")
                output_lines.append(plan['advisory'])
        else:
            print("\n⚠️ No planner output")
            output_lines.append("\nNo detailed plan generated.")
        
        output_lines.append("")
        output_lines.append("")
        
        # 4. Final Reply
        output_lines.append("SECTION 4: EXECUTIVE SUMMARY")
        output_lines.append("-" * 40)
        
        if final_state.get("final_reply"):
            print("\n✅ FINAL REPLY:")
            print(f"   {final_state['final_reply'][:200]}...")
            output_lines.append(f"\n{final_state['final_reply']}")
        else:
            output_lines.append("\nNo final summary generated.")
        
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("END OF REPORT")
        output_lines.append("=" * 80)
        
        # Write to file
        output_dir = os.path.join(os.path.dirname(__file__), "outputs")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"paymasry_series_a_plan_{timestamp}.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        
        print("\n" + "=" * 80)
        print(f"📄 PLAN EXPORTED TO: {output_file}")
        print("=" * 80)
        
        # Summary stats
        print("\n📈 WORKFLOW STATS:")
        print(f"   - Research Offline: {'✅' if final_state.get('research_offline') else '❌'}")
        print(f"   - Research Online: {'✅' if final_state.get('research_online') else '❌'}")
        print(f"   - Planner Output: {'✅' if final_state.get('final_plan') else '❌'}")
        print(f"   - Final Reply: {'✅' if final_state.get('final_reply') else '❌'}")
        
        return final_state, output_file
        
    except Exception as e:
        print(f"\n❌ WORKFLOW FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_research_to_planner_handoff():
    """Test that research results are properly passed to planner."""
    
    print("\n\n")
    print("=" * 80)
    print("🔗 TESTING RESEARCH -> PLANNER HANDOFF")
    print("=" * 80)
    
    # Simpler request focused on planning with research
    simple_request = """
    I need a 30-day plan to prepare for investor meetings. 
    Research what Egyptian fintech investors look for, then create the plan.
    """
    
    initial_state = {
        "messages": [HumanMessage(content=simple_request)],
        "user_context": {
            "business_name": "PayMasry",
            "business_type": "FinTech",
            "stage": "Seed",
            "goals": "Prepare for Series A investor meetings"
        },
        "gap_analysis": {
            "summary": "Need to improve pitch deck and financial projections",
            "critical_gaps": [
                {"area": "Pitch Deck", "gap": "Outdated, missing traction metrics"}
            ]
        },
        "action": None,
        "next_agent": None,
        "search_query": None,
        "task_type": None,
        "final_plan": None,
        "research_offline": None,
        "research_online": None,
        "final_reply": None,
    }
    
    try:
        print("\n🔄 Running orchestrator...")
        final_state = master_app.invoke(initial_state)
        
        # Check handoff
        research_done = bool(final_state.get("research_offline") or final_state.get("research_online"))
        planner_done = bool(final_state.get("final_plan"))
        
        print("\n📊 HANDOFF RESULTS:")
        print(f"   Research completed: {'✅' if research_done else '❌'}")
        print(f"   Planner executed: {'✅' if planner_done else '❌'}")
        
        if research_done and planner_done:
            print("\n✅ HANDOFF TEST PASSED: Research -> Planner flow working")
        elif research_done and not planner_done:
            print("\n⚠️ Research done but planner not triggered")
        else:
            print("\n⚠️ Research may have been skipped")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n" + "🌟" * 40)
    print("PAYMASRY SERIES A PREPARATION - FULL WORKFLOW TEST")
    print("🌟" * 40)
    
    # Run main workflow test
    final_state, output_file = run_full_workflow_test()
    
    if output_file:
        print(f"\n\n📂 Open the plan at: {output_file}")
    
    # Optional: Run handoff test
    # test_research_to_planner_handoff()
    
    print("\n\n✅ TEST SUITE COMPLETED")
