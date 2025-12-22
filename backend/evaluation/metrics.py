import re
from typing import List, Dict
from collections import Counter

def calculate_hallucination_rate(gaps: List[Dict], research_summary: Dict) -> Dict:
    """
    Hallucination = gap makes claims NOT supported by research_summary.
    
    Method:
    1. Extract all facts from research_summary
    2. For each gap, check if reasoning cites research facts
    3. Hallucination rate = unsupported_gaps / total_gaps
    """
    # Flatten research into searchable text
    research_text = ""
    research_text += " ".join(research_summary.get("market_trends", []))
    research_text += " ".join(research_summary.get("best_practices", []))
    
    for comp in research_summary.get("competitor_analysis", []):
        research_text += " " + comp.get("competitor", "")
        research_text += " ".join(comp.get("strengths", []))
    
    research_text = research_text.lower()
    
    unsupported_count = 0
    supported_count = 0
    
    for gap in gaps:
        reasoning = gap.get("reasoning", "").lower()
        description = gap.get("description", "").lower()
        combined = reasoning + " " + description
        
        # Extract claim keywords (nouns, numbers)
        claim_words = set(re.findall(r'\b\w{4,}\b', combined))
        research_words = set(re.findall(r'\b\w{4,}\b', research_text))
        
        # Check overlap
        overlap = claim_words & research_words
        overlap_ratio = len(overlap) / len(claim_words) if claim_words else 0
        
        if overlap_ratio < 0.5:  # Less than 30% word overlap = hallucination
            unsupported_count += 1
        else:
            supported_count += 1
    
    total = unsupported_count + supported_count
    hallucination_rate = unsupported_count / total if total > 0 else 0
    
    return {
        "hallucination_rate": hallucination_rate,
        "unsupported_gaps": unsupported_count,
        "supported_gaps": supported_count,
        "score": hallucination_rate  
    }

def calculate_factual_grounding(gaps: List[Dict], research_summary: Dict) -> Dict:
    """
    Stricter than hallucination: checks if gaps cite SPECIFIC research items.
    
    Method:
    1. Check if gap sources field references research items
    2. Verify claims match cited sources
    """
    grounded_count = 0
    
    for gap in gaps:
        sources = gap.get("sources", [])
        reasoning = gap.get("reasoning", "").lower()
        
        # Check if sources are meaningful (not just generic)
        has_specific_citation = any(
            "market_trends" in s or 
            "competitor" in s or 
            "benchmark" in s or
            "best_practice" in s
            for s in sources
        )
        
        # Check if reasoning mentions research concepts
        mentions_research = any(keyword in reasoning for keyword in [
            "research", "study", "competitor", "benchmark", "trend", "practice"
        ])
        
        if has_specific_citation or mentions_research:
            grounded_count += 1
    
    total = len(gaps)
    grounding_rate = grounded_count / total if total > 0 else 0
    
    return {
        "grounding_rate": grounding_rate,
        "grounded_gaps": grounded_count,
        "total_gaps": total,
        "score": grounding_rate
    }

def calculate_relevance_score(gaps: List[Dict], user_goal: str) -> Dict:
    """
    Measures if gaps actually help achieve user_goal.
    
    Method:
    1. Extract keywords from user_goal
    2. Check if gaps mention goal keywords or mark related_to_goal
    """
    goal_keywords = set(re.findall(r'\b\w{4,}\b', user_goal.lower()))
    
    relevant_count = 0
    
    for gap in gaps:
        # Explicit marking
        if gap.get("related_to_goal"):
            relevant_count += 1
            continue
        
        # Implicit check: gap description mentions goal keywords
        gap_text = gap.get("description", "").lower()
        gap_words = set(re.findall(r'\b\w{4,}\b', gap_text))
        
        overlap = goal_keywords & gap_words
        if len(overlap) >= 1:  # At least one keyword match
            relevant_count += 1
    
    total = len(gaps)
    relevance = relevant_count / total if total > 0 else 0
    
    return {
        "relevance_score": relevance,
        "relevant_gaps": relevant_count,
        "total_gaps": total,
        "score": relevance
    }

def calculate_coverage(gaps: List[Dict], research_summary: Dict, expected_gap_categories: List[str]) -> Dict:
    """
    Did the LLM identify obvious gaps mentioned in research?
    
    Expected categories for pre-seed: compliance, automation, marketing, tech debt
    """
    found_categories = set(gap.get("category", "") for gap in gaps)
    expected_set = set(expected_gap_categories)
    
    coverage = len(found_categories & expected_set) / len(expected_set) if expected_set else 1.0
    
    return {
        "coverage_score": coverage,
        "found_categories": list(found_categories),
        "expected_categories": expected_gap_categories,
        "missing_categories": list(expected_set - found_categories),
        "score": coverage
    }

def calculate_severity_calibration(gaps: List[Dict]) -> Dict:
    """
    Checks if severity distribution is reasonable.
    
    Good calibration: Mix of critical/high/medium, not all one level.
    """
    severities = [g.get("severity", "medium") for g in gaps]
    severity_counts = Counter(severities)
    
    # Ideal: some critical, mostly high/medium, few low
    total = len(gaps)
    if total == 0:
        return {"calibration_score": 0, "distribution": {}}
    
    critical_ratio = severity_counts.get("critical", 0) / total
    high_ratio = severity_counts.get("high", 0) / total
    medium_ratio = severity_counts.get("medium", 0) / total
    
    # Penalize if ALL gaps are same severity
    diversity_score = len(severity_counts) / 4  # Max 4 levels
    
    # Penalize if >70% are critical (over-alarming) or >70% are low (under-alarming)
    balance_score = 1.0
    if critical_ratio > 0.7 or severity_counts.get("low", 0) / total > 0.7:
        balance_score = 0.5
    
    calibration = (diversity_score + balance_score) / 2
    
    return {
        "calibration_score": calibration,
        "distribution": dict(severity_counts),
        "score": calibration
    }

def evaluate_gap_quality(
    gaps_output: Dict,
    input_data: Dict,
    expected_gap_categories: List[str] = None
) -> Dict:
    """
    Comprehensive evaluation combining all metrics.
    
    Args:
        gaps_output: {internal_gaps: [...], market_gaps: [...]}
        input_data: {startup_profile, research_summary, user_goal}
        expected_gap_categories: List of categories we expect to see
    
    Returns:
        Dict with all metric scores
    """
    all_gaps = gaps_output.get("internal_gaps", []) + gaps_output.get("market_gaps", [])
    research = input_data.get("research_summary", {})
    goal = input_data.get("user_goal", "")
    
    if expected_gap_categories is None:
        # Default expectations
        sector = input_data.get("startup_profile", {}).get("sector", "")
        if sector == "fintech":
            expected_gap_categories = ["process", "technical", "resource"]
        elif sector == "tourism":
            expected_gap_categories = ["process", "resource", "channels"]
        else:
            expected_gap_categories = []
    
    metrics = {
        "hallucination": calculate_hallucination_rate(all_gaps, research),
        "grounding": calculate_factual_grounding(all_gaps, research),
        "relevance": calculate_relevance_score(all_gaps, goal),
        "coverage": calculate_coverage(all_gaps, research, expected_gap_categories),
        "severity_calibration": calculate_severity_calibration(all_gaps)
    }
    
    # Overall score (weighted average)
    overall = (
        metrics["hallucination"]["score"] * 0.3 +
        metrics["grounding"]["score"] * 0.25 +
        metrics["relevance"]["score"] * 0.25 +
        metrics["coverage"]["score"] * 0.1 +
        metrics["severity_calibration"]["score"] * 0.1
    )
    
    return {
        **metrics,
        "overall_score": overall,
        "total_gaps": len(all_gaps)
    }
