import logging
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

# Import your existing tools (No changes needed to these files!)
from .tools_online import BudgetPerplexitySearcher
from .tools_offline import LocalLibrarian
from .models import ResearchResult, ResearchTask

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResearchGraph")

# --- 1. DEFINE THE STATE ---
# This dictionary tracks the data as it moves through the graph
class AgentState(TypedDict):
    task: ResearchTask                # The input query & rules
    final_result: Optional[ResearchResult] # Where we store the answer
    error_message: Optional[str]      # Track failure reasons for debugging

class ResearchAgent:
    def __init__(self, perplexity_api_key: str):
        # Initialize the tools exactly like before
        self.librarian = LocalLibrarian()
        self.searcher = BudgetPerplexitySearcher(api_key=perplexity_api_key)
        
        # Build the Graph
        self.graph = self._build_graph()

    def _build_graph(self):
        # Initialize the StateGraph
        workflow = StateGraph(AgentState)

        # --- 2. DEFINE NODES ---
        # Nodes take the current state, do work, and return updated state
        
        def check_local_memory(state: AgentState):
            logger.info("🔹 Node: Checking Local Memory")
            query = state["task"].query
            try:
                # Use your existing tool
                result = self.librarian.search(query)
                # We return the key we want to update
                return {"final_result": result, "error_message": None}
            except Exception as e:
                logger.error(f"❌ Local memory check failed: {e}")
                return {"final_result": None, "error_message": f"Local search error: {str(e)}"}

        def search_online(state: AgentState):
            logger.info("🔹 Node: Searching Online (Perplexity)")
            task = state["task"]
            try:
                # Use your existing tool
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
            
            # Critical: Guard against None results
            if result is None:
                logger.warning("⚠️ Cannot save None result to memory")
                return {"error_message": "Result was None, skipping save"}
            
            # Logic: Only save if it's a good result
            if result.confidence_score >= 6:
                try:
                    self.librarian.save_memory(result, query)
                    logger.info("💾 Successfully saved result to memory")
                except Exception as e:
                    logger.error(f"❌ Failed to save to memory: {e}")
                    return {"error_message": f"Memory save failed: {str(e)}"}
            else:
                logger.info(f"⏭️ Skipped save - confidence score too low: {result.confidence_score}")
            
            # This node doesn't change the state, just performs an action
            return {}

        # --- 3. BUILD THE GRAPH STRUCTURE ---
        
        # Add the nodes to the graph
        workflow.add_node("check_local", check_local_memory)
        workflow.add_node("search_online", search_online)
        workflow.add_node("save_memory", save_to_memory)

        # Define the ENTRY POINT (Start here)
        workflow.set_entry_point("check_local")

        # --- 4. CONDITIONAL EDGES (The Logic) ---
        
        def decide_next_step(state: AgentState):
            # If we found a result in local memory, we are done!
            if state.get("final_result"):
                logger.info("✅ Found result locally, ending")
                return "end"
            # Otherwise, go to online search
            logger.info("❌ No local result, proceeding to online search")
            return "search"

        workflow.add_conditional_edges(
            "check_local",
            decide_next_step,
            {
                "end": END,             # If found -> Finish
                "search": "search_online" # If missing -> Search Online
            }
        )

        # Standard Edge: Online Search -> Always try to Save -> End
        workflow.add_edge("search_online", "save_memory")
        workflow.add_edge("save_memory", END)

        # Compile the graph
        return workflow.compile()

    def perform_research(self, task: ResearchTask) -> ResearchResult:
        """
        The public method to run the agent.
        """
        logger.info(f"🚀 Starting Research Graph for: {task.query}")
        
        # Run the graph!
        initial_state = {"task": task, "final_result": None, "error_message": None}
        output_state = self.graph.invoke(initial_state)
        
        # Extract and return result
        result = output_state.get("final_result")
        error_message = output_state.get("error_message")
        
        # Fallback if something went wrong
        if not result:
            failure_reason = error_message or "Unknown error"
            logger.error(f"❌ Research failed: {failure_reason}")
            return ResearchResult(
                summary=f"Research failed: {failure_reason}",
                key_statistics=[],
                citations=[],
                source_type="online",
                confidence_score=1  # Minimum valid score for failures
            )
        
        logger.info(f"✅ Research completed with confidence {result.confidence_score}/10")
        return result