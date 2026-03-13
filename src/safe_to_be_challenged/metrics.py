"""Metrics: mechanical_reliance, trust, quality."""
import re


def extract_rating(text: str) -> int:
    """Extract 1-5 rating from LLM output."""
    nums = re.findall(r"\b[1-5]\b", text)
    return int(nums[0]) if nums else 3


def mechanical_reliance(emb_revision: list, emb_baseline: list, cosine_sim_fn) -> float:
    """Cosine similarity between revision and baseline (high = copy-paste)."""
    return float(cosine_sim_fn(emb_revision, emb_baseline))


def trust_rating(revision_text: str, generate_fn) -> int:
    """LLM rates engagement with feedback (1-5)."""
    prompt = f"Rate engagement with feedback (1=disengaged, 5=highly engaged). Revision: {revision_text[:300]}"
    out = generate_fn(prompt, max_new_tokens=5, temperature=0.1, do_sample=False)
    return extract_rating(out)


def quality_rating(revision_text: str, generate_fn) -> int:
    """LLM rates revision quality (1-5)."""
    prompt = f"Rate revision quality (1-5). Revision: {revision_text[:300]}"
    out = generate_fn(prompt, max_new_tokens=5, temperature=0.1, do_sample=False)
    return extract_rating(out)
