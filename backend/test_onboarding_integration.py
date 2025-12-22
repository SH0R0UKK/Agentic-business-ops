"""
Full Onboarding Integration Test
==================================
Tests the complete pipeline:
1. Upload business documents (PDF, images)
2. Onboarding extracts business context
3. User asks a question
4. Research agent gathers market intel
5. Planner creates actionable plan
6. Output saved to file
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from agents.orchestrator.orchestrator import master_app

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

# Example files to upload (replace with your actual file paths)
ONBOARDING_FILES = [
    # Add your business document paths here
    # r"C:\path\to\business_plan.pdf",
    # r"C:\path\to\swot_analysis.png",
    # r"C:\path\to\company_overview.txt",
]

USER_QUESTION = """
We're planning to launch a new product line next quarter. 
Can you research market trends and create a 60-day go-to-market plan 
with specific milestones and responsible parties?
"""

ORG_ID = "test_company_001"

# ============================================================================
# TEST SCENARIOS
# ============================================================================

def test_onboarding_only():
    """Test onboarding alone without full workflow."""
    print("\n" + "=" * 80)
    print("TEST 1: ONBOARDING ONLY")
    print("=" * 80)
    
    if not ONBOARDING_FILES:
        print("⚠️  No files configured. Add file paths to ONBOARDING_FILES.")
        return None
    
    initial_state = {
        "messages": [HumanMessage(content="Please process my business documents.")],
        "user_context": {"org_id": ORG_ID},
        "onboarding_files": ONBOARDING_FILES,
        "onboarding_status": "pending",
        "action": None,
        "next_agent": None,
        "search_query": None,
        "task_type": None,
        "final_plan": None,
        "research_offline": None,
        "research_online": None,
        "final_reply": None,
    }
    
    print(f"\n📂 Uploading {len(ONBOARDING_FILES)} files...")
    for f in ONBOARDING_FILES:
        print(f"   - {Path(f).name}")
    
    try:
        final_state = master_app.invoke(initial_state)
        
        print("\n" + "=" * 80)
        print("ONBOARDING RESULTS")
        print("=" * 80)
        
        if final_state.get("onboarding_status") == "completed":
            context = final_state.get("user_context", {})
            print(f"\n✅ Onboarding Status: {final_state['onboarding_status']}")
            print(f"Business Name: {context.get('business_name', 'N/A')}")
            print(f"Business Type: {context.get('business_type', 'N/A')}")
            print(f"Location: {context.get('location', 'N/A')}")
            print(f"Stage: {context.get('stage', 'N/A')}")
            print(f"Goals: {len(context.get('goals', []))}")
            print(f"Constraints: {len(context.get('key_constraints', []))}")
            print(f"Documents: {len(context.get('available_documents', []))}")
        else:
            print(f"\n❌ Onboarding Status: {final_state.get('onboarding_status')}")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_full_pipeline_with_onboarding():
    """Test complete pipeline: onboarding -> research -> planning."""
    print("\n\n" + "=" * 80)
    print("TEST 2: FULL PIPELINE (ONBOARDING -> RESEARCH -> PLANNING)")
    print("=" * 80)
    
    if not ONBOARDING_FILES:
        print("⚠️  No files configured. Skipping full pipeline test.")
        print("   Add file paths to ONBOARDING_FILES to test this scenario.")
        return None
    
    initial_state = {
        "messages": [HumanMessage(content=USER_QUESTION)],
        "user_context": {"org_id": ORG_ID},
        "onboarding_files": ONBOARDING_FILES,  # Triggers onboarding
        "onboarding_status": "pending",
        "action": None,
        "next_agent": None,
        "search_query": None,
        "task_type": None,
        "final_plan": None,
        "research_offline": None,
        "research_online": None,
        "final_reply": None,
    }
    
    print(f"\n📂 Step 1: Onboarding {len(ONBOARDING_FILES)} files")
    print(f"💬 Step 2: User Question: {USER_QUESTION[:100]}...")
    
    try:
        print("\n🔄 Running full orchestrator pipeline...")
        final_state = master_app.invoke(initial_state)
        
        print("\n" + "=" * 80)
        print("PIPELINE RESULTS")
        print("=" * 80)
        
        # Collect results
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append("BUSINESS ADVISORY REPORT")
        output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        # 1. Onboarding Results
        output_lines.append("SECTION 1: BUSINESS CONTEXT (FROM ONBOARDING)")
        output_lines.append("-" * 40)
        
        if final_state.get("onboarding_status") == "completed":
            context = final_state.get("user_context", {})
            print(f"\n✅ Onboarding: {context.get('business_name', 'N/A')}")
            
            output_lines.append(f"\nBusiness Name: {context.get('business_name', 'N/A')}")
            output_lines.append(f"Business Type: {context.get('business_type', 'N/A')}")
            output_lines.append(f"Location: {context.get('location', 'N/A')}")
            output_lines.append(f"Stage: {context.get('stage', 'N/A')}")
            
            if context.get('goals'):
                output_lines.append("\nBusiness Goals:")
                for goal in context.get('goals', []):
                    output_lines.append(f"  - {goal}")
            
            if context.get('key_constraints'):
                output_lines.append("\nKey Constraints:")
                for constraint in context.get('key_constraints', []):
                    output_lines.append(f"  - {constraint}")
        else:
            print(f"\n⚠️  Onboarding: {final_state.get('onboarding_status')}")
            output_lines.append("\nOnboarding was not completed.")
        
        output_lines.append("")
        output_lines.append("")
        
        # 2. Research Results
        output_lines.append("SECTION 2: MARKET RESEARCH")
        output_lines.append("-" * 40)
        
        if final_state.get("research_online"):
            online = final_state["research_online"]
            print(f"\n✅ Research: {online.get('status')}")
            
            output_lines.append(f"\nSummary: {online.get('summary', 'N/A')}")
            output_lines.append("\nKey Findings:")
            for i, finding in enumerate(online.get('findings', []), 1):
                if isinstance(finding, dict):
                    output_lines.append(f"  {i}. {finding.get('pattern', finding)}")
                else:
                    output_lines.append(f"  {i}. {finding}")
        else:
            print("\n⚠️  No research conducted")
            output_lines.append("\nNo research was conducted.")
        
        output_lines.append("")
        output_lines.append("")
        
        # 3. Action Plan
        output_lines.append("SECTION 3: ACTION PLAN")
        output_lines.append("-" * 40)
        
        if final_state.get("final_plan"):
            plan = final_state["final_plan"]
            print(f"\n✅ Planning: Complete")
            
            if plan.get('strategy_advice'):
                output_lines.append(f"\n{plan['strategy_advice']}")
            
            if plan.get('schedule_events'):
                output_lines.append("\nScheduled Events:")
                for event in plan['schedule_events']:
                    output_lines.append(f"  - {event.get('date')}: {event.get('task')}")
                    output_lines.append(f"    {event.get('details')}")
        else:
            print("\n⚠️  No plan generated")
            output_lines.append("\nNo action plan was generated.")
        
        output_lines.append("")
        output_lines.append("")
        
        # 4. Final Reply
        output_lines.append("SECTION 4: EXECUTIVE SUMMARY")
        output_lines.append("-" * 40)
        
        if final_state.get("final_reply"):
            print(f"\n✅ Final Reply: {final_state['final_reply'][:100]}...")
            output_lines.append(f"\n{final_state['final_reply']}")
        
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("END OF REPORT")
        output_lines.append("=" * 80)
        
        # Save to file
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"onboarding_pipeline_test_{timestamp}.txt"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        
        print(f"\n📄 Report saved to: {output_file}")
        
        # Summary
        print("\n" + "=" * 80)
        print("WORKFLOW STATS")
        print("=" * 80)
        print(f"   - Onboarding: {'✅' if final_state.get('onboarding_status') == 'completed' else '❌'}")
        print(f"   - Research: {'✅' if final_state.get('research_online') else '❌'}")
        print(f"   - Planning: {'✅' if final_state.get('final_plan') else '❌'}")
        print(f"   - Final Reply: {'✅' if final_state.get('final_reply') else '❌'}")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_without_onboarding():
    """Test pipeline without onboarding (manual context)."""
    print("\n\n" + "=" * 80)
    print("TEST 3: WITHOUT ONBOARDING (MANUAL CONTEXT)")
    print("=" * 80)
    
    # Manually provided context (no file upload)
    manual_context = {
        "business_name": "TechStart Egypt",
        "business_type": "SaaS - Project Management",
        "location": "Cairo, Egypt",
        "stage": "MVP",
        "goals": [
            "Launch beta version in Q1",
            "Acquire 100 pilot users",
            "Raise seed funding"
        ],
        "sector": "technology"
    }
    
    initial_state = {
        "messages": [HumanMessage(content="Create a 30-day product launch plan with marketing milestones.")],
        "user_context": manual_context,  # Manual context provided
        "onboarding_files": None,  # No onboarding
        "action": None,
        "next_agent": None,
        "search_query": None,
        "task_type": None,
        "final_plan": None,
        "research_offline": None,
        "research_online": None,
        "final_reply": None,
    }
    
    print("\n📋 Using manual context (no file upload)")
    print(f"   Business: {manual_context['business_name']}")
    print(f"   Type: {manual_context['business_type']}")
    
    try:
        print("\n🔄 Running orchestrator...")
        final_state = master_app.invoke(initial_state)
        
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"   - Onboarding: Skipped (manual context)")
        print(f"   - Research: {'✅' if final_state.get('research_online') else '❌'}")
        print(f"   - Planning: {'✅' if final_state.get('final_plan') else '❌'}")
        print(f"   - Final Reply: {'✅' if final_state.get('final_reply') else '❌'}")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n" + "🌟" * 40)
    print("ONBOARDING INTEGRATION TEST SUITE")
    print("🌟" * 40)
    
    # Test 1: Onboarding only
    if ONBOARDING_FILES:
        test_onboarding_only()
        
        # Test 2: Full pipeline with onboarding
        test_full_pipeline_with_onboarding()
    else:
        print("\n⚠️  ONBOARDING_FILES is empty!")
        print("   Update the ONBOARDING_FILES list at the top of this file")
        print("   with paths to your business documents to test onboarding.\n")
    
    # Test 3: Without onboarding (works without files)
    test_without_onboarding()
    
    print("\n\n✅ TEST SUITE COMPLETED")
