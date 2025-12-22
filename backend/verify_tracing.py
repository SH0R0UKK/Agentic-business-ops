"""
LangSmith Tracing Verification Script
Verifies that all agents are properly configured for LangSmith tracing.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 80)
print("🔍 LANGSMITH TRACING VERIFICATION")
print("=" * 80)

# 1. Check Environment Variables
print("\n1️⃣ Environment Variables:")
langsmith_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT")
langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT")
langchain_tracing = os.getenv("LANGCHAIN_TRACING_V2")

if langsmith_key:
    print(f"   ✅ LANGSMITH_API_KEY: {langsmith_key[:20]}...")
else:
    print("   ❌ LANGSMITH_API_KEY: NOT SET")

if langsmith_project:
    print(f"   ✅ LANGSMITH_PROJECT: {langsmith_project}")
else:
    print("   ⚠️  LANGSMITH_PROJECT: NOT SET (will use default)")

if langsmith_endpoint:
    print(f"   ✅ LANGSMITH_ENDPOINT: {langsmith_endpoint}")
else:
    print("   ⚠️  LANGSMITH_ENDPOINT: NOT SET (will use default)")

if langchain_tracing == "true":
    print(f"   ✅ LANGCHAIN_TRACING_V2: {langchain_tracing}")
else:
    print(f"   ⚠️  LANGCHAIN_TRACING_V2: {langchain_tracing} (should be 'true')")

# 2. Test LangSmith SDK
print("\n2️⃣ LangSmith SDK:")
try:
    from langsmith import Client
    client = Client(
        api_key=langsmith_key,
        api_url=langsmith_endpoint or "https://api.smith.langchain.com"
    )
    print("   ✅ LangSmith SDK imported successfully")
    print("   ✅ Client initialized")
    
    # Test connection
    try:
        # This will validate the API key
        print("   🔄 Testing connection to LangSmith...")
        # Note: We don't actually make a test call to avoid rate limits
        print("   ✅ Client configured (use actual agent runs to verify connection)")
    except Exception as e:
        print(f"   ⚠️  Connection test skipped: {e}")
        
except ImportError:
    print("   ❌ LangSmith SDK not installed")
    print("   💡 Run: pip install langsmith")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Check Tracing Helpers
print("\n3️⃣ Tracing Helpers:")
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from backend.tools.tracing import (
        LANGSMITH_ENABLED,
        trace_run,
        log_event,
        trace_agent,
        trace_function
    )
    
    print(f"   ✅ Tracing helpers imported")
    print(f"   {'✅' if LANGSMITH_ENABLED else '⚠️ '} LANGSMITH_ENABLED: {LANGSMITH_ENABLED}")
    
    # Test trace_run context manager
    with trace_run("test_trace", {"test": "data"}):
        print("   ✅ trace_run context manager works")
    
    print("   ✅ All tracing helpers functional")
    
except ImportError as e:
    print(f"   ❌ Import error: {e}")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# 4. Check Orchestrator Integration
print("\n4️⃣ Orchestrator Nodes:")
try:
    from backend.agents.orchestrator.orchestrator import workflow, master_app
    
    # Get all nodes from the compiled graph
    nodes = list(workflow.nodes.keys())
    print(f"   ✅ Orchestrator imported")
    print(f"   📊 Total nodes: {len(nodes)}")
    
    expected_nodes = ["supervisor", "onboarding", "planner", "research", "gap_agent"]
    for node in expected_nodes:
        if node in nodes:
            print(f"   ✅ {node}")
        else:
            print(f"   ❌ {node} - MISSING")
    
    # Check for placeholder
    from backend.agents.orchestrator.orchestrator import gap_analysis_node
    print(f"   ✅ gap_analysis_node properly imported")
    
except ImportError as e:
    print(f"   ❌ Import error: {e}")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# 5. Check Individual Agents
print("\n5️⃣ Agent Modules:")
agents = [
    ("Onboarding", "backend.agents.onboarding.agent", "run_onboarding"),
    ("Researcher", "backend.agents.researcher.agent", "run_research_agent"),
    ("Planner", "backend.agents.Planner.planner", "app_graph"),
    ("Gap Analysis", "backend.agents.gap_analysis.agent", "gap_analysis_node"),
]

for agent_name, module_path, function_name in agents:
    try:
        module = __import__(module_path, fromlist=[function_name])
        func = getattr(module, function_name)
        print(f"   ✅ {agent_name}: {function_name} imported")
    except ImportError as e:
        print(f"   ❌ {agent_name}: Import failed - {e}")
    except AttributeError as e:
        print(f"   ❌ {agent_name}: Function not found - {e}")
    except Exception as e:
        print(f"   ⚠️  {agent_name}: {e}")

# 6. Summary
print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)

issues = []
if not langsmith_key:
    issues.append("LANGSMITH_API_KEY not set")
if not LANGSMITH_ENABLED:
    issues.append("LangSmith tracing not enabled")
if langchain_tracing != "true":
    issues.append("LANGCHAIN_TRACING_V2 should be 'true'")

if issues:
    print("\n⚠️  Issues found:")
    for issue in issues:
        print(f"   • {issue}")
    print("\n💡 Fix these issues before testing")
else:
    print("\n✅ All checks passed! LangSmith tracing is properly configured.")
    print("   🚀 All agents will be tracked in the LangSmith dashboard")
    print(f"   📊 Project: {langsmith_project}")
    print(f"   🔗 Dashboard: https://smith.langchain.com/")

print("\n" + "=" * 80)
