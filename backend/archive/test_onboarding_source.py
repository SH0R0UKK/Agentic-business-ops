"""
Onboarding Source Test
======================
Tests the orchestrator pipeline with files from the source folder.
The pipeline ALWAYS starts with onboarding, which auto-detects files in source/.

Test Scenarios:
1. Auto-onboarding from source folder
2. Full pipeline: onboarding → research → planning
3. Source folder with custom question
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from agents.orchestrator.orchestrator import master_app

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

SOURCE_DIR = Path(__file__).parent.parent / "source"

# Check what files are in source folder
SOURCE_FILES = []
if SOURCE_DIR.exists():
    SOURCE_FILES = [str(f) for f in SOURCE_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]

print(f"\n{'='*80}")
print("SOURCE FOLDER FILES")
print(f"{'='*80}")
print(f"Location: {SOURCE_DIR}")
print(f"Files found: {len(SOURCE_FILES)}")
for f in SOURCE_FILES:
    print(f"  - {Path(f).name}")
print(f"{'='*80}\n")

# ============================================================================
# TEST 1: AUTO-ONBOARDING FROM SOURCE FOLDER
# ============================================================================

def test_auto_onboarding():
    """Test automatic onboarding from source folder."""
    print("\n" + "="*80)
    print("TEST 1: AUTO-ONBOARDING FROM SOURCE FOLDER")
    print("="*80)
    
    initial_state = {
        "messages": [HumanMessage(content="Please analyze my business documents and provide a summary.")],
        "user_context": {"org_id": "test_company_source"},
        "onboarding_files": None,  # Will auto-detect from source folder
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
    
    print("\n🔄 Running orchestrator with auto-onboarding...")
    
    try:
        final_state = master_app.invoke(initial_state)
        
        print("\n" + "="*80)
        print("ONBOARDING RESULTS")
        print("="*80)
        
        if final_state.get("onboarding_status") == "completed":
            context = final_state.get("user_context", {})
            print(f"\n✅ Onboarding Status: {final_state['onboarding_status']}")
            print(f"\nExtracted Business Context:")
            print(f"   Business Name: {context.get('business_name', 'N/A')}")
            print(f"   Business Type: {context.get('business_type', 'N/A')}")
            print(f"   Location: {context.get('location', 'N/A')}")
            print(f"   Stage: {context.get('stage', 'N/A')}")
            print(f"   Goals: {', '.join(context.get('goals', []))}")
            print(f"   Target Audience: {context.get('target_audience', 'N/A')}")
            print(f"   Sector: {context.get('sector', 'N/A')}")
            print(f"\n   Documents Processed:")
            for doc in context.get('available_documents', []):
                print(f"      • {doc}")
        else:
            print(f"⚠️ Onboarding Status: {final_state.get('onboarding_status', 'unknown')}")
        
        # Show final reply
        if final_state.get("final_reply"):
            print(f"\n" + "="*80)
            print("ASSISTANT RESPONSE")
            print("="*80)
            print(final_state['final_reply'])
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 2: FULL PIPELINE WITH BUSINESS QUESTION
# ============================================================================

def test_full_pipeline():
    """Test complete pipeline: onboarding → research → planning."""
    print("\n\n" + "="*80)
    print("TEST 2: FULL PIPELINE (ONBOARDING → RESEARCH → PLANNING)")
    print("="*80)
    
    business_question = """
    Based on my business context, create a 60-day growth plan that includes:
    1. Market research on our sector
    2. Competitive analysis
    3. Actionable milestones with responsible parties
    4. Budget considerations
    """
    
    initial_state = {
        "messages": [HumanMessage(content=business_question)],
        "user_context": {"org_id": "test_company_pipeline"},
        "onboarding_files": None,  # Auto-detect
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
    
    print(f"\n💬 User Question: {business_question[:100]}...")
    print("\n🔄 Running full pipeline...")
    
    try:
        final_state = master_app.invoke(initial_state)
        
        # Build comprehensive report
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append("BUSINESS ADVISORY REPORT")
        output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        # Section 1: Onboarding Results
        output_lines.append("SECTION 1: BUSINESS CONTEXT (FROM ONBOARDING)")
        output_lines.append("-" * 40)
        
        if final_state.get("onboarding_status") == "completed":
            context = final_state.get("user_context", {})
            output_lines.append(f"Business Name: {context.get('business_name', 'N/A')}")
            output_lines.append(f"Business Type: {context.get('business_type', 'N/A')}")
            output_lines.append(f"Location: {context.get('location', 'N/A')}")
            output_lines.append(f"Stage: {context.get('stage', 'N/A')}")
            output_lines.append(f"Sector: {context.get('sector', 'N/A')}")
            output_lines.append(f"\nGoals:")
            for goal in context.get('goals', []):
                output_lines.append(f"  • {goal}")
            output_lines.append(f"\nConstraints:")
            for constraint in context.get('constraints', []):
                output_lines.append(f"  • {constraint}")
            output_lines.append(f"\nTarget Audience: {context.get('target_audience', 'N/A')}")
            output_lines.append(f"\nDocuments Analyzed:")
            for doc in context.get('available_documents', []):
                output_lines.append(f"  • {doc}")
        else:
            output_lines.append(f"Status: {final_state.get('onboarding_status', 'N/A')}")
        
        output_lines.append("")
        output_lines.append("")
        
        # Section 2: Research Results
        output_lines.append("SECTION 2: MARKET RESEARCH")
        output_lines.append("-" * 40)
        
        if final_state.get("research_online"):
            research = final_state["research_online"]
            output_lines.append(f"Question: {research.get('question', 'N/A')}")
            output_lines.append(f"Status: {research.get('status', 'N/A')}")
            output_lines.append(f"\nExecutive Summary:")
            output_lines.append(research.get('summary', 'N/A'))
            
            if research.get('findings'):
                output_lines.append(f"\nKey Findings:")
                for finding in research['findings']:
                    output_lines.append(f"  • {finding}")
        else:
            output_lines.append("Research: Not performed")
        
        output_lines.append("")
        output_lines.append("")
        
        # Section 3: Action Plan
        output_lines.append("SECTION 3: ACTION PLAN")
        output_lines.append("-" * 40)
        
        if final_state.get("final_plan"):
            plan = final_state["final_plan"]
            if isinstance(plan, dict):
                output_lines.append(plan.get('structured_plan', 'N/A'))
                output_lines.append("")
                output_lines.append("Chat Summary:")
                output_lines.append(plan.get('chat_summary', 'N/A'))
            else:
                output_lines.append(str(plan))
        else:
            output_lines.append("Plan: Not generated")
        
        output_lines.append("")
        output_lines.append("")
        
        # Section 4: Final Reply
        output_lines.append("SECTION 4: EXECUTIVE SUMMARY")
        output_lines.append("-" * 40)
        
        if final_state.get("final_reply"):
            output_lines.append(final_state["final_reply"])
        
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("END OF REPORT")
        output_lines.append("=" * 80)
        
        # Save report
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"source_pipeline_test_{timestamp}.txt"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        
        print(f"\n📄 Report saved to: {output_file}")
        
        # Summary
        print("\n" + "="*80)
        print("WORKFLOW STATS")
        print("="*80)
        print(f"   Onboarding: {'✅' if final_state.get('onboarding_status') == 'completed' else '❌'}")
        print(f"   Research: {'✅' if final_state.get('research_online') else '❌'}")
        print(f"   Planning: {'✅' if final_state.get('final_plan') else '❌'}")
        print(f"   Final Reply: {'✅' if final_state.get('final_reply') else '❌'}")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 3: QUICK QUESTION AFTER ONBOARDING
# ============================================================================

def test_quick_question():
    """Test quick question after auto-onboarding."""
    print("\n\n" + "="*80)
    print("TEST 3: QUICK QUESTION AFTER ONBOARDING")
    print("="*80)
    
    initial_state = {
        "messages": [HumanMessage(content="What are the top 3 priorities for my business right now?")],
        "user_context": {"org_id": "test_company_quick"},
        "onboarding_files": None,  # Auto-detect
        "action": None,
        "next_agent": None,
        "search_query": None,
        "task_type": None,
        "final_plan": None,
        "research_offline": None,
        "research_online": None,
        "final_reply": None,
    }
    
    print("\n🔄 Running orchestrator...")
    
    try:
        final_state = master_app.invoke(initial_state)
        
        print("\n" + "="*80)
        print("RESULTS")
        print("="*80)
        print(f"   Onboarding: {'✅' if final_state.get('onboarding_status') == 'completed' else '⏭️ Skipped'}")
        
        if final_state.get('onboarding_status') == 'completed':
            context = final_state.get("user_context", {})
            print(f"   Business: {context.get('business_name', 'N/A')}")
        
        print(f"   Research: {'✅' if final_state.get('research_online') else '⏭️ Skipped'}")
        print(f"   Planning: {'✅' if final_state.get('final_plan') else '⏭️ Skipped'}")
        
        if final_state.get("final_reply"):
            print("\n" + "="*80)
            print("ASSISTANT RESPONSE")
            print("="*80)
            print(final_state["final_reply"])
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🌟"*40)
    print("ONBOARDING SOURCE FOLDER TEST SUITE")
    print("🌟"*40)
    
    if not SOURCE_FILES:
        print("\n⚠️  WARNING: No files found in source folder!")
        print(f"   Expected location: {SOURCE_DIR}")
        print("   Please add business documents (PDF, images, text files) to test onboarding.")
        print("\n   Detected files: None")
    else:
        print(f"\n✅ Found {len(SOURCE_FILES)} files in source folder - ready to test!")
    
    # Run all tests
    print("\n" + "="*80)
    print("STARTING TESTS")
    print("="*80)
    
    # Test 1: Auto-onboarding
    test_auto_onboarding()
    
    # Test 2: Full pipeline (only if we have files)
    if SOURCE_FILES:
        test_full_pipeline()
    
    # Test 3: Quick question
    test_quick_question()
    
    print("\n\n✅ TEST SUITE COMPLETED")
    print("="*80)
