import os
import datetime
import operator
import json
import re
from typing import Annotated, TypedDict, List, Union

# AI Frameworks
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage

# Tools & Config
from dotenv import load_dotenv
from backend.tools.calculator import check_calendar_availability  # Ensure this path is correct
from backend.agents.Planner.prompts import get_planner_prompt     # <--- NEW UNIFIED PROMPT IMPORT

# MLOps
import mlflow
import mlflow.langchain

# --- BLOCK 1: SETUP ---
load_dotenv()

# Setup MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns"))
mlflow.set_experiment("Business_Planning_Agent")
mlflow.langchain.autolog()

# Setup LLM - Using Perplexity Sonar Reasoning Pro for complex planning
llm = ChatOpenAI(
    model="sonar-reasoning-pro",  # Best for complex multi-step planning with chain-of-thought
    temperature=0.1,
    base_url="https://api.perplexity.ai",
    api_key=os.getenv("PERPLEXITY_API_KEY") or os.getenv("PPLX_API_KEY"),
    timeout=180,  # Longer timeout for reasoning
    max_retries=3,
)

# Bind Tools
tools = [check_calendar_availability]
llm_with_tools = llm.bind_tools(tools)

# --- BLOCK 2: STATE DEFINITION ---
class AgentState(TypedDict):
    # Shared conversation history
    messages: Annotated[List[BaseMessage], operator.add]
    # Context injected by Orchestrator
    user_context: dict
    # Research results from Research Agent (passed through MasterState)
    research_offline: dict
    research_online: dict
    # The final result bubble-up
    final_plan: dict 

# --- BLOCK 3: THE NODE LOGIC ---
def planning_node(state: AgentState):
    # 1. Unpack State
    user_msg = state['messages'][-1].content
    context = state.get('user_context', {})
    current_date = datetime.date.today()
    
    # Include research findings if available (passed from orchestrator)
    research_context = ""
    if state.get('research_offline') or state.get('research_online'):
        research_context = "\n\n### RESEARCH FINDINGS (Use these in your plan):\n"
        
        if state.get('research_offline') and isinstance(state['research_offline'], dict):
            offline = state['research_offline']
            if offline.get('summary'):
                research_context += f"\n**Internal Knowledge Base:**\n{offline.get('summary', 'N/A')}\n"
        
        if state.get('research_online') and isinstance(state['research_online'], dict):
            online = state['research_online']
            if online.get('summary'):
                research_context += f"\n**Live Market Research:**\n{online.get('summary', 'N/A')}\n"
                if online.get('findings'):
                    research_context += "\nKey Findings:\n"
                    for i, finding in enumerate(online.get('findings', [])[:5], 1):
                        if isinstance(finding, dict):
                            research_context += f"  {i}. {finding.get('pattern', finding)}\n"
                        else:
                            research_context += f"  {i}. {finding}\n"

    # 2. Get Unified Prompt (No more if/else for task_type)
    sys_msg_content = get_planner_prompt(current_date, context)

    # 3. Construct System Message
    # We explicitly tell it to use tools or output JSON
    final_sys_msg = f"""{sys_msg_content}
    {research_context}
    
    IMPORTANT: 
    - You have a tool `check_calendar_availability`. 
    - If you are proposing specific dates, YOU MUST CALL THIS TOOL FIRST to check if they are free.
    - If the tool returns 'BUSY', you must find another date.
    - ONLY when you are ready to give the final answer, output the Strict JSON.
    - Your response MUST end with a valid JSON object (the final plan).
    """

    # 4. Execute LLM
    with mlflow.start_run():
        response = llm_with_tools.invoke([
            SystemMessage(content=final_sys_msg),
            *state["messages"]
        ])

    # 5. Handle Tool Calls vs. Final Output
    # CASE A: The Agent wants to use a tool (Calendar)
    if response.tool_calls:
        # We return the message so the graph can route to "tools" node
        return {"messages": [response]}
    
    # CASE B: The Agent is done and is returning the JSON plan
    else:
        parsed_plan = {}
        try:
            # Clean raw content (strip Markdown formatting)
            raw_content = response.content
            if isinstance(raw_content, list):
                 # Handle generic list content if needed
                 raw_content = "".join([b["text"] for b in raw_content if "text" in b])
            
            content_str = str(raw_content)
            
            # For reasoning models, extract JSON from chain-of-thought response
            # Try to find JSON block in markdown first
            json_match = re.search(r'```json\s*(.*?)\s*```', content_str, re.DOTALL)
            if json_match:
                clean_content = json_match.group(1).strip()
            else:
                # Try to find JSON object with expected keys
                json_match = re.search(r'\{[^{}]*"(?:strategy_advice|chat_summary|schedule_events)"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content_str, re.DOTALL)
                if json_match:
                    clean_content = json_match.group(0)
                else:
                    # Last resort: find any JSON-like structure
                    json_match = re.search(r'(\{[\s\S]*\})\s*$', content_str)
                    if json_match:
                        clean_content = json_match.group(1)
                    else:
                        clean_content = content_str.replace("```json", "").replace("```", "").strip()
            
            # Parse
            parsed_plan = json.loads(clean_content)
            
            # Validate keys exist (Optional safety)
            if "chat_summary" not in parsed_plan:
                parsed_plan["chat_summary"] = "Plan generated."

        except Exception as e:
            # Fallback if parsing fails
            parsed_plan = {
                "strategy_advice": str(response.content),
                "schedule_events": [],
                "chat_summary": "I created a plan but there was a formatting error."
            }
        
        # CRITICAL FIX: We return 'final_plan' here.
        # This populates the key in MasterState so the Orchestrator sees it.
        return {
            "messages": [response],
            "final_plan": parsed_plan 
        }

# --- BLOCK 4: GRAPH ---
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("planner", planning_node)
workflow.add_node("tools", ToolNode(tools))

# Edges
workflow.set_entry_point("planner")

workflow.add_conditional_edges(
    "planner",
    tools_condition,
    {
        "tools": "tools",  # If tool_calls exists -> go to tools
        END: END           # If no tool_calls -> finish
    }
)

workflow.add_edge("tools", "planner") # Tools always report back to planner

app_graph = workflow.compile()