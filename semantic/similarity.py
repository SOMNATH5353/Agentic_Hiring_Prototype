# semantic/similarity.py

from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import numpy as np


def compute_semantic_matches(
    jd_sentences: List[str],
    jd_embeddings: np.ndarray,
    resume_sentences: List[str],
    resume_embeddings: np.ndarray,
    threshold: float = 0.65
) -> List[Dict]:
    """
    Matches resume evidence to JD expectations semantically.

    Returns explainable match records.
    """

    matches = []

    if len(jd_embeddings) == 0 or len(resume_embeddings) == 0:
        return matches

    similarity_matrix = cosine_similarity(resume_embeddings, jd_embeddings)

    for r_idx, resume_sentence in enumerate(resume_sentences):
        for j_idx, jd_sentence in enumerate(jd_sentences):

            score = similarity_matrix[r_idx][j_idx]

            if score >= threshold:
                matches.append({
                    "resume_point": resume_sentence,
                    "jd_point": jd_sentence,
                    "similarity": round(float(score), 3)
                })

    return matches
