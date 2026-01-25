# System Analysis: Agentic Business Ops Platform

## Overview
This is an AI-powered business consultancy platform for Egyptian startups using a multi-agent architecture built with LangGraph and Perplexity AI.

## Architecture Components

### 1. **API Layer** ([backend/api.py](backend/api.py))
- **FastAPI** web server exposing REST endpoints
- **Key Endpoints:**
  - `POST /api/upload` - Upload business documents (PDF, presentations)
  - `POST /api/question` - Ask questions about uploaded documents
  - `POST /api/plan` - Generate business action plans
  - `GET /api/profile/{startup_id}` - Get startup profile
  - `GET /api/plans/{startup_id}` - Get all plans for a startup

### 2. **Database Layer** ([backend/data/db/storage.py](backend/data/db/storage.py))
- **SQLite database** storing:
  - `profiles` table: Startup business information
  - `plans` table: Generated action plans with tasks/phases
- **Key Functions:**
  - `init_db()` - Initialize database schema
  - `save_profile()`, `get_profile()` - Profile CRUD
  - `save_plan()`, `get_plan()` - Plan CRUD

### 3. **Agent System** (LangGraph Multi-Agent)

#### **Orchestrator** ([backend/agents/orchestrator/orchestrator.py](backend/agents/orchestrator/orchestrator.py))
- **Role:** Master coordinator routing between agents
- **Supervisor LLM:** Makes routing decisions
- **Flow:**
  1. Receives user query
  2. Decides which agent to call (onboarding, researcher, planner, gap_analysis)
  3. Collects results and either routes to next agent or replies to user

#### **Agents:**

1. **Onboarding Agent** ([backend/agents/onboarding/agent.py](backend/agents/onboarding/agent.py))
   - **Purpose:** Extract structured business information from documents
   - **Input:** Raw documents (PDF, text)
   - **Output:** Structured profile (business_name, type, stage, goals, etc.)
   - **LLM:** Perplexity Sonar

2. **Researcher Agent** ([backend/agents/researcher/agent.py](backend/agents/researcher/agent.py))
   - **Purpose:** Answer questions using knowledge base + web research
   - **Components:**
     - **Offline (RAG):** ChromaDB vector database with document embeddings
     - **Online:** Web search via Perplexity
   - **Output:** research_offline and research_online structured packs

3. **Gap Analysis Agent** ([backend/agents/gap_analysis/agent.py](backend/agents/gap_analysis/agent.py))
   - **Purpose:** Compare startup profile against best practices
   - **Output:** Identified gaps and recommendations

4. **Planner Agent** ([backend/agents/Planner/planner.py](backend/agents/Planner/planner.py))
   - **Purpose:** Generate actionable business plans with phases/tasks
   - **Input:** Goal, time horizon, startup context, research results
   - **Output:** Structured plan with schedule_events and strategy_advice

### 4. **State Management** ([backend/agents/state.py](backend/agents/state.py))
- **MasterState TypedDict:** Shared state passed between all agents
- **Key Fields:**
  - `messages` - Conversation history
  - `user_context` - Business profile
  - `next_agent` - Routing decision
  - `action` - "route" or "reply"
  - `final_plan`, `research_offline`, `research_online` - Agent outputs

## Data Flow

### Question Answering Flow:
```
User Question → API → Orchestrator
                        ↓
                    Supervisor decides
                        ↓
                  Researcher Agent
                  (RAG + Web Search)
                        ↓
                 Supervisor synthesizes
                        ↓
                  Final Answer → User
```

### Plan Generation Flow:
```
User Goal + Files → API → Orchestrator
                             ↓
                     Onboarding Agent
                     (if new startup)
                             ↓
                     Researcher Agent
                     (gather insights)
                             ↓
                     Gap Analysis Agent
                     (identify gaps)
                             ↓
                     Planner Agent
                     (generate schedule)
                             ↓
                     Transform to UI format
                             ↓
                     Save to DB → User
```

## Key Dependencies

### Core Libraries:
- **fastapi** - Web API framework
- **langgraph** - Agent orchestration (StateGraph)
- **langchain-openai** - Perplexity API integration
- **chromadb** - Vector database for RAG
- **sentence-transformers** - Text embeddings
- **pypdf** - PDF document processing
- **sqlite3** - Database storage

### API Keys Required:
- `PERPLEXITY_API_KEY` - Main LLM API
- `LANGSMITH_API_KEY` - (Optional) Tracing/debugging

## Common Issues & Solutions

### 1. JSON Parsing Errors
**Problem:** LLM returns text instead of valid JSON
**Solution:** `force_to_json()` helper in orchestrator with multiple fallback strategies

### 2. Routing Loops
**Problem:** Orchestrator gets stuck in infinite routing
**Solution:** `iteration_count` safety counter (max 15 iterations)

### 3. Missing Context
**Problem:** Agents don't have enough information
**Solution:** Check `user_context` is properly populated by onboarding

### 4. Document Processing
**Problem:** Files not being ingested
**Solution:** Verify file paths in `onboarding_files` and `processed_files`

### 5. Database Errors
**Problem:** Profile/plan save failures
**Solution:** Check DB initialization and schema with `init_db()`

## Testing Strategy

### Level 1: Imports & Environment
- Verify all packages are installed
- Check API keys are set
- Confirm file structure exists

### Level 2: Database
- Test `init_db()` creates schema
- Test save/retrieve operations
- Verify SQLite file exists

### Level 3: LLM Connectivity
- Test basic Perplexity API calls
- Verify JSON response handling
- Check timeout/retry logic

### Level 4: Individual Agents
- Test onboarding with sample documents
- Test researcher with queries
- Test planner with goals
- Verify each agent's output format

### Level 5: Orchestrator
- Test supervisor routing logic
- Verify state transitions
- Check `force_to_json()` fallbacks
- Test iteration_count safety

### Level 6: API Endpoints
- Test `/upload` with files
- Test `/question` with queries
- Test `/plan` generation
- Test `/profile` retrieval

### Level 7: Integration
- End-to-end document upload → plan
- Full question answering flow
- Multi-agent collaboration

## How to Debug

### 1. Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Check LangSmith Traces
- Set `LANGSMITH_API_KEY` in `.env`
- View traces at https://smith.langchain.com

### 3. Run Diagnostic Tests
```bash
# Run all diagnostic tests
pytest backend/tests/test_diagnostics.py -v -s

# Run specific level
pytest backend/tests/test_diagnostics.py::TestLevel3_LLMConnectivity -v -s
```

### 4. Test Individual Components
```python
# Test database directly
from backend.data.db.storage import init_db, save_profile
init_db()
save_profile({"startup_id": "test", "business_name": "Test"})

# Test agent directly
from backend.agents.onboarding.agent import run_onboarding
result = run_onboarding(state)
```

### 5. Check State at Each Step
```python
# In orchestrator, add logging:
for step in master_app.stream(initial_state):
    print(f"Step: {list(step.keys())[0]}")
    print(f"State: {step}")
```

## Next Steps

1. **Run Diagnostic Tests** to identify specific failures
2. **Check Logs** for error messages
3. **Verify Database** operations work
4. **Test Agents** individually before testing orchestrator
5. **Fix Issues** based on test results
6. **Run Integration Tests** after unit tests pass

## File Reference Map

| Component | File Path |
|-----------|-----------|
| API Server | [backend/api.py](backend/api.py) |
| Database | [backend/data/db/storage.py](backend/data/db/storage.py) |
| Orchestrator | [backend/agents/orchestrator/orchestrator.py](backend/agents/orchestrator/orchestrator.py) |
| State | [backend/agents/state.py](backend/agents/state.py) |
| Onboarding | [backend/agents/onboarding/agent.py](backend/agents/onboarding/agent.py) |
| Researcher | [backend/agents/researcher/agent.py](backend/agents/researcher/agent.py) |
| Planner | [backend/agents/Planner/planner.py](backend/agents/Planner/planner.py) |
| Gap Analysis | [backend/agents/gap_analysis/agent.py](backend/agents/gap_analysis/agent.py) |
| Tests | [backend/tests/](backend/tests/) |
