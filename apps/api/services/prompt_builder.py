"""
Prompt builder - constructs prompts for grounded generation
"""
from typing import List, Dict, Any

SYSTEM_PROMPT = """You are Basirah, a knowledge assistant grounded exclusively in the Quran, Sahih al-Bukhari, Sahih Muslim, and Tafsir Ibn Kathir.

**Rules you must always follow:**
1. Answer ONLY from the retrieved evidence passages provided below
2. Do NOT use any knowledge from your training data
3. Do NOT invent references or quote text not present in the evidence
4. Cite EVERY factual claim to a specific passage using its canonical reference [Reference]
5. If the evidence is weak, incomplete, or does not directly address the question, state this explicitly
6. NEVER answer without visible references
7. Distinguish between direct textual support and synthesis across multiple passages
8. When citing Tafsir, clearly indicate it is commentary/interpretation, not direct revelation

**Citation format:**
- Use square brackets with the canonical reference: [Quran 2:255], [Bukhari 1], [Muslim 45], [Tafsir 2:255]
- Place citations immediately after the relevant statement
- Multiple citations for one statement: [Quran 2:255][Tafsir 2:255]
- For Tafsir: Use format [Tafsir SURAH:VERSE] to show which Quranic verse is being explained
"""

def build_prompt(question: str, evidence: List[Dict[str, Any]]) -> str:
    """
    Build a grounded generation prompt

    Args:
        question: User question
        evidence: List of retrieved passages with references

    Returns:
        Complete prompt for LLM
    """
    if not evidence:
        return f"""Question: {question}

No relevant evidence was found in the corpus. Please inform the user that you cannot answer this question based on the available sources."""

    # Build evidence section
    evidence_text = "\n\n".join([
        f"[{i+1}] Reference: {e['reference']}\n{e['text']}"
        for i, e in enumerate(evidence)
    ])

    prompt = f"""{SYSTEM_PROMPT}

**Retrieved Evidence:**

{evidence_text}

**Question:** {question}

**Instructions:**
- Base your answer STRICTLY on the evidence above
- Cite using the canonical references (e.g., [Quran 2:255], not [1])
- If evidence is insufficient, say so clearly
- Do not add information not present in the evidence

**Answer:**"""

    return prompt

def extract_citations(answer: str) -> List[str]:
    """
    Extract citation references from generated answer

    Args:
        answer: Generated answer text

    Returns:
        List of cited references
    """
    import re
    # Match patterns like [Quran 2:255], [Bukhari 1], [Muslim 42]
    pattern = r'\[(Quran|Bukhari|Muslim)\s+[\d:]+\]'
    citations = re.findall(pattern, answer)
    return [c.strip('[]') for c in citations]
