"""
Confidence scoring - estimate answer quality based on retrieval and citations
"""
from typing import List, Dict, Any
import re

def calculate_confidence(
    answer: str,
    evidence: List[Dict[str, Any]],
    retrieval_scores: List[float]
) -> float:
    """
    Calculate confidence score for generated answer

    Factors:
    1. Retrieval quality (average score of top passages)
    2. Citation coverage (% of evidence cited)
    3. Answer length (penalize very short answers)

    Args:
        answer: Generated answer
        evidence: Retrieved evidence passages
        retrieval_scores: Scores from retrieval

    Returns:
        Confidence score between 0 and 1
    """
    if not evidence or not answer:
        return 0.0

    # Factor 1: Retrieval quality (30%)
    avg_retrieval_score = sum(retrieval_scores[:5]) / min(5, len(retrieval_scores))
    retrieval_confidence = min(avg_retrieval_score, 1.0) * 0.3

    # Factor 2: Citation coverage (50%)
    # Extract cited references from answer
    cited_pattern = r'\[(Quran|Bukhari|Muslim)\s+[\d:]+\]'
    cited_refs = set(re.findall(cited_pattern, answer))

    # Get available references from evidence
    available_refs = set([e['reference'] for e in evidence[:10]])

    if available_refs:
        citation_coverage = len(cited_refs) / len(available_refs)
    else:
        citation_coverage = 0.0

    citation_confidence = min(citation_coverage, 1.0) * 0.5

    # Factor 3: Answer quality heuristics (20%)
    answer_length = len(answer.split())
    length_score = min(answer_length / 100, 1.0)  # Prefer 100+ words

    # Penalize if no citations found
    has_citations = len(cited_refs) > 0
    citation_penalty = 0.5 if not has_citations else 1.0

    answer_quality = length_score * citation_penalty * 0.2

    # Combine factors
    total_confidence = retrieval_confidence + citation_confidence + answer_quality

    return round(min(total_confidence, 1.0), 3)
