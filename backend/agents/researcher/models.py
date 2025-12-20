from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ResearchResult(BaseModel):
    """
    Standardized output format for the Research Agent.
    This is what other agents (like the Orchestrator) will receive.
    """
    summary: str = Field(..., description="A concise answer to the query.")
    key_statistics: List[str] = Field(default_factory=list, description="List of specific data points found.")
    citations: List[str] = Field(default_factory=list, description="URLs or filenames of sources.")
    source_type: Literal["local", "online"] = Field(..., description="Where this data came from.")
    confidence_score: int = Field(..., ge=1, le=10, description="1-10 rating of answer quality.")
    
    def to_markdown(self) -> str:
        """Helper to format the result for human reading or LLM context."""
        stats = "\n".join([f"- {s}" for s in self.key_statistics])
        sources = "\n".join([f"- {s}" for s in self.citations])
        return (
            f"**Summary:** {self.summary}\n\n"
            f"**Key Stats:**\n{stats}\n\n"
            f"**Sources ({self.source_type}):**\n{sources}"
        )

class ResearchTask(BaseModel):
    """
    Input schema for the Research Agent.
    """
    query: str
    grounding_rules: List[str] = Field(
        default=["Prioritize recent data (post-2023)", "Cite official sources"],
        description="Rules the agent must follow."
    )