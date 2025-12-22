"""
Startup verification script for Agentic Business Ops backend.
Checks dependencies, environment, and runs basic health checks.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Verify Python version."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Verify required packages are installed."""
    print("\n📦 Checking dependencies...")
    
    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "langgraph",
        "langchain_openai",
        "chromadb",
        "sentence_transformers",
        "pypdf",
        "dotenv"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def check_environment():
    """Verify environment variables."""
    print("\n🔑 Checking environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Required
    perplexity_key = os.getenv("PERPLEXITY_API_KEY") or os.getenv("PPLX_API_KEY")
    
    if not perplexity_key:
        print("  ❌ PERPLEXITY_API_KEY - NOT SET")
        print("     Set in .env file or environment")
        return False
    else:
        print(f"  ✅ PERPLEXITY_API_KEY - {perplexity_key[:10]}...")
    
    # Optional
    langsmith_key = os.getenv("LANGSMITH_API_KEY")
    if langsmith_key:
        print(f"  ✅ LANGSMITH_API_KEY - {langsmith_key[:10]}... (tracing enabled)")
    else:
        print("  ℹ️  LANGSMITH_API_KEY - not set (tracing disabled, this is OK)")
    
    return True


def check_directory_structure():
    """Verify directory structure."""
    print("\n📁 Checking directory structure...")
    
    backend_dir = Path(__file__).parent
    
    required_dirs = [
        "agents",
        "agents/onboarding",
        "agents/researcher",
        "agents/Planner",
        "agents/orchestrator",
        "data",
        "data/db",
        "tools",
        "tests"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = backend_dir / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ - MISSING")
            all_exist = False
    
    return all_exist


def check_database():
    """Initialize and check database."""
    print("\n💾 Checking database...")
    
    try:
        from backend.data.db.storage import init_db, get_connection
        
        init_db()
        print("  ✅ Database initialized")
        
        # Test connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"  ✅ Tables: {', '.join(tables)}")
        return True
        
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False


def check_models():
    """Verify models can be imported."""
    print("\n🔧 Checking models...")
    
    try:
        from backend.agents.models import (
            OnboardingRequest, StartupProfile,
            ResearchRequest, ResearchResponse,
            PlanRequest, Plan
        )
        print("  ✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Model import error: {e}")
        return False


def check_api():
    """Check if API can be imported."""
    print("\n🌐 Checking API...")
    
    try:
        from backend.main import app
        print("  ✅ FastAPI app imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ API import error: {e}")
        return False


def main():
    """Run all checks."""
    print("="*70)
    print("🚀 AGENTIC BUSINESS OPS - BACKEND VERIFICATION")
    print("="*70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Directory Structure", check_directory_structure),
        ("Database", check_database),
        ("Models", check_models),
        ("API", check_api)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! Backend is ready to run.")
        print("\nStart the server with:")
        print("  python backend/main.py")
        print("  or")
        print("  uvicorn backend.main:app --reload")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
