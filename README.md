# Gap Analysis Agent - Technical Documentation

Create `backend/agents/README_GAP_ANALYSIS.md`:

```markdown
# Gap Analysis Agent - Technical Documentation

## Overview

The Gap Analysis Agent is a specialized worker in the supervisor-worker architecture that identifies internal and market gaps for startups. It receives curated research from the orchestrator, analyzes business weaknesses, and produces prioritized, evidence-backed gap reports.

---

## Architecture Position

```
User → Orchestrator → Profiling → Orchestrator
                           ↓
              Research Agent (Online + Offline)
                           ↓
              Orchestrator (curates prompt)
                           ↓
         ╔═══════════════════════════════╗
         ║   GAP ANALYSIS AGENT         ║  ← YOU ARE HERE
         ║   (Worker - No Direct Chat)  ║
         ╚═══════════════════════════════╝
                           ↓
              Orchestrator → Planning → User
```

**Design Principle**: This is a **worker agent** - it never chats with users, only processes data and returns structured JSON.

---

## Logical Flow

### Phase 1: Input Reception (State Extraction)

```
┌─────────────────────────────────────────────────────────┐
│ INPUT: LangGraph State Dictionary                      │
├─────────────────────────────────────────────────────────┤
│ Required Keys:                                          │
│  -  startup_profile: {company_name, sector, stage, ...}  │
│  -  research_summary: {market_trends, competitors, ...}  │
│  -  user_goal: "Launch campaign in 3 months"            │
└─────────────────────────────────────────────────────────┘
                           ↓
         [Validate presence of required keys]
                           ↓
         [Extract and prepare for LLM prompt]
```

**Code Reference**: `gap_analysis_node()` lines 51-53

---

### Phase 2: LLM Analysis (ReAct Loop)

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Build Prompt                                   │
├─────────────────────────────────────────────────────────┤
│ System Prompt:                                          │
│  "You are a startup business analyst..."               │
│  + JSON schema requirements                             │
│                                                          │
│ User Prompt:                                            │
│  {startup_profile} + {research_summary} + {user_goal}  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Call LLM (Provider-Agnostic)                   │
├─────────────────────────────────────────────────────────┤
│ Tools/llm.py routes to:                                │
│  -  Gemini: google.generativeai                          │
│  -  OpenAI: openai.chat.completions                      │
│  -  Sonar: perplexity.ai API                            │
│  -  Mock: Deterministic test data                        │
│                                                          │
│ Request: response_format={"type": "json"}              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Parse Response                                  │
├─────────────────────────────────────────────────────────┤
│ Expected JSON:                                          │
│ {                                                       │
│   "internal_gaps": [                                    │
│     {                                                   │
│       "gap_id": "",                                     │
│       "category": "process|technical|resource|team",    │
│       "description": "What's missing",                  │
│       "severity": "critical|high|medium|low",           │
│       "confidence": 0.0-1.0,                            │
│       "reasoning": "Why this is a gap",                 │
│       "related_to_goal": true|false,                    │
│       "sources": ["market_trends", ...]             │
│     }                                                   │
│   ],                                                    │
│   "market_gaps": [                                      │
│     {                                                   │
│       ... same fields as internal_gaps ...              │
│       "competitive_threat": "Competitor X has Y"        │
│     }                                                   │
│   ]                                                     │
│ }                                                       │
│                                                          │
│ Fallback: If parse fails, extract JSON from text       │
└─────────────────────────────────────────────────────────┘
```

**Code Reference**: `gap_analysis_node()` lines 55-74

---

### Phase 3: Post-Processing Pipeline

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Ensure Gap IDs                                  │
├─────────────────────────────────────────────────────────┤
│ Function: _ensure_ids(gaps, prefix)                     │
│                                                          │
│ For each gap missing gap_id:                            │
│   gap_id = f"{prefix}-{uuid4().hex[:8]}"                │
│   Example: "INT-a3f9c012", "MKT-7b2e4f8a"               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Attach Citations                                │
├─────────────────────────────────────────────────────────┤
│ Function: _attach_basic_citations(gaps)                 │
│                                                          │
│ For each gap missing sources:                           │
│   gap["sources"] = ["research_summary"]                 │
│                                                          │
│ Purpose: Ensure every gap is traceable                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Mark Critical Goal-Blockers                     │
├─────────────────────────────────────────────────────────┤
│ Function: _mark_critical_when_goal_blocked(gaps)        │
│                                                          │
│ For each gap where:                                     │
│   related_to_goal == True AND severity != "critical"    │
│ Then:                                                   │
│   gap["severity"] = "critical"                          │
│                                                          │
│ Rationale: Gaps blocking user goals are critical        │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Filter by Confidence (Business Rule)            │
├─────────────────────────────────────────────────────────┤
│ Function: filter_and_cap_gaps()                         │
│ From: tools/validators.py                               │
│                                                          │
│ Rule 1: Min Confidence Threshold                        │
│   Remove gaps where confidence < 0.5                    │
│   Env: GAP_MIN_CONFIDENCE (default: 0.5)               │
│                                                          │
│ Rationale: Low-confidence gaps waste planning time      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: Sort by Priority                                │
├─────────────────────────────────────────────────────────┤
│ Sort Order:                                             │
│  1. Severity (critical > high > medium > low)           │
│  2. Confidence (0.95 > 0.80 > 0.60)                     │
│                                                          │
│ Implementation:                                         │
│   sev_rank = {"critical": 3, "high": 2, ...}            │
│   gaps.sort(key=lambda g: (sev_rank[severity],          │
│                             g["confidence"]),            │
│              reverse=True)                               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 6: Cap Total Gaps (Business Rule)                  │
├─────────────────────────────────────────────────────────┤
│ Rule: Max 10 total gaps (configurable)                 │
│   Env: GAP_MAX_TOTAL (default: 10)                     │
│                                                          │
│ Strategy: Proportional Capping                          │
│   If 8 internal + 6 market = 14 total:                  │
│     Keep 6 internal (8/14 * 10 ≈ 6)                     │
│     Keep 4 market (6/14 * 10 ≈ 4)                       │
│                                                          │
│ Rationale: Prevents cognitive overload in planning      │
└─────────────────────────────────────────────────────────┘
```

**Code Reference**: `gap_analysis_node()` lines 76-85

---

### Phase 4: State Update & Return

```
┌─────────────────────────────────────────────────────────┐
│ OUTPUT: Updated State Dictionary                       │
├─────────────────────────────────────────────────────────┤
│ state["internal_gaps"] = [...]  # List of gap dicts    │
│ state["market_gaps"] = [...]                            │
│ state["gap_analysis_metadata"] = {                      │
│   "total_gaps_identified": int,                         │
│   "critical_gaps_count": int,                           │
│   "analysis_timestamp": ISO8601                         │
│ }                                                        │
│                                                          │
│ Return: state (modified in-place for LangGraph)        │
└─────────────────────────────────────────────────────────┘
                           ↓
         [LangGraph routes to next node: Planning Agent]
```

**Code Reference**: `gap_analysis_node()` lines 88-95

---

## Input Schema

### Required State Keys

```
{
  "startup_profile": {
    "company_name": str,           # Required
    "sector": str,                 # Required: "tourism" | "fintech" | "saas" | ...
    "stage": str,                  # Required: "pre-seed" | "seed" | "series-a"
    "team_size": int,              # Required
    "current_capabilities": list,  # Required: ["feature1", "feature2"]
    "has_mvp": bool,               # Required
    "monthly_revenue": float       # Required: 0 if no revenue
  },
  
  "research_summary": {
    "market_trends": list,         # Required: ["trend1", "trend2"]
    "competitor_analysis": [       # Required
      {
        "competitor": str,
        "strengths": list
      }
    ],
    "best_practices": list,        # Required
    "industry_benchmarks": dict    # Optional: {"metric": value}
  },
  
  "user_goal": str                 # Required: "Achieve X in Y timeframe"
}
```

### Validation Rules

| Field | Validation | Failure Behavior |
|-------|------------|------------------|
| startup_profile | Must exist | Raises `ValueError` |
| research_summary | Must exist | Raises `ValueError` |
| user_goal | Must be non-empty string | Defaults to "" (degrades quality) |
| sector | No validation | Defaults to "general" in mock |

**Code Reference**: `_extract_input()` (not shown in provided code, but should exist)

---

## Output Schema

### State Updates

```
state["internal_gaps"]: List[Dict] = [
  {
    "gap_id": "INT-a3f9c012",               # Auto-generated UUID prefix
    "category": "process",                  # Enum: process|technical|resource|team
    "description": "No CI/CD pipeline",     # Human-readable gap description
    "severity": "critical",                 # Enum: critical|high|medium|low
    "confidence": 0.85,                     # Float [0.0, 1.0]
    "reasoning": "Research shows...",       # Evidence from research_summary
    "related_to_goal": true,                # Bool: Blocks user_goal?
    "sources": ["market_trends"]        # Traceability to research items[1]
  }
]

state["market_gaps"]: List[Dict] = [
  {
    # ... same fields as internal_gaps ...
    "competitive_threat": "Competitor X has feature Y"  # Additional field
  }
]

state["gap_analysis_metadata"]: Dict = {
  "total_gaps_identified": 6,              # Sum of internal + market
  "critical_gaps_count": 2,                # Count of severity="critical"
  "analysis_timestamp": "2025-12-22T07:33:00.000Z"  # UTC ISO8601
}
```

### Gap Categories

| Category | Description | Typical Issues |
|----------|-------------|----------------|
| **process** | Operational/workflow gaps | Missing CI/CD, no documentation, manual processes |
| **technical** | Technical debt/infrastructure | Legacy code, no monitoring, poor architecture |
| **resource** | Budget/people/tools | Insufficient marketing spend, understaffed |
| **team** | Skills/knowledge gaps | No ML expertise, missing CTO |

### Severity Levels

| Severity | Meaning | Planning Priority |
|----------|---------|-------------------|
| **critical** | Blocks user goal OR existential risk | Immediate action (Week 1) |
| **high** | Major competitive disadvantage | Short-term (Month 1) |
| **medium** | Moderate impact on growth | Mid-term (Quarter 1) |
| **low** | Nice-to-have improvement | Backlog |

---

## Evaluation Metrics

### 1. Hallucination Rate

**Definition**: Percentage of gaps making claims NOT supported by research_summary.

**Calculation**:
```
for each gap:
    overlap_ratio = len(gap_keywords ∩ research_keywords) / len(gap_keywords)
    if overlap_ratio < 0.5:
        unsupported_count += 1

hallucination_rate = unsupported_count / total_gaps
```

**Interpretation**:
- **0.0 - 0.1**: Excellent (≤10% hallucination)
- **0.1 - 0.3**: Acceptable (10-30% hallucination)
- **> 0.3**: Poor (agent inventing information)

**Why It Matters**: Hallucinated gaps waste resources on non-existent problems.

---

### 2. Factual Grounding

**Definition**: Percentage of gaps with explicit citations to research sources.

**Calculation**:
```
for each gap:
    if "competitor" in gap["reasoning"] OR
       len(gap["sources"]) > 0:
        grounded_count += 1

grounding_rate = grounded_count / total_gaps
```

**Interpretation**:
- **> 0.8**: Excellent (evidence-backed)
- **0.5 - 0.8**: Acceptable
- **< 0.5**: Poor (unsupported claims)

**Why It Matters**: Ensures recommendations are defensible to stakeholders.

---

### 3. Relevance Score

**Definition**: Percentage of gaps directly related to user's stated goal.

**Calculation**:
```
goal_keywords = extract_keywords(user_goal)

for each gap:
    if gap["related_to_goal"] OR
       any(keyword in gap["description"] for keyword in goal_keywords):
        relevant_count += 1

relevance = relevant_count / total_gaps
```

**Interpretation**:
- **> 0.7**: Focused analysis
- **0.4 - 0.7**: Some drift
- **< 0.4**: Off-topic

**Why It Matters**: Prevents scope creep and keeps planning focused.

---

### 4. Coverage

**Definition**: Did the agent identify expected gap categories for the sector?

**Example**:
- Fintech pre-seed: Expect `["process", "technical"]` (compliance, automation)
- Tourism seed: Expect `["resource", "channels"]` (marketing, distribution)

**Calculation**:
```
found = set(gap["category"] for gap in gaps)
expected = {"process", "technical"}  # Based on sector

coverage = len(found ∩ expected) / len(expected)
```

**Interpretation**:
- **1.0**: All expected categories found
- **0.5 - 1.0**: Partial coverage
- **< 0.5**: Blind spots

**Why It Matters**: Catches systematic omissions.

---

### 5. Severity Calibration

**Definition**: Is the severity distribution reasonable (not all critical, not all low)?

**Calculation**:
```
severity_counts = Counter(gap["severity"] for gap in gaps)
diversity_score = len(severity_counts) / 4  # Max 4 levels

# Penalize if >70% are same severity
if any(count/total > 0.7 for count in severity_counts.values()):
    calibration = diversity_score * 0.5
else:
    calibration = diversity_score
```

**Interpretation**:
- **> 0.7**: Well-calibrated
- **0.4 - 0.7**: Acceptable variance
- **< 0.4**: Over/under-alarming

**Why It Matters**: Helps planning agent prioritize realistically.

---

### Overall Quality Score

```
overall = (
    (1 - hallucination_rate) * 0.30 +  # Factual accuracy (30%)
    grounding_rate * 0.25 +             # Evidence strength (25%)
    relevance * 0.25 +                  # Goal alignment (25%)
    coverage * 0.10 +                   # Completeness (10%)
    calibration * 0.10                  # Priority balance (10%)
)
```

**Benchmark Scores**:
- **0.80 - 1.00**: Production-ready
- **0.60 - 0.80**: Acceptable for MVP
- **< 0.60**: Needs tuning

---

## LLM Provider Comparison

### Running Experiments

```
cd backend
python experiments/compare_llms.py
```

### Recent Benchmark Results (Dec 2025)

| Provider | Tourism Overall | Fintech Overall | Strength | Weakness |
|----------|----------------|----------------|----------|----------|
| **Sonar** | 0.775 | 0.808 | High grounding (1.0), literal | Lower creativity |
| **Gemini** | 0.787 | 0.792 | Perfect relevance (1.0), goal-focused | Paraphrases research |
| **Mock** | N/A | N/A | Deterministic, fast | Hardcoded logic |

**Recommendation**:
- **Production**: Gemini (balanced performance, cost-effective)
- **Compliance-heavy**: Sonar (more literal citations)
- **Testing**: Mock (zero latency, no API costs)

---

## Configuration

### Environment Variables

```
# LLM Selection
LLM_PROVIDER=gemini              # Options: gemini | openai | sonar | mock

# API Keys
GOOGLE_API_KEY=your_key          # For gemini
OPENAI_API_KEY=your_key          # For openai
PERPLEXITY_API_KEY=your_key      # For sonar

# Model Selection
GEMINI_MODEL=gemini-2.5-flash
OPENAI_MODEL=gpt-4o-mini
SONAR_MODEL=sonar-pro

# Business Rules
GAP_MIN_CONFIDENCE=0.5           # Filter gaps below this threshold
GAP_MAX_TOTAL=10                 # Maximum gaps to return

# Tracing (LangSmith)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=Agentic_business_ops
```

---

## Usage Examples

### 1. Standalone Execution

```
from agents.gap_analysis import gap_analysis_node

state = {
    "startup_profile": {
        "company_name": "PayFlow",
        "sector": "fintech",
        "stage": "pre-seed",
        "team_size": 3,
        "current_capabilities": ["payment API"],
        "has_mvp": True,
        "monthly_revenue": 0
    },
    "research_summary": {
        "market_trends": ["SOC2 compliance expected for B2B"],
        "competitor_analysis": [
            {"competitor": "Stripe", "strengths": ["SOC2 certified"]}
        ],
        "best_practices": ["Automate KYC/AML"],
        "industry_benchmarks": {}
    },
    "user_goal": "Onboard 10 pilot customers in 2 months"
}

result = gap_analysis_node(state)

print(f"Found {len(result['internal_gaps'])} internal gaps")
print(f"Found {len(result['market_gaps'])} market gaps")
```

### 2. LangGraph Integration

```
from langgraph.graph import StateGraph
from agents.gap_analysis import gap_analysis_node

graph = StateGraph(State)
graph.add_node("gap_analysis", gap_analysis_node)
graph.add_edge("research_merge", "gap_analysis")  # After research
graph.add_edge("gap_analysis", "planning")        # Before planning

app = graph.compile()
```

### 3. Testing with Mock Provider

```
import os
os.environ["LLM_PROVIDER"] = "mock"

# Runs instantly, no API calls
result = gap_analysis_node(tourism_test_case)
```

---

## Performance Characteristics

### Latency

| Provider | Avg Response Time | P95 Response Time |
|----------|-------------------|-------------------|
| Mock | 5ms | 10ms |
| Gemini | 1.2s | 2.5s |
| OpenAI | 1.8s | 3.2s |
| Sonar | 2.1s | 4.0s |

### Token Usage (Typical)

| Input Type | Prompt Tokens | Completion Tokens | Total |
|------------|---------------|-------------------|-------|
| Tourism (simple) | ~800 | ~400 | ~1,200 |
| Fintech (complex) | ~1,200 | ~600 | ~1,800 |

**Cost Estimate** (Gemini 1.5 Flash):
- Input: $0.000125/1K tokens
- Output: $0.000375/1K tokens
- **~$0.0003 per analysis**

---

## Error Handling

### Common Failures

| Error | Cause | Mitigation |
|-------|-------|------------|
| `ValueError: Missing state key` | Orchestrator didn't pass required data | Validate state in orchestrator |
| `JSONDecodeError` | LLM returned malformed JSON | Fallback parser extracts `{...}` from text |
| `APIError: 429 Rate Limit` | Too many requests | Implement exponential backoff |
| `Empty gaps list` | Min confidence too high | Lower `GAP_MIN_CONFIDENCE` |

### Graceful Degradation

```
try:
    parsed = json.loads(llm_response)
except JSONDecodeError:
    # Fallback: Extract JSON from markdown code blocks
    start = llm_response.find("{")
    end = llm_response.rfind("}")
    parsed = json.loads(llm_response[start:end+1])
```

---

## Monitoring & Observability

### LangSmith Tracing

Every execution is traced with:
- **Input**: Full state snapshot
- **LLM call**: Prompt, tokens, latency
- **Output**: Gaps generated
- **Metadata**: Provider, model, timestamp

**View traces**: https://smith.langchain.com/projects/Agentic_business_ops

### Key Metrics to Monitor

1. **Execution time**: Alert if > 5s
2. **Hallucination rate**: Alert if > 30%
3. **Empty results**: Alert if > 5% of runs
4. **API errors**: Alert on any 5xx errors

---

## Future Improvements

### Roadmap

1. **Real Confidence Scoring** (Q1 2026)
   - Replace LLM self-assessment with calculated overlap metrics
   - Implementation: `validators.calculate_basic_confidence()`

2. **Multi-Agent Debate** (Q2 2026)
   - Run 2-3 LLMs in parallel
   - Synthesize consensus gaps
   - Trade-off: 3x latency for higher quality

3. **Historical Gap Tracking** (Q2 2026)
   - Store gaps in DB
   - Track which gaps were addressed
   - Avoid repeating resolved issues

4. **Domain-Specific Prompts** (Q3 2026)
   - Fintech: Emphasize compliance
   - Healthcare: HIPAA requirements
   - E-commerce: Supply chain

---

## Testing

### Unit Tests

```
pytest tests/test_gap_analysis.py -v
```

### Integration Tests

```
python -m pytest tests/ -k "gap" --cov=agents.gap_analysis
```

### Benchmark Suite

```
python experiments/compare_llms.py
```

---

## Troubleshooting

### "No gaps returned"

**Symptom**: `internal_gaps` and `market_gaps` are empty.

**Diagnosis**:
1. Check `GAP_MIN_CONFIDENCE` - might be too high
2. Verify LLM returned valid JSON
3. Check LangSmith trace for LLM output

**Fix**:
```
export GAP_MIN_CONFIDENCE=0.3  # Lower threshold
```

### "All gaps marked critical"

**Symptom**: Every gap has `severity="critical"`.

**Diagnosis**: `_mark_critical_when_goal_blocked()` over-triggering.

**Fix**: Review user_goal phrasing - avoid keywords in all gaps.

### "Hallucination rate = 100%"

**Symptom**: Evaluation shows all gaps unsupported.

**Diagnosis**: Research summary too sparse OR threshold too strict.

**Fix**: Ensure research_summary has 3+ trends and 2+ competitors.

---

## References

- **Code**: `backend/agents/gap_analysis.py`
- **Validation**: `backend/tools/validators.py`
- **Metrics**: `backend/evaluation/metrics.py`
- **Experiments**: `backend/experiments/compare_llms.py`
- **Tests**: `backend/tests/test_gap_analysis.py`

---

## Contact & Support

For questions or issues:
1. Check LangSmith traces first
2. Review error logs in `backend/logs/`
3. Open GitHub issue with trace ID

**Last Updated**: December 22, 2025
```



[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/92311839/20cc5d1b-ebe6-4d33-b4e8-9d54f73335ea/image.jpg)
