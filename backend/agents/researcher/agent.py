import logging
import asyncio
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

# Import your existing tools
from .tools_online import BudgetPerplexitySearcher, online_research_with_llm
from .tools_offline import LocalLibrarian, offline_research_with_llm
from .models import (
    ResearchResult, ResearchTask, 
    OfflineEvidencePack, OnlineBenchmarkPack, CombinedResearchResult
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResearchGraph")


# --- 1. DEFINE THE STATE ---
class AgentState(TypedDict):
    task: ResearchTask                         # The input query & rules
    final_result: Optional[ResearchResult]     # Legacy: simple result
    offline_pack: Optional[OfflineEvidencePack]  # New: structured offline
    online_pack: Optional[OnlineBenchmarkPack]   # New: structured online
    error_message: Optional[str]               # Track failure reasons


class ResearchAgent:
    """
    Research Agent that combines offline RAG and online search.
    Provides both legacy simple results and new structured packs for Gap Analysis.
    """
    
    def __init__(self, perplexity_api_key: str = None):
        import os
        self.api_key = perplexity_api_key or os.getenv("PERPLEXITY_API_KEY")
        
        # Initialize the tools
        self.librarian = LocalLibrarian()
        self.searcher = BudgetPerplexitySearcher(api_key=self.api_key)
        
        # Build the Graph (legacy flow)
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build LangGraph workflow for legacy simple research flow."""
        workflow = StateGraph(AgentState)

        def check_local_memory(state: AgentState):
            logger.info("🔹 Node: Checking Local Memory")
            query = state["task"].query
            try:
                result = self.librarian.search(query)
                return {"final_result": result, "error_message": None}
            except Exception as e:
                logger.error(f"❌ Local memory check failed: {e}")
                return {"final_result": None, "error_message": f"Local search error: {str(e)}"}

        def search_online(state: AgentState):
            logger.info("🔹 Node: Searching Online (Perplexity)")
            task = state["task"]
            try:
                result = self.searcher.search(task.query, task.grounding_rules)
                if result is None:
                    error_msg = "Online search returned None (possible API failure)"
                    logger.warning(f"⚠️ {error_msg}")
                    return {"final_result": None, "error_message": error_msg}
                return {"final_result": result, "error_message": None}
            except Exception as e:
                logger.error(f"❌ Online search failed: {e}")
                return {"final_result": None, "error_message": f"Online search error: {str(e)}"}

        def save_to_memory(state: AgentState):
            logger.info("🔹 Node: Saving to Memory")
            result = state["final_result"]
            query = state["task"].query
            
            if result is None:
                logger.warning("⚠️ Cannot save None result to memory")
                return {"error_message": "Result was None, skipping save"}
            
            if result.confidence_score >= 6:
                try:
                    self.librarian.save_memory(result, query)
                    logger.info("💾 Successfully saved result to memory")
                except Exception as e:
                    logger.error(f"❌ Failed to save to memory: {e}")
                    return {"error_message": f"Memory save failed: {str(e)}"}
            else:
                logger.info(f"⏭️ Skipped save - confidence score too low: {result.confidence_score}")
            
            return {}

        # Add nodes
        workflow.add_node("check_local", check_local_memory)
        workflow.add_node("search_online", search_online)
        workflow.add_node("save_memory", save_to_memory)

        workflow.set_entry_point("check_local")

        def decide_next_step(state: AgentState):
            if state.get("final_result"):
                logger.info("✅ Found result locally, ending")
                return "end"
            logger.info("❌ No local result, proceeding to online search")
            return "search"

        workflow.add_conditional_edges(
            "check_local",
            decide_next_step,
            {
                "end": END,
                "search": "search_online"
            }
        )

        workflow.add_edge("search_online", "save_memory")
        workflow.add_edge("save_memory", END)

        return workflow.compile()

    def perform_research(self, task: ResearchTask) -> ResearchResult:
        """
        Legacy method: Run simple research graph.
        Returns a single ResearchResult.
        """
        logger.info(f"🚀 Starting Research Graph for: {task.query}")
        
        initial_state = {
            "task": task, 
            "final_result": None, 
            "offline_pack": None,
            "online_pack": None,
            "error_message": None
        }
        output_state = self.graph.invoke(initial_state)
        
        result = output_state.get("final_result")
        error_message = output_state.get("error_message")
        
        if not result:
            failure_reason = error_message or "Unknown error"
            logger.error(f"❌ Research failed: {failure_reason}")
            return ResearchResult(
                summary=f"Research failed: {failure_reason}",
                key_statistics=[],
                citations=[],
                source_type="online",
                confidence_score=1
            )
        
        logger.info(f"✅ Research completed with confidence {result.confidence_score}/10")
        return result

    async def perform_combined_research(
        self, 
        question: str,
        startup_context: dict = None,
        profile_context: dict = None
    ) -> CombinedResearchResult:
        """
        New method: Run both offline and online research with LLM reasoning.
        Returns structured packs for Gap Analysis Agent.
        
        Args:
            question: Research question
            startup_context: Optional startup profile for offline search
            profile_context: Optional profile context for online search
        
        Returns:
            CombinedResearchResult with both offline and online packs
        """
        logger.info(f"🚀 Starting Combined Research for: {question}")
        
        # Run both research paths concurrently
        offline_task = offline_research_with_llm(question, startup_context)
        online_task = online_research_with_llm(question, profile_context)
        
        offline_pack, online_pack = await asyncio.gather(
            offline_task, 
            online_task,
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(offline_pack, Exception):
            logger.error(f"Offline research failed: {offline_pack}")
            offline_pack = OfflineEvidencePack(
                question=question,
                summary=f"Error: {str(offline_pack)}",
                claims=[],
                contradictions=[],
                missing_info=[],
                status="error"
            )
        
        if isinstance(online_pack, Exception):
            logger.error(f"Online research failed: {online_pack}")
            online_pack = OnlineBenchmarkPack(
                question=question,
                summary=f"Error: {str(online_pack)}",
                findings=[],
                assumptions=[],
                prohibited_uses=[],
                status="error"
            )
        
        logger.info("✅ Combined research completed")
        
        return CombinedResearchResult(
            offline=offline_pack,
            online=online_pack
        )

    def perform_combined_research_sync(
        self, 
        question: str,
        startup_context: dict = None,
        profile_context: dict = None
    ) -> CombinedResearchResult:
        """
        Synchronous wrapper for perform_combined_research.
        Use this when you can't use async/await.
        """
        return asyncio.run(
            self.perform_combined_research(question, startup_context, profile_context)
        )


# --- ORCHESTRATOR ENTRY POINT ---
async def run_research_agent(state: dict) -> dict:
    """
    Entry point for the orchestrator to call the Research Agent.
    
    Inputs:
        state: Current orchestrator state with:
            - 'messages' (or 'user_question' or 'search_query'): The question to research
            - 'user_context' (optional): Startup profile context
    
    Returns:
        Dict with:
            - 'research_offline': OfflineEvidencePack as dict
            - 'research_online': OnlineBenchmarkPack as dict
    """
    logger.info("🔬 Research Agent invoked by orchestrator")
    
    # Extract question from state
    question = None
    
    # Try different possible field names
    if 'search_query' in state and state['search_query']:
        question = state['search_query']
    elif 'user_question' in state:
        question = state['user_question']
    elif 'messages' in state and state['messages']:
        # Get last user message
        last_msg = state['messages'][-1]
        question = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    
    if not question:
        logger.error("No question found in state")
        return {
            "research_offline": {
                "question": "N/A",
                "summary": "No question provided to research agent",
                "claims": [],
                "contradictions": [],
                "missing_info": [],
                "status": "error"
            },
            "research_online": {
                "question": "N/A",
                "summary": "No question provided to research agent",
                "findings": [],
                "assumptions": [],
                "prohibited_uses": [],
                "status": "error"
            }
        }
    
    # Extract context
    startup_context = state.get('user_context', {})
    profile_context = state.get('user_context', {})
    
    logger.info(f"Researching: {question[:100]}...")
    
    # Create agent and run research
    agent = ResearchAgent()
    result = await agent.perform_combined_research(
        question=question,
        startup_context=startup_context,
        profile_context=profile_context
    )
    
    # Convert Pydantic models to dicts
    return {
        "research_offline": result.offline.model_dump() if result.offline else None,
        "research_online": result.online.model_dump() if result.online else None
    }