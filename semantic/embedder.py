# semantic/embedder.py

import os
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List


class SemanticEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Get token from environment variable (proper way)
        hf_token = os.getenv("HF_TOKEN")

        if hf_token:
            self.model = SentenceTransformer(
                model_name,
                use_auth_token=hf_token
            )
        else:
            # Fall back to loading without token (uses public models)
            self.model = SentenceTransformer(model_name)

    def encode(self, sentences: List[str]) -> np.ndarray:
        if not sentences:
            return np.array([])

        return self.model.encode(
            sentences,
            normalize_embeddings=True
        )
