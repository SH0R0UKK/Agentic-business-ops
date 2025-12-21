import os
import datetime
import operator
from typing import Annotated, TypedDict, List, Union
import json

# AI Frameworks
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

# Add these new imports
from langgraph.prebuilt import ToolNode, tools_condition
from backend.tools.calculator import check_calendar_availability
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# MLOps
import mlflow

# 1. Load Environment Variables
load_dotenv() # This reads your .env file

# 2. Setup MLflow (The Monitoring)
# This creates the 'mlruns' folder in your root directory automatically
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns"))
mlflow.set_experiment("Business_Planning_Agent")

# 3. Setup Gemini LLM (The Brain)
# We use temperature=0.1 to make the JSON output consistent/strict
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1
)

# 4. Bind Tools (CRITICAL STEP YOU MISSED)
tools = [check_calendar_availability]
llm_with_tools = llm.bind_tools(tools)


# --- BLOCK 2: SCHEMAS & STATE ---

# 1. Output Schema (The "Contract" with V0 Dashboard)
# We use Pydantic to enforce strict JSON formatting
class PlanOutput(BaseModel):
    response_type: str = Field(
        description="Must be 'timeline' (for schedules) or 'advisory' (for text advice)"
    )
    chat_summary: str = Field(
        description="A friendly 1-2 sentence summary to show in the chat window."
    )
    dashboard_data: dict = Field(
        description="The payload. Contains 'events' list (if timeline) OR 'content' string (if advisory)"
    )

# 2. Agent State (The "Memory" passing through the graph)
class AgentState(TypedDict):

    # 'messages': Stores the conversation history (User query, etc.)
    messages: Annotated[List[BaseMessage], operator.add] 
    # 'user_context': Stores business data (e.g., {"business_type": "Clothing", "stock": 500})
    user_context: dict
    # 'task_type': The decision made by the Orchestrator ("timeline" vs "advisory")
    task_type: str
    # 'final_plan': The result we send back to FastAPI
    final_plan: dict

    # --- BLOCK 3: THE NODE LOGIC ---
def planning_node(state: AgentState):
    # 1. Unpack State
    user_msg = state['messages'][-1].content
    context = state.get('user_context', {})
    task_type = state.get("task_type", "advisory") 
    current_date = datetime.date.today()

    # 2. Select Prompt (Fixed Logic)
    # PROMPT A: For Scheduling (Strict JSON Dates)
    # PROMPT A: For Scheduling (Strategic & Aware of Availability)
    PROMPT_TIMELINE = f"""
    ### ROLE
    You are an elite Business Operations Strategist and Master Project Scheduler.
    Your goal is to convert high-level business objectives into concrete, actionable, and date-specific execution plans for SMEs.

    ### CONTEXT
    - **Current Date:** {current_date}
    - **Objective:** You will receive a business goal (e.g., "Clear 500 units of stock", "Schedule team training", "Conduct quarterly audit").
    - **Constraint:** Act strictly within the provided business context and calendar availability.

    ### STRATEGIC LOGIC (STEP 1: PLAN BEFORE YOU CHECK)
    Before checking specific dates, apply these best practices:

    1. **Smart Spacing:** Avoid stacking major tasks back-to-back unless urgent. Leave 1-2 days gap for preparation/recovery between dependent tasks.
    2. **Task Type Awareness:** 
    - **External-facing tasks** (marketing campaigns, launches, client meetings) → Best on Thurs/Fri/Weekend.
    - **Internal tasks** (HR, operations, audits, training) → Best on Tue/Wed.
    - Avoid scheduling routine tasks on Mondays unless specified.
    3. **Recovery Strategy:** 
    - If an "Ideal Date" is BUSY, HOLIDAY, or WEEKEND:
        - Do NOT just pick the next day blindly.
        - Move to the *next strategic slot* appropriate for the task type.
    - Always respect explicit user requests (see below).

    ### USER-SPECIFIC DATE HANDLING
    If the user explicitly asks to "Change task X to Date Y":
    1. Check Date Y using `check_calendar_availability`.
    2. If BUSY/HOLIDAY/WEEKEND:
    - Do NOT auto-move it.
    - Schedule on Date Y as requested.
    - **Warning:** Include in 'chat_summary': 
        "⚠️ Note: You requested [Date], which is a [Reason]. Are you sure you want to proceed?"
    3. If AVAILABLE:
    - Schedule normally and confirm in 'chat_summary'.

    ### EXECUTION LOOP (STEP 2: VERIFY)
    1. **Identify:** Mentally pick ideal dates for each task based on task type, spacing, and dependencies.
    2. **Check:** Use `check_calendar_availability` to verify ONLY those specific dates.
    3. **Finalize:** Lock dates that are available; apply Recovery Strategy for BUSY dates (unless user explicitly requested).

    ### RESPONSE FORMAT (STRICT JSON)
    Output a single JSON object. No Markdown.

    {{
    "response_type": "timeline",
    "chat_summary": "A friendly summary explaining the reasoning and strategy applied (e.g., 'I scheduled the training on Tuesday to maximize internal team availability').",
    "dashboard_data": {{
        "events": [
        {{
            "date": "YYYY-MM-DD",
            "task": "Short Title (Max 5 words)",
            "details": "Specific instruction starting with a verb"
        }}
        ]
    }}
    }}

    ### GUIDELINES (DOs)
    1. Logical Sequencing: Ensure tasks follow a dependency chain (Preparation → Task → Review/Follow-up).
    2. Date Math: Start planning from {current_date}. Never schedule in the past.
    3. Specificity: Be precise. Avoid vague instructions like "Do research." Example: "Analyze supplier pricing for Q4."

    ### GUIDELINES (DON'Ts)
    1. No Overbooking: Never schedule on a date the tool reports as BUSY, HOLIDAY, or WEEKEND unless user explicitly requests.
    2. No Hallucinations: Do not invent metrics or events not provided in context.
    3. No Fluff: Keep instructions actionable and concise.

    ### EXAMPLE INPUT/OUTPUT
    **Input:** "Prepare quarterly HR report and schedule team training."
    **Strategy:** "Need to collect data first, then train the team on optimal internal days."
    **Output Logic:**
    - Day 1 (Mon): Draft report template
    - Day 2 (Tue): Collect employee data
    - Day 4 (Thu): Conduct team training session (internal-friendly day)
    """


    PROMPT_ADVISORY = f"""
    You are a Strategic Business Advisor.
    GOAL: Provide expert advice.
    OUTPUT: Strict JSON with 'dashboard_data' containing 'content' (markdown).
    """

    if task_type == "timeline":
        sys_msg_content = PROMPT_TIMELINE
    else:
        sys_msg_content = PROMPT_ADVISORY

    # 3. Construct Final System Message
    final_sys_msg = f"""{sys_msg_content}
    
    USER CONTEXT: {context}
    
    IMPORTANT: You have a tool called 'check_calendar_availability'.
    - If you are scheduling dates, you MUST call this tool first.
    - If the tool says 'BUSY', pick another date.
    - When you are finished and have a final plan, output ONLY the JSON matching the PlanOutput schema.
    """

    # 4. EXECUTION (Unified MLOps & Tool Call)
    with mlflow.start_run():
        mlflow.log_param("task_type", task_type)
        mlflow.log_text(final_sys_msg, "system_prompt.txt")

        # We use llm_with_tools so the agent can DECIDE to call a tool or answer
        response = llm_with_tools.invoke([
            SystemMessage(content=final_sys_msg), 
            *state["messages"] 
        ])
        
        # Log the output
        mlflow.log_text(str(response.content), "agent_response_raw.txt")
    
    # 5. Handle The Result
    # If it's a Tool Call, LangGraph handles it via the Edge.
    # If it's a Final Answer (JSON text), we try to parse it to 'final_plan'
    
    # 5. Handle The Result
    parsed_plan = {}
    
    # Only try to parse if the agent is NOT calling a tool (i.e., it's done)
    if not response.tool_calls:
        try:
            # A. Extract text (Handle both String and Gemini 2.0 List format)
            raw_content = response.content
            if isinstance(raw_content, list):
                # Join all text blocks: [{'text': '...'}, {'text': '...'}] -> "..."
                text_content = "".join([block["text"] for block in raw_content if "text" in block])
            else:
                text_content = str(raw_content)

            # B. Clean and Parse JSON
            clean_content = text_content.replace("```json", "").replace("```", "").strip()
            parsed_plan = json.loads(clean_content)
            
        except Exception as e:
            # Fallback if parsing fails
            parsed_plan = {
                "error": "Failed to parse JSON plan", 
                "details": str(e),
                "raw_output": str(response.content)
            }

    # 6. Return Update
    # We append the new response to messages, and update final_plan
    return {
        "messages": state["messages"] + [response], 
        "final_plan": parsed_plan
    }

# --- BLOCK 4: THE AGENTIC GRAPH ---

workflow = StateGraph(AgentState)

# 1. Add Nodes
workflow.add_node("planner", planning_node)
workflow.add_node("tools", ToolNode(tools)) 

# 2. Add Edges
workflow.set_entry_point("planner")

# 3. Conditional Logic
workflow.add_conditional_edges(
    "planner",
    tools_condition, 
    {
        "tools": "tools", # If tool called -> Go to tools
        END: END          # If text returned -> Finish
    }
)

workflow.add_edge("tools", "planner") # Loop back after tool

app_graph = workflow.compile()