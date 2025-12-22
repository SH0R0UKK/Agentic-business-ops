"""
LangSmith tracing helpers for the backend.
Provides optional, non-intrusive tracing capabilities.
"""

import os
import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# Check if LangSmith is configured
LANGSMITH_ENABLED = bool(os.getenv("LANGSMITH_API_KEY"))
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "agentic-business-ops")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

if LANGSMITH_ENABLED:
    try:
        from langsmith import Client, traceable
        from langsmith.run_helpers import get_current_run_tree
        
        # Initialize client
        langsmith_client = Client(
            api_key=os.getenv("LANGSMITH_API_KEY"),
            api_url=LANGSMITH_ENDPOINT
        )
        logger.info(f"✅ LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")
    except ImportError:
        LANGSMITH_ENABLED = False
        logger.warning("⚠️ LangSmith SDK not installed. Tracing disabled.")
        langsmith_client = None
        traceable = None
        get_current_run_tree = None
else:
    logger.info("ℹ️ LangSmith tracing disabled (LANGSMITH_API_KEY not set)")
    langsmith_client = None
    traceable = None
    get_current_run_tree = None


@contextmanager
def trace_run(name: str, metadata: Optional[Dict[str, Any]] = None, run_type: str = "chain"):
    """
    Context manager for tracing a run.
    
    If LangSmith is configured, creates a trace/span with the given name and metadata.
    Otherwise, behaves as a no-op.
    
    Args:
        name: Name of the run/span
        metadata: Optional metadata dictionary
        run_type: Type of run ("chain", "tool", "llm", "retriever", etc.)
    
    Example:
        with trace_run("orchestrator_run", {"startup_id": "123"}):
            result = orchestrate(state)
    """
    if not LANGSMITH_ENABLED or not traceable:
        # No-op if tracing is disabled
        yield None
        return
    
    try:
        # Set up environment for LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = LANGSMITH_ENDPOINT
        
        # Use LangSmith's traceable decorator as context manager
        with langsmith_client.trace(
            name=name,
            run_type=run_type,
            project_name=LANGSMITH_PROJECT,
            metadata=metadata or {}
        ) as run:
            yield run
    except Exception as e:
        logger.warning(f"⚠️ LangSmith tracing error (non-fatal): {e}")
        yield None


def log_event(name: str, data: Optional[Dict[str, Any]] = None):
    """
    Log an event into the current trace.
    
    If LangSmith is configured and there's an active trace, logs the event.
    Otherwise, behaves as a no-op.
    
    Args:
        name: Event name
        data: Optional event data
    
    Example:
        log_event("research_started", {"question": "What is market size?"})
    """
    if not LANGSMITH_ENABLED or not get_current_run_tree:
        return
    
    try:
        current_run = get_current_run_tree()
        if current_run:
            current_run.add_event(
                name=name,
                **( data or {})
            )
    except Exception as e:
        logger.debug(f"Could not log event to LangSmith: {e}")


def trace_agent(agent_name: str):
    """
    Decorator for tracing agent functions.
    
    Automatically wraps agent entry points with tracing.
    
    Args:
        agent_name: Name of the agent (e.g., "onboarding", "researcher", "planner")
    
    Example:
        @trace_agent("onboarding")
        def run_onboarding(request: OnboardingRequest) -> StartupProfile:
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract metadata from arguments if possible
            metadata = {
                "agent": agent_name,
                "function": func.__name__
            }
            
            # Try to extract request object for metadata
            if args and hasattr(args[0], 'model_dump'):
                try:
                    request_data = args[0].model_dump()
                    metadata["startup_id"] = request_data.get("startup_id", "unknown")
                except:
                    pass
            
            with trace_run(f"{agent_name}_agent", metadata=metadata, run_type="chain"):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def trace_function(func_name: Optional[str] = None, run_type: str = "tool"):
    """
    Decorator for tracing individual functions.
    
    Args:
        func_name: Optional custom name for the trace (defaults to function name)
        run_type: Type of run ("tool", "chain", etc.)
    
    Example:
        @trace_function("pdf_ocr")
        def extract_text_from_pdf(pdf_path: str) -> str:
            ...
    """
    def decorator(func):
        name = func_name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            metadata = {
                "function": func.__name__,
                "module": func.__module__
            }
            
            with trace_run(name, metadata=metadata, run_type=run_type):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Utility function to sanitize data for tracing (remove sensitive info)
def sanitize_for_trace(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove sensitive information from data before logging to trace.
    
    Args:
        data: Dictionary to sanitize
    
    Returns:
        Sanitized dictionary
    """
    sensitive_keys = {"api_key", "password", "token", "secret", "auth"}
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_trace(value)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            sanitized[key] = [sanitize_for_trace(item) for item in value]
        else:
            sanitized[key] = value
    
    return sanitized
