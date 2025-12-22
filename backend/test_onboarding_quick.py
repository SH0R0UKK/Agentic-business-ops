"""
Quick test of onboarding agent directly (no orchestrator imports)
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# Direct import of onboarding module
from agents.orchestrator.onboarding.agent import run_onboarding

# Find source files
SOURCE_DIR = Path(__file__).parent.parent / "source"
source_files = []

if SOURCE_DIR.exists():
    source_files = [str(f) for f in SOURCE_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]

print("="*80)
print("ONBOARDING AGENT DIRECT TEST")
print("="*80)
print(f"\nSource Directory: {SOURCE_DIR}")
print(f"Files Found: {len(source_files)}")

if not source_files:
    print("\n⚠️ No files in source folder. Please add business documents.")
    sys.exit(1)

for f in source_files:
    print(f"  • {Path(f).name}")

print("\n" + "="*80)
print("RUNNING ONBOARDING...")
print("="*80)

try:
    result = run_onboarding(
        file_paths=source_files,
        org_id="test_direct"
    )
    
    print("\n" + "="*80)
    print("EXTRACTION RESULTS")
    print("="*80)
    
    context = result['user_context']
    print(f"\nBusiness Name: {context.get('business_name', 'N/A')}")
    print(f"Business Type: {context.get('business_type', 'N/A')}")
    print(f"Location: {context.get('location', 'N/A')}")
    print(f"Stage: {context.get('stage', 'N/A')}")
    print(f"Sector: {context.get('sector', 'N/A')}")
    
    print(f"\nGoals:")
    for goal in context.get('goals', []):
        print(f"  • {goal}")
    
    print(f"\nConstraints:")
    for constraint in context.get('constraints', []):
        print(f"  • {constraint}")
    
    print(f"\nTarget Audience: {context.get('target_audience', 'N/A')}")
    
    print(f"\nDocuments Processed:")
    for doc in context.get('available_documents', []):
        print(f"  • {doc}")
    
    print("\n✅ TEST COMPLETED SUCCESSFULLY")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
