from typing import List, Dict

def filter_and_cap_gaps(
    internal_gaps: List[Dict],
    market_gaps: List[Dict],
    min_confidence: float = 0.5,
    max_total: int = 10
) -> tuple[list[Dict], list[Dict]]:
    # Filter by confidence
    i = [g for g in internal_gaps if g.get("confidence", 0) >= min_confidence]
    m = [g for g in market_gaps if g.get("confidence", 0) >= min_confidence]

    # Sort by severity priority then confidence
    sev_rank = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    i.sort(key=lambda g: (sev_rank.get(g.get("severity", "low"), 0), g.get("confidence", 0)), reverse=True)
    m.sort(key=lambda g: (sev_rank.get(g.get("severity", "low"), 0), g.get("confidence", 0)), reverse=True)

    # Cap total count while preserving ratio
    total = len(i) + len(m)
    if total > max_total:
        # proportional cap
        i_take = max(1, int(max_total * (len(i) / total))) if total else 0
        m_take = max_total - i_take
        i = i[:i_take]
        m = m[:m_take]
    return i, m
