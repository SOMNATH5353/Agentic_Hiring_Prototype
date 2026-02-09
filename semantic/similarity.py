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

    # Ensure embeddings are 2D
    if len(jd_embeddings.shape) == 1:
        jd_embeddings = jd_embeddings.reshape(1, -1)
    if len(resume_embeddings.shape) == 1:
        resume_embeddings = resume_embeddings.reshape(1, -1)

    # Compute similarity matrix: shape (num_jd, num_resume)
    similarity_matrix = cosine_similarity(jd_embeddings, resume_embeddings)

    for jd_idx in range(len(jd_sentences)):
        for resume_idx in range(len(resume_sentences)):
            # Safety check for bounds
            if jd_idx >= similarity_matrix.shape[0] or resume_idx >= similarity_matrix.shape[1]:
                continue

            similarity = similarity_matrix[jd_idx, resume_idx]  # Use comma notation for 2D indexing

            if similarity >= threshold:
                matches.append({
                    'jd_text': jd_sentences[jd_idx],
                    'resume_text': resume_sentences[resume_idx],
                    'similarity': float(similarity),
                    'jd_index': jd_idx,
                    'resume_index': resume_idx
                })

    # Sort by similarity descending
    matches.sort(key=lambda x: x['similarity'], reverse=True)

    return matches
