# Backend - Agentic Business Ops

AI-powered business consultancy platform for Egyptian startups.

## Architecture Overview

```
backend/
├── agents/              # AI agents (onboarding, researcher, planner, orchestrator)
│   ├── models.py       # Shared input/output contracts
│   ├── state.py        # Orchestrator state definition
│   ├── onboarding/     # Business profiling agent
│   ├── researcher/     # Research agent (offline + online)
│   ├── Planner/        # Strategic planning agent
│   └── orchestrator/   # Multi-agent orchestration
├── data/               # Data storage and artifacts
│   ├── db/            # SQLite databases
│   ├── benchmark_sources/ # Benchmark data sources
│   ├── test_documents/    # Sample documents for testing
│   └── chroma/        # Vector database storage
├── tools/              # Shared utilities
│   ├── tracing.py      # LangSmith tracing helpers
│   ├── calculator.py   # Date/calendar utilities
│   └── pdf_ocr.py      # Document processing (if needed)
├── tests/              # Unified test suite
│   ├── conftest.py     # Test fixtures
│   ├── test_onboarding.py
│   ├── test_researcher.py
│   ├── test_planner.py
│   └── test_orchestrator.py
├── archive/            # Deprecated/experimental code
├── main.py             # FastAPI application
└── requirements.txt    # Python dependencies
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the backend directory:

```env
# Required
PERPLEXITY_API_KEY=your_api_key_here
PPLX_API_KEY=your_api_key_here  # Alternative name

# Optional - LangSmith Tracing
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=agentic-business-ops
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Optional - Server Config
BACKEND_PORT=8000
```

**Note:** The application works without `LANGSMITH_API_KEY` - tracing is optional and non-intrusive.

### 3. Initialize Database

The database is automatically initialized on first run. To manually initialize:

```python
from backend.data.db.storage import init_db
init_db()
```

## Running the Backend

### Development Server

```bash
cd backend
python main.py
```

Or with uvicorn directly:

```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```http
GET /
GET /health
```

### Onboarding
```http
POST /api/onboarding
GET  /api/profile/{startup_id}
```

### Research
```http
POST /api/research
```

### Planning
```http
POST /api/plan
GET  /api/plans/{startup_id}
GET  /api/plan/{plan_id}
```

### Orchestrator (Conversational)
```http
POST /api/chat
```

## Testing

### Run All Tests

```bash
# From project root
pytest backend/tests

# With verbose output
pytest backend/tests -v

# Run specific test file
pytest backend/tests/test_onboarding.py

# Run with coverage
pytest backend/tests --cov=backend --cov-report=html
```

### Test Structure

- `conftest.py` - Shared fixtures and configuration
- `test_onboarding.py` - Onboarding agent tests
- `test_researcher.py` - Research agent tests
- `test_planner.py` - Planner agent tests
- `test_orchestrator.py` - Orchestrator tests

All tests are designed to:
- Work without external API calls when keys are missing
- Test input/output contracts
- Verify model validation
- Check error handling

## Agent Contracts

### Onboarding Agent

**Input:** `OnboardingRequest`
```python
{
    "startup_id": str,
    "founder_inputs": dict,
    "file_paths": list[str]
}
```

**Output:** `StartupProfile`
```python
{
    "startup_id": str,
    "business_name": str,
    "business_type": str,
    "sector": str,
    "location": str,
    "stage": str,
    "goals": list[str],
    "key_constraints": list[str],
    ...
}
```

### Research Agent

**Input:** `ResearchRequest`
```python
{
    "startup_id": str,
    "question": str,
    "startup_profile": StartupProfile (optional),
    "search_offline": bool,
    "search_online": bool
}
```

**Output:** `ResearchResponse`
```python
{
    "startup_id": str,
    "question": str,
    "offline": OfflineEvidencePack,
    "online": OnlineBenchmarkPack,
    "combined_summary": str,
    "confidence_score": int
}
```

### Planner Agent

**Input:** `PlanRequest`
```python
{
    "startup_id": str,
    "startup_profile": StartupProfile,
    "research_offline": OfflineEvidencePack (optional),
    "research_online": OnlineBenchmarkPack (optional),
    "time_horizon_days": int,
    "task_type": "timeline" | "advisory"
}
```

**Output:** `Plan`
```python
{
    "plan_id": str,
    "startup_id": str,
    "title": str,
    "summary": str,
    "phases": list[Phase],
    "strategy_advice": str (optional),
    "schedule_events": list[dict]
}
```

## Tracing with LangSmith

LangSmith tracing is **optional** and **non-intrusive**. The system works perfectly without it.

### Enable Tracing

Set environment variables:
```env
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=your_project_name
```

### Disable Tracing

Simply don't set `LANGSMITH_API_KEY` - all tracing calls become no-ops.

### Usage in Code

```python
from backend.tools.tracing import trace_run, log_event

# Trace a function
with trace_run("my_function", metadata={"user_id": "123"}):
    result = do_work()
    log_event("milestone_reached", {"step": 1})
```

## Data Management

### SQLite Database

Location: `backend/data/db/business_ops.db`

Tables:
- `profiles` - Startup profiles
- `plans` - Strategic plans

### Vector Database

Location: `backend/data/chroma/`

Used for:
- Offline knowledge base search
- Document embeddings
- Semantic search

### Benchmark Sources

Location: `backend/data/benchmark_sources/`

Contains JSON files with curated business intelligence sources.

## Changes from Previous Version

### ✅ Added
- Unified agent models with clear contracts (`agents/models.py`)
- FastAPI REST API with full CRUD endpoints
- SQLite database for profiles and plans
- LangSmith tracing (optional)
- Unified pytest test suite
- Comprehensive error handling

### ❌ Removed
- MLflow integration (replaced with LangSmith)
- DVC data versioning
- Scattered test files
- Duplicate/experimental code (moved to `archive/`)

### 🔧 Refactored
- Clear folder structure (agents, data, tools, tests)
- Explicit input/output models for all agents
- Consistent error handling
- Improved logging

## Development Guidelines

### Adding a New Agent

1. Create subfolder under `backend/agents/`
2. Define input/output models in `agents/models.py`
3. Implement agent logic with clear entry function
4. Add tracing wrappers (optional)
5. Write tests in `backend/tests/test_<agent>.py`
6. Update orchestrator routing if needed

### Adding a New Endpoint

1. Define Pydantic models for request/response
2. Add route in `backend/main.py`
3. Implement handler calling appropriate agent
4. Add database storage if needed
5. Write API tests

### Error Handling

- Use specific exception types
- Return clear error messages
- Log errors with context
- Don't expose internal details to API

## Troubleshooting

### Database Issues

```bash
# Reset database
rm backend/data/db/business_ops.db
python -c "from backend.data.db.storage import init_db; init_db()"
```

### Import Errors

Ensure you're running from project root:
```bash
cd /path/to/Agentic-business-ops
python -m backend.main
```

### API Key Errors

Verify `.env` file is in correct location and loaded:
```python
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("PERPLEXITY_API_KEY"))
```

### Tracing Errors

If LangSmith errors occur:
1. Unset `LANGSMITH_API_KEY` to disable tracing
2. Check API key is valid
3. Verify `langsmith` package is installed

## Contributing

1. Create feature branch
2. Make changes with tests
3. Run full test suite: `pytest backend/tests`
4. Update documentation
5. Submit PR

## License

[Your License Here]
