from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# === Original Models (unchanged) ===

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


# === New Models for LLM-Enhanced Research ===

class Claim(BaseModel):
    """A factual claim extracted from RAG context."""
    value: str = Field(..., description="The factual claim")
    source_chunk_id: str = Field(default="unknown", description="Chunk ID from context")
    url: str = Field(default="", description="Source URL")
    doc_type: str = Field(default="unknown", description="Document type")


class Contradiction(BaseModel):
    """A contradiction found between sources."""
    claim_a: str = Field(..., description="First conflicting claim")
    claim_b: str = Field(..., description="Second conflicting claim")
    source_a: str = Field(default="", description="Source of first claim")
    source_b: str = Field(default="", description="Source of second claim")


class OfflineEvidencePack(BaseModel):
    """Structured output from offline RAG with LLM reasoning."""
    question: str = Field(..., description="Original research question")
    summary: str = Field(..., description="Concise answer based on RAG")
    claims: List[Claim] = Field(default_factory=list, description="Factual claims with sources")
    contradictions: List[Contradiction] = Field(default_factory=list, description="Conflicting info found")
    missing_info: List[str] = Field(default_factory=list, description="Questions about missing data")
    status: Literal["success", "error", "no_results"] = Field(default="success")
    
    def to_markdown(self) -> str:
        claims_md = "\n".join([f"- {c.value} (source: {c.url})" for c in self.claims])
        missing_md = "\n".join([f"- {m}" for m in self.missing_info])
        return (
            f"**Summary:** {self.summary}\n\n"
            f"**Claims:**\n{claims_md}\n\n"
            f"**Missing Info:**\n{missing_md}"
        )


class BenchmarkSource(BaseModel):
    """A source from online benchmark findings."""
    url: str = Field(default="", description="Source URL")
    title: str = Field(default="", description="Source title")


class BenchmarkFinding(BaseModel):
    """A benchmark finding from online research."""
    pattern: str = Field(..., description="Observed trend or finding")
    scope: Literal["egypt", "mena", "global"] = Field(default="global", description="Geographic scope")
    sources: List[BenchmarkSource] = Field(default_factory=list, description="Sources for this finding")
    approx_date_range: str = Field(default="unknown", description="Approximate date range")


class OnlineBenchmarkPack(BaseModel):
    """Structured output from online research with LLM reasoning."""
    question: str = Field(..., description="Original research question")
    summary: str = Field(..., description="Concise answer based on web sources")
    findings: List[BenchmarkFinding] = Field(default_factory=list, description="Benchmark findings")
    freshness_days: Optional[int] = Field(default=None, description="Age of most recent source")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made")
    prohibited_uses: List[str] = Field(default_factory=list, description="Disclaimers")
    status: Literal["success", "error", "no_results"] = Field(default="success")
    
    def to_markdown(self) -> str:
        findings_md = "\n".join([f"- {f.pattern} ({f.scope})" for f in self.findings])
        disclaimers = "\n".join([f"- ⚠️ {p}" for p in self.prohibited_uses])
        return (
            f"**Summary:** {self.summary}\n\n"
            f"**Findings:**\n{findings_md}\n\n"
            f"**Disclaimers:**\n{disclaimers}"
        )


class CombinedResearchResult(BaseModel):
    """Combined offline and online research results for Gap Analysis."""
    offline: Optional[OfflineEvidencePack] = None
    online: Optional[OnlineBenchmarkPack] = None
    
    def to_markdown(self) -> str:
        parts = []
        if self.offline:
            parts.append("## Offline Research (RAG)\n" + self.offline.to_markdown())
        if self.online:
            parts.append("## Online Research (Web)\n" + self.online.to_markdown())
        return "\n\n---\n\n".join(parts)