# backend/agents/planner/graph.py

import os
import datetime
import operator
import json
from typing import Annotated, TypedDict, List, Union

# AI Frameworks
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

# Tools & Config
from dotenv import load_dotenv
from backend.tools.calculator import check_calendar_availability
from backend.agents.Planner.prompts import planner_prompt_template  # <--- UPDATED IMPORT

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
    model="gemini-2.0-flash-lite", # Using the stable version
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1,
    transport="rest"
)

# Bind Tools
tools = [check_calendar_availability]
llm_with_tools = llm.bind_tools(tools)

# --- BLOCK 2: STATE DEFINITION ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_context: dict
    final_plan: dict 

# --- BLOCK 3: THE NODE LOGIC ---
def planning_node(state: AgentState):
    # 1. Unpack State
    user_msg = state['messages'][-1].content
    context = state.get('user_context', {})
    current_date = datetime.date.today()

    # 2. Prepare Variables for the Template
    # We extract data here so LangSmith can log the exact inputs
    prompt_variables = {
        "business_name": context.get("business_name", "The Business"),
        "current_date": str(current_date),
        "user_context_str": str(context),
        "user_msg": user_msg
    }

    # 3. Create the Chain
    # (Template -> LLM with Tools)
    # This automatically tracks the "Prompt Generation" step in LangSmith
    chain = planner_prompt_template | llm_with_tools

    # 4. Execute
    with mlflow.start_run():
        # We pass the dictionary of variables to the chain
        response = chain.invoke(prompt_variables)

    # 5. Handle Tool Calls vs. Final Output
    
    # CASE A: The Agent wants to use a tool (Calendar)
    if response.tool_calls:
        return {"messages": [response]}
    
    # CASE B: The Agent is done and is returning the JSON plan
    else:
        parsed_plan = {}
        try:
            # Clean raw content (strip Markdown formatting)
            raw_content = response.content
            if isinstance(raw_content, list):
                 raw_content = "".join([b["text"] for b in raw_content if "text" in b])
            
            clean_content = str(raw_content).replace("```json", "").replace("```", "").strip()
            
            # Parse
            parsed_plan = json.loads(clean_content)
            
            # Validate keys exist
            if "chat_summary" not in parsed_plan:
                parsed_plan["chat_summary"] = "Plan generated."

        except Exception as e:
            # Fallback if parsing fails
            parsed_plan = {
                "strategy_advice": str(response.content),
                "schedule_events": [],
                "chat_summary": "I created a plan but there was a formatting error."
            }
        
        # Return final_plan to the Orchestrator
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