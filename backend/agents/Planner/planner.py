import os
import datetime
import operator
import json
from typing import Annotated, TypedDict, List, Union

# AI Frameworks
from langchain_google_genai import ChatGoogleGenerativeAI
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

# Setup LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", # Or your preferred version
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1,
    transport="rest"

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
    # The final result bubble-up
    final_plan: dict 

# --- BLOCK 3: THE NODE LOGIC ---
def planning_node(state: AgentState):
    # 1. Unpack State
    user_msg = state['messages'][-1].content
    context = state.get('user_context', {})
    current_date = datetime.date.today()

    # 2. Get Unified Prompt (No more if/else for task_type)
    sys_msg_content = get_planner_prompt(current_date, context)

    # 3. Construct System Message
    # We explicitly tell it to use tools or output JSON
    final_sys_msg = f"""{sys_msg_content}
    
    IMPORTANT: 
    - You have a tool `check_calendar_availability`. 
    - If you are proposing specific dates, YOU MUST CALL THIS TOOL FIRST to check if they are free.
    - If the tool returns 'BUSY', you must find another date.
    - ONLY when you are ready to give the final answer, output the Strict JSON.
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
            
            clean_content = str(raw_content).replace("```json", "").replace("```", "").strip()
            
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