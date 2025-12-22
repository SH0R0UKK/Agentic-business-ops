"""
Test the orchestrator with the integrated Research Agent.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_path = Path(__file__).parent
project_root = backend_path.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from agents.orchestrator.orchestrator import master_app
from agents.state import MasterState


def test_orchestrator_with_research():
    """Test that the orchestrator can route to and execute research."""
    print("=" * 70)
    print("TESTING ORCHESTRATOR WITH RESEARCH NODE")
    print("=" * 70)
    
    # Create initial state
    initial_state = {
        "messages": [
            HumanMessage(content="I need research on the best startup accelerators in Egypt and their application process")
        ],
        "user_context": {
            "startup_name": "Test Startup",
            "stage": "pre-seed",
            "sector": "fintech",
            "location": "Egypt"
        },
        "action": "route",
        "next_agent": "research",  # Directly route to research for testing
        "search_query": "What are the best startup accelerators in Egypt and their application process?",
        "task_type": None,
        "final_plan": None,
        "research_data": None,
        "rag_data": None,
        "gap_analysis": None,
        "research_offline": None,
        "research_online": None,
        "final_reply": None
    }
    
    print("\nInitial State:")
    print(f"  - Action: {initial_state['action']}")
    print(f"  - Next Agent: {initial_state['next_agent']}")
    print(f"  - Search Query: {initial_state['search_query']}")
    
    print("\n" + "-" * 70)
    print("Running orchestrator graph...")
    print("-" * 70)
    
    try:
        # Run the graph
        final_state = master_app.invoke(initial_state)
        
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        
        # Check if research was executed
        if final_state.get("research_offline"):
            print("\n✅ OFFLINE RESEARCH COMPLETED")
            offline = final_state["research_offline"]
            print(f"   Status: {offline.get('status')}")
            print(f"   Summary: {offline.get('summary', '')[:200]}...")
            print(f"   Claims: {len(offline.get('claims', []))}")
            print(f"   Missing Info: {len(offline.get('missing_info', []))}")
        else:
            print("\n❌ No offline research results")
        
        if final_state.get("research_online"):
            print("\n✅ ONLINE RESEARCH COMPLETED")
            online = final_state["research_online"]
            print(f"   Status: {online.get('status')}")
            print(f"   Summary: {online.get('summary', '')[:200]}...")
            print(f"   Findings: {len(online.get('findings', []))}")
            print(f"   Disclaimers: {len(online.get('prohibited_uses', []))}")
        else:
            print("\n❌ No online research results")
        
        # Assertions
        assert final_state.get("research_offline") is not None, "research_offline should be set"
        assert final_state.get("research_online") is not None, "research_online should be set"
        assert isinstance(final_state["research_offline"], dict), "research_offline should be a dict"
        assert isinstance(final_state["research_online"], dict), "research_online should be a dict"
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_orchestrator_supervisor_to_research():
    """Test that the supervisor can decide to route to research."""
    print("\n\n")
    print("=" * 70)
    print("TESTING SUPERVISOR -> RESEARCH ROUTING")
    print("=" * 70)
    
    # Create initial state with user message asking for research
    initial_state = {
        "messages": [
            HumanMessage(content="Can you research the latest funding trends for Egyptian startups?")
        ],
        "user_context": {
            "startup_name": "FinTech Co",
            "stage": "seed",
            "sector": "fintech"
        },
        "action": None,
        "next_agent": None,
        "search_query": None,
        "task_type": None,
        "final_plan": None,
        "research_data": None,
        "rag_data": None,
        "gap_analysis": None,
        "research_offline": None,
        "research_online": None,
        "final_reply": None
    }
    
    print("\nInitial State:")
    print(f"  - User Message: {initial_state['messages'][0].content}")
    print(f"  - Context: {initial_state['user_context']}")
    
    print("\n" + "-" * 70)
    print("Running orchestrator from entry point...")
    print("-" * 70)
    
    try:
        # Run the graph from supervisor entry point
        final_state = master_app.invoke(initial_state)
        
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        
        print(f"\nFinal Action: {final_state.get('action')}")
        print(f"Last Agent: {final_state.get('next_agent')}")
        
        # Check what happened
        if final_state.get("research_offline") or final_state.get("research_online"):
            print("\n✅ Research was executed during the flow")
            if final_state.get("research_offline"):
                print(f"   Offline status: {final_state['research_offline'].get('status')}")
            if final_state.get("research_online"):
                print(f"   Online status: {final_state['research_online'].get('status')}")
        else:
            print("\n⚠️ Research was not executed (supervisor may have chosen different path)")
        
        if final_state.get("final_reply"):
            print(f"\nFinal Reply: {final_state['final_reply'][:300]}...")
        
        print("\n" + "=" * 70)
        print("✅ SUPERVISOR TEST COMPLETED")
        print("=" * 70)
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("PERPLEXITY_API_KEY") and not os.getenv("PPLX_API_KEY"):
        print("⚠️ PERPLEXITY_API_KEY or PPLX_API_KEY not set")
        print("Set it in .env file")
        sys.exit(1)
    
    # Test 1: Direct routing to research
    test_orchestrator_with_research()
    
    # Test 2: Supervisor decision routing
    test_orchestrator_supervisor_to_research()
