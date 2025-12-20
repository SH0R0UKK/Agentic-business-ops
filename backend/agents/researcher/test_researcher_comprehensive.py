"""
Comprehensive test suite for the Research Agent.
Tests different flows, error handling, and edge cases.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from backend.agents.researcher import ResearchAgent, ResearchTask, ResearchResult

# Load environment variables
load_dotenv()

# Configure logging to see agent behavior
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class TestResearchAgent:
    def __init__(self):
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("❌ PERPLEXITY_API_KEY not found in .env file")
        
        self.agent = ResearchAgent(perplexity_api_key=api_key)
        print("✅ Research Agent initialized successfully\n")

    def test_basic_online_search(self):
        """Test 1: Basic online search with a simple query"""
        print("\n" + "="*70)
        print("TEST 1: Basic Online Search")
        print("="*70)
        
        task = ResearchTask(
            query="What is the capital of France?",
            grounding_rules=["Provide factual information only"]
        )
        
        result = self.agent.perform_research(task)
        
        assert result is not None, "Result should not be None"
        assert result.summary != "", "Summary should not be empty"
        assert result.confidence_score > 0, "Confidence score should be positive"
        
        print(f"\n✅ Test Passed!")
        print(result.to_markdown())
        return result

    def test_local_memory_hit(self):
        """Test 2: Local memory caching (second run should be faster)"""
        print("\n" + "="*70)
        print("TEST 2: Local Memory Cache Hit")
        print("="*70)
        
        # First query to populate memory
        task = ResearchTask(
            query="What is Python programming language?",
            grounding_rules=["Focus on current definition"]
        )
        
        print("\n📌 First Run (Online Search):")
        result1 = self.agent.perform_research(task)
        source1 = result1.source_type
        
        print(f"\n📌 Second Run (Should use local memory):")
        result2 = self.agent.perform_research(task)
        source2 = result2.source_type
        
        print(f"\nFirst search source: {source1}")
        print(f"Second search source: {source2}")
        
        # Second run should ideally be from local memory if confidence is high
        if result1.confidence_score >= 6:
            assert source2 == "local", "Second run should use local memory"
            print("✅ Local memory caching working correctly!")
        else:
            print(f"⚠️  First result confidence too low ({result1.confidence_score}), not cached")
        
        print(result2.to_markdown())
        return result2

    def test_error_handling_none_result(self):
        """Test 3: Graceful handling when API returns invalid data"""
        print("\n" + "="*70)
        print("TEST 3: Error Handling - Invalid/None Results")
        print("="*70)
        
        # Query that might return low confidence or error
        task = ResearchTask(
            query="xyzabc12345 nonsensical query that won't yield results",
            grounding_rules=["Attempt to find meaningful data"]
        )
        
        try:
            result = self.agent.perform_research(task)
            
            # Should return a result, even if it failed
            assert result is not None, "Should return ResearchResult even on error"
            assert isinstance(result, ResearchResult), "Result should be ResearchResult instance"
            
            print(f"\n✅ Error handled gracefully")
            print(f"Result Summary: {result.summary}")
            print(f"Confidence Score: {result.confidence_score}")
            print(f"Source: {result.source_type}")
            
        except Exception as e:
            print(f"❌ Test Failed with exception: {e}")
            raise

    def test_different_query_types(self):
        """Test 4: Various query types"""
        print("\n" + "="*70)
        print("TEST 4: Different Query Types")
        print("="*70)
        
        queries = [
            {
                "query": "Current Bitcoin price",
                "rules": ["Provide latest market data"]
            },
            {
                "query": "Top 5 programming languages in 2024",
                "rules": ["Base on latest surveys and usage statistics"]
            },
            {
                "query": "What are the side effects of common medications?",
                "rules": ["Cite medical sources only"]
            }
        ]
        
        results = []
        for i, query_config in enumerate(queries, 1):
            print(f"\n📌 Query {i}: {query_config['query'][:50]}...")
            
            task = ResearchTask(
                query=query_config['query'],
                grounding_rules=query_config['rules']
            )
            
            result = self.agent.perform_research(task)
            results.append(result)
            
            print(f"   ✅ Source: {result.source_type}, Confidence: {result.confidence_score}/10")
        
        assert len(results) == len(queries), "All queries should return results"
        print(f"\n✅ All {len(results)} queries completed successfully")
        return results

    def test_grounding_rules_compliance(self):
        """Test 5: Verify grounding rules are followed"""
        print("\n" + "="*70)
        print("TEST 5: Grounding Rules Compliance")
        print("="*70)
        
        task = ResearchTask(
            query="Recent developments in artificial intelligence",
            grounding_rules=[
                "Focus on post-2023 developments",
                "Cite peer-reviewed sources",
                "Include key statistics"
            ]
        )
        
        result = self.agent.perform_research(task)
        
        print(f"\n✅ Query executed with grounding rules:")
        for rule in task.grounding_rules:
            print(f"   - {rule}")
        
        print(f"\nResult:")
        print(result.to_markdown())
        
        assert len(result.citations) > 0, "Should have citations"
        print(f"\n✅ Got {len(result.citations)} citations")
        return result

    def test_confidence_score_validity(self):
        """Test 6: Verify confidence scores are valid (1-10)"""
        print("\n" + "="*70)
        print("TEST 6: Confidence Score Validity")
        print("="*70)
        
        tasks = [
            ResearchTask(query="What is water?", grounding_rules=[]),
            ResearchTask(query="Recent world events", grounding_rules=["Include 2024 data"]),
            ResearchTask(query="Market trends", grounding_rules=["Financial data only"])
        ]
        
        for i, task in enumerate(tasks, 1):
            result = self.agent.perform_research(task)
            
            assert 0 <= result.confidence_score <= 10, \
                f"Confidence score must be 0-10, got {result.confidence_score}"
            
            print(f"✅ Task {i}: Confidence score {result.confidence_score}/10 is valid")
        
        print(f"\n✅ All confidence scores are valid (0-10 range)")

    def test_result_structure(self):
        """Test 7: Verify result structure is complete"""
        print("\n" + "="*70)
        print("TEST 7: Result Structure Validation")
        print("="*70)
        
        task = ResearchTask(
            query="What is machine learning?",
            grounding_rules=[]
        )
        
        result = self.agent.perform_research(task)
        
        # Check all required fields
        required_fields = ['summary', 'key_statistics', 'citations', 'source_type', 'confidence_score']
        for field in required_fields:
            assert hasattr(result, field), f"Result missing field: {field}"
            print(f"✅ Field '{field}' present: {getattr(result, field)}")
        
        print(f"\n✅ Result structure is complete and valid")

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "🚀 "*20)
        print("STARTING COMPREHENSIVE RESEARCH AGENT TESTS")
        print("🚀 "*20 + "\n")
        
        try:
            self.test_basic_online_search()
            self.test_local_memory_hit()
            self.test_error_handling_none_result()
            self.test_different_query_types()
            self.test_grounding_rules_compliance()
            self.test_confidence_score_validity()
            self.test_result_structure()
            
            print("\n" + "✅ "*20)
            print("ALL TESTS PASSED!")
            print("✅ "*20 + "\n")
            
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    tester = TestResearchAgent()
    tester.run_all_tests()
