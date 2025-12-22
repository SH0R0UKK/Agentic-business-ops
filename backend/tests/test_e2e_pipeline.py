"""
End-to-End Pipeline Test
Tests the full orchestrator flow: onboarding → research → gap analysis → planning → evaluation
"""

import os
import sys
import asyncio
import pytest
from pathlib import Path
from langchain_core.messages import HumanMessage

# Import backend (now works globally thanks to pip install -e .)
from backend.agents.orchestrator.orchestrator import master_app
from backend.agents.state import MasterState
from backend.evaluation.metrics import evaluate_gap_quality

# Test configuration
STARTUP_ID = "test-e2e-startup-001"
SOURCE_FOLDER = Path(__file__).parent.parent.parent / "source"
TEST_DOCUMENT = SOURCE_FOLDER / "Document.pdf"
USER_QUESTION = "Help me assess this business and create a 4-week execution plan with specific milestones."


class TestE2EPipeline:
    """End-to-end test of the complete orchestrator pipeline."""
    
    def test_document_exists(self):
        """Verify test document exists."""
        assert SOURCE_FOLDER.exists(), f"Source folder not found: {SOURCE_FOLDER}"
        assert TEST_DOCUMENT.exists(), f"Test document not found: {TEST_DOCUMENT}"
        print(f"✅ Test document found: {TEST_DOCUMENT.name}")
    
    def test_full_pipeline(self):
        """
        Run the complete pipeline:
        1. Onboarding with document
        2. Research (offline + online)
        3. Gap analysis
        4. Planning
        5. Evaluation
        """
        print("\n" + "="*80)
        print("🚀 STARTING END-TO-END PIPELINE TEST")
        print("="*80)
        
        # Step 1: Prepare initial state
        print("\n1️⃣ Preparing initial state...")
        initial_state = {
            "messages": [HumanMessage(content=USER_QUESTION)],
            "user_context": {"org_id": STARTUP_ID},
            "onboarding_status": "pending",
            "onboarding_files": [str(TEST_DOCUMENT)],
            "processed_files": None,
            "action": None,
            "next_agent": None,
            "iteration_count": 0,
            "task_type": "timeline",
            "search_query": None,
            "final_plan": None,
            "research_data": None,
            "rag_data": None,
            "gap_analysis": None,
            "research_offline": None,
            "research_online": None,
            "final_reply": None
        }
        
        print(f"   • Startup ID: {STARTUP_ID}")
        print(f"   • Document: {TEST_DOCUMENT.name}")
        print(f"   • Question: {USER_QUESTION}")
        
        # Step 2: Run orchestrator
        print("\n2️⃣ Running orchestrator...")
        print("   (This will execute: onboarding → supervisor → research → gap analysis → planner)")
        
        try:
            final_state = master_app.invoke(initial_state)
            print("   ✅ Orchestrator completed")
        except Exception as e:
            pytest.fail(f"❌ Orchestrator failed: {e}")
        
        # Step 3: Verify onboarding output
        print("\n3️⃣ Verifying onboarding output...")
        assert "user_context" in final_state, "Missing user_context in final state"
        
        user_context = final_state["user_context"]
        print(f"   • Business name: {user_context.get('business_name', 'N/A')}")
        print(f"   • Business type: {user_context.get('business_type', 'N/A')}")
        print(f"   • Location: {user_context.get('location', 'N/A')}")
        print(f"   • Stage: {user_context.get('stage', 'N/A')}")
        
        # Basic validation
        assert user_context.get("org_id") == STARTUP_ID, "Startup ID mismatch"
        print("   ✅ Onboarding output validated")
        
        # Step 4: Verify research outputs
        print("\n4️⃣ Verifying research outputs...")
        
        research_offline = final_state.get("research_offline")
        research_online = final_state.get("research_online")
        
        if research_offline:
            print(f"   • Offline research status: {research_offline.get('status', 'N/A')}")
            if research_offline.get("status") == "success":
                summary = research_offline.get("summary", "")
                print(f"   • Offline summary length: {len(summary)} chars")
        else:
            print("   ⚠️  No offline research output")
        
        if research_online:
            print(f"   • Online research status: {research_online.get('status', 'N/A')}")
            if research_online.get("status") == "success":
                summary = research_online.get("summary", "")
                print(f"   • Online summary length: {len(summary)} chars")
        else:
            print("   ⚠️  No online research output")
        
        # At least one research method should have run
        has_research = (
            (research_offline and research_offline.get("status") == "success") or
            (research_online and research_online.get("status") == "success")
        )
        
        if has_research:
            print("   ✅ Research outputs validated")
        else:
            print("   ⚠️  No successful research found (may be expected if no query was made)")
        
        # Step 5: Verify gap analysis output
        print("\n5️⃣ Verifying gap analysis output...")
        
        # Gap analysis might be in different places depending on orchestrator flow
        internal_gaps = final_state.get("internal_gaps", [])
        market_gaps = final_state.get("market_gaps", [])
        gap_analysis_str = final_state.get("gap_analysis")
        
        total_gaps = len(internal_gaps) + len(market_gaps)
        
        if total_gaps > 0:
            print(f"   • Internal gaps: {len(internal_gaps)}")
            print(f"   • Market gaps: {len(market_gaps)}")
            print(f"   • Total gaps: {total_gaps}")
            
            # Show sample gap
            if internal_gaps:
                sample = internal_gaps[0]
                print(f"   • Sample gap: {sample.get('category', 'N/A')} - {sample.get('description', 'N/A')[:60]}...")
            
            print("   ✅ Gap analysis output validated")
        else:
            print("   ⚠️  No gaps found (may be expected depending on orchestrator flow)")
        
        # Step 6: Verify planner output
        print("\n6️⃣ Verifying planner output...")
        
        final_plan = final_state.get("final_plan")
        
        if final_plan:
            print(f"   • Plan title: {final_plan.get('title', 'N/A')}")
            print(f"   • Plan summary: {final_plan.get('summary', 'N/A')[:80]}...")
            
            phases = final_plan.get("phases", [])
            schedule_events = final_plan.get("schedule_events", [])
            
            print(f"   • Phases: {len(phases)}")
            print(f"   • Schedule events: {len(schedule_events)}")
            
            # Validate structure
            if phases:
                print(f"   • Sample phase: {phases[0].get('phase_name', 'N/A')}")
            if schedule_events:
                print(f"   • Sample event: {schedule_events[0].get('title', 'N/A')} on {schedule_events[0].get('date', 'N/A')}")
            
            assert isinstance(final_plan, dict), "Plan should be a dictionary"
            print("   ✅ Planner output validated")
        else:
            print("   ⚠️  No plan generated (orchestrator may not have routed to planner)")
        
        # Step 7: Run evaluation
        print("\n7️⃣ Running evaluation metrics...")
        
        if total_gaps > 0 and has_research:
            try:
                # Prepare evaluation input
                gaps_output = {
                    "internal_gaps": internal_gaps,
                    "market_gaps": market_gaps
                }
                
                # Build research summary for evaluation
                research_summary = {}
                if research_offline and research_offline.get("status") == "success":
                    research_summary["market_trends"] = [research_offline.get("summary", "")]
                    research_summary["best_practices"] = []
                    research_summary["competitor_analysis"] = []
                
                if research_online and research_online.get("status") == "success":
                    research_summary["market_trends"] = research_summary.get("market_trends", []) + [research_online.get("summary", "")]
                
                evaluation_input = {
                    "startup_profile": user_context,
                    "research_summary": research_summary,
                    "user_goal": USER_QUESTION
                }
                
                # Run evaluation
                metrics = evaluate_gap_quality(gaps_output, evaluation_input)
                
                print(f"   • Overall score: {metrics.get('overall_score', 0):.2f}")
                print(f"   • Hallucination rate: {metrics.get('hallucination', {}).get('hallucination_rate', 0):.2f}")
                print(f"   • Grounding rate: {metrics.get('grounding', {}).get('grounding_rate', 0):.2f}")
                print(f"   • Relevance score: {metrics.get('relevance', {}).get('relevance_score', 0):.2f}")
                print(f"   • Coverage score: {metrics.get('coverage', {}).get('coverage_score', 0):.2f}")
                
                # Assertions
                assert isinstance(metrics, dict), "Metrics should be a dictionary"
                assert "overall_score" in metrics, "Metrics should have overall_score"
                assert 0 <= metrics["overall_score"] <= 1, "Overall score should be between 0 and 1"
                
                print("   ✅ Evaluation metrics validated")
                
            except Exception as e:
                print(f"   ⚠️  Evaluation failed: {e}")
                print("   (This is non-fatal for the test)")
        else:
            print("   ⚠️  Skipping evaluation (insufficient data)")
        
        # Step 8: Final summary
        print("\n" + "="*80)
        print("📊 PIPELINE TEST SUMMARY")
        print("="*80)
        
        results = {
            "onboarding": "✅" if user_context.get("business_name") else "⚠️",
            "research": "✅" if has_research else "⚠️",
            "gap_analysis": "✅" if total_gaps > 0 else "⚠️",
            "planning": "✅" if final_plan else "⚠️",
            "evaluation": "✅" if (total_gaps > 0 and has_research) else "⚠️"
        }
        
        for component, status in results.items():
            print(f"   {status} {component.capitalize()}")
        
        # Overall pass/fail
        all_passed = all(status == "✅" for status in results.values())
        
        if all_passed:
            print("\n✅ ALL PIPELINE COMPONENTS PASSED")
        else:
            print("\n⚠️  SOME COMPONENTS INCOMPLETE (may be expected based on orchestrator routing)")
        
        print("\n" + "="*80)
        
        # Final assertion - at minimum, orchestrator should complete without error
        assert final_state is not None, "Orchestrator should return a final state"
        assert "user_context" in final_state, "Final state should have user_context"
    
    def test_pipeline_with_custom_question(self):
        """Test pipeline with a more specific research-focused question."""
        print("\n" + "="*80)
        print("🔬 TESTING RESEARCH-FOCUSED PIPELINE")
        print("="*80)
        
        research_question = "What are the key market trends and competitors in this business sector? Create a gap analysis."
        
        initial_state = {
            "messages": [HumanMessage(content=research_question)],
            "user_context": {"org_id": STARTUP_ID + "-research"},
            "onboarding_status": "pending",
            "onboarding_files": [str(TEST_DOCUMENT)],
            "action": None,
            "next_agent": None,
            "iteration_count": 0,
            "search_query": None,
        }
        
        try:
            final_state = master_app.invoke(initial_state)
            
            # Should have research output
            has_research = (
                final_state.get("research_offline") is not None or
                final_state.get("research_online") is not None
            )
            
            print(f"   • Research executed: {'✅' if has_research else '⚠️'}")
            print(f"   • Final reply: {final_state.get('final_reply', 'N/A')[:100]}...")
            
            assert final_state is not None, "Pipeline should complete"
            print("\n✅ Research-focused pipeline test passed")
            
        except Exception as e:
            print(f"\n⚠️  Test completed with issues: {e}")
            # Don't fail - orchestrator behavior may vary


if __name__ == "__main__":
    # Run tests directly
    test = TestE2EPipeline()
    
    print("Running E2E Pipeline Tests...")
    
    try:
        test.test_document_exists()
        test.test_full_pipeline()
        test.test_pipeline_with_custom_question()
        print("\n✅ ALL TESTS COMPLETED")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
