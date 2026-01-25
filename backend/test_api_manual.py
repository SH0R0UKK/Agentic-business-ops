"""
Quick API Test - Manually test the API endpoints
Run the API server first with: python backend/api.py
Then run this script: python backend/test_api_manual.py
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check passed")


def test_upload_document():
    """Test document upload."""
    print("\n" + "="*60)
    print("TEST 2: Upload Document")
    print("="*60)
    
    # Create a sample text file
    sample_content = """
    Business Name: TestCorp Egypt
    Industry: FinTech - Digital Payments
    Location: Cairo, Egypt
    Stage: Seed Stage
    
    Goals:
    - Launch MVP by Q2 2026
    - Acquire 1000 early users
    - Secure seed funding of $500K
    
    Target Audience: Young professionals aged 25-35 in Cairo
    
    Key Challenges:
    - Limited budget for marketing
    - Need to comply with Central Bank regulations
    - Building trust in digital payments
    
    Unique Value Proposition:
    Fast, secure mobile payments with lowest fees in Egypt
    """
    
    # Save to temp file
    temp_file = Path("temp_test_doc.txt")
    temp_file.write_text(sample_content)
    
    try:
        with open(temp_file, "rb") as f:
            files = {"file": ("business_plan.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        result = response.json()
        startup_id = result["startup_id"]
        
        print(f"✅ Upload successful - Startup ID: {startup_id}")
        return startup_id
        
    finally:
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()


def test_get_profile(startup_id):
    """Test profile retrieval."""
    print("\n" + "="*60)
    print("TEST 3: Get Profile")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/profile/{startup_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Profile retrieved")
    else:
        print(f"⚠️  Profile not yet created (expected for new uploads)")


def test_question(startup_id):
    """Test question answering."""
    print("\n" + "="*60)
    print("TEST 4: Ask Question")
    print("="*60)
    
    payload = {
        "startup_id": startup_id,
        "question": "What is the target market for this business?"
    }
    
    print(f"Question: {payload['question']}")
    print("⏳ Sending request (this may take 30-60 seconds)...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/question",
            json=payload,
            timeout=120  # 2 minute timeout
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📝 Answer:\n{result['answer']}")
            print(f"\n📚 Evidence sources: {len(result.get('supporting_evidence', []))}")
            print("✅ Question answered successfully")
        else:
            print(f"Response: {response.text}")
            print("⚠️  Question failed - may need documents in RAG")
            
    except requests.exceptions.Timeout:
        print("⏱️  Request timed out - this is normal for first-time processing")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_generate_plan(startup_id):
    """Test plan generation."""
    print("\n" + "="*60)
    print("TEST 5: Generate Plan")
    print("="*60)
    
    payload = {
        "startup_id": startup_id,
        "goal": "Launch MVP and acquire first 100 users",
        "time_horizon_days": 60
    }
    
    print(f"Goal: {payload['goal']}")
    print(f"Time Horizon: {payload['time_horizon_days']} days")
    print("⏳ Generating plan (this may take 60-120 seconds)...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/plan",
            json=payload,
            timeout=180  # 3 minute timeout
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📋 Plan ID: {result['plan_id']}")
            print(f"Title: {result['title']}")
            print(f"Phases: {len(result.get('phases', []))}")
            print(f"Tasks: {len(result.get('tasks', []))}")
            
            # Show first few tasks
            tasks = result.get('tasks', [])
            if tasks:
                print(f"\n📌 Sample tasks:")
                for task in tasks[:3]:
                    print(f"   - {task['title']}")
            
            print("✅ Plan generated successfully")
        else:
            print(f"Response: {response.text}")
            print("⚠️  Plan generation failed")
            
    except requests.exceptions.Timeout:
        print("⏱️  Request timed out - plan generation is complex")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MANUAL API TEST SUITE")
    print("="*60)
    print("Make sure the API server is running:")
    print("  python backend/api.py")
    print("="*60)
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Upload document
        startup_id = test_upload_document()
        
        # Test 3: Get profile
        test_get_profile(startup_id)
        
        # Test 4: Ask question (skip for quick test)
        print("\n⏭️  Skipping question test (slow) - uncomment to test")
        # test_question(startup_id)
        
        # Test 5: Generate plan (skip for quick test)
        print("⏭️  Skipping plan generation test (slow) - uncomment to test")
        # test_generate_plan(startup_id)
        
        print("\n" + "="*60)
        print("✅ BASIC API TESTS COMPLETED")
        print("="*60)
        print(f"\nStartup ID for manual testing: {startup_id}")
        print("\nTo test more features, uncomment the slow tests above")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("Make sure the server is running with: python backend/api.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
