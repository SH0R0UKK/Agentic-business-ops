"""
Simple test script for the API endpoints.
Run the server first: python -m uvicorn backend.api:app --port 8000
Then run this script: python backend/test_api.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing /api/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing /...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_upload():
    """Test file upload (using existing source file)"""
    print("\n🔍 Testing /api/upload...")
    try:
        # Use the existing PDF in source folder
        import os
        file_path = "source/Document.pdf"
        if not os.path.exists(file_path):
            print(f"   ⚠️ Test file not found: {file_path}")
            return False
        
        with open(file_path, "rb") as f:
            files = {"file": ("Document.pdf", f, "application/pdf")}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            return data.get("startup_id")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def test_question(startup_id: str):
    """Test question endpoint"""
    print(f"\n🔍 Testing /api/question for startup {startup_id}...")
    try:
        payload = {
            "startup_id": startup_id,
            "question": "What are the main goals of this business?"
        }
        response = requests.post(
            f"{BASE_URL}/api/question",
            json=payload,
            timeout=120
        )
        
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Answer: {data.get('answer', 'N/A')[:200]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_plan(startup_id: str):
    """Test plan generation endpoint"""
    print(f"\n🔍 Testing /api/plan for startup {startup_id}...")
    try:
        payload = {
            "startup_id": startup_id,
            "goal": "Increase online sales by 40%",
            "time_horizon_days": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/plan",
            json=payload,
            timeout=180
        )
        
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Plan ID: {data.get('plan_id', 'N/A')}")
        print(f"   Title: {data.get('title', 'N/A')}")
        print(f"   Phases: {len(data.get('phases', []))}")
        print(f"   Tasks: {len(data.get('tasks', []))}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 API Integration Test")
    print("=" * 60)
    
    # Test basic endpoints
    if not test_root():
        print("\n❌ Server not responding. Make sure it's running on port 8000")
        exit(1)
    
    test_health()
    
    # Test upload
    startup_id = test_upload()
    if startup_id:
        print(f"\n✅ Got startup_id: {startup_id}")
        
        # Uncomment below to test question/plan (takes time due to LLM calls)
        # test_question(startup_id)
        # test_plan(startup_id)
    
    print("\n" + "=" * 60)
    print("✅ Basic API tests completed!")
    print("=" * 60)
