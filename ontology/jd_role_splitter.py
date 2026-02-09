# ontology/jd_role_splitter.py

from typing import Dict, List


# --------------------------------------------------
# ROLE DEFINITIONS (CAN GROW LATER)
# --------------------------------------------------
ROLE_KEYWORDS = {
    "python_backend": {
        "python", "api", "apis", "database", "sql",
        "backend", "flask", "django", "crud", "server"
    },

    "ml_engineer": {
        "machine learning", "ml", "dataset", "data",
        "preprocess", "train", "evaluate", "model",
        "numpy", "pandas", "scikit", "prediction"
    }
}


def split_jd_by_role(jd_requirements: List[str]) -> Dict[str, List[str]]:
    """
    Split JD requirements into role-specific buckets.
    """
    role_buckets = {role: [] for role in ROLE_KEYWORDS}

    for sentence in jd_requirements:
        s = sentence.lower()

        matched = False
        for role, keywords in ROLE_KEYWORDS.items():
            if any(k in s for k in keywords):
                role_buckets[role].append(sentence)
                matched = True

        # Optional: keep unclassified sentences if needed later
        if not matched:
            pass  # ignored intentionally

    # Remove empty roles
    return {role: reqs for role, reqs in role_buckets.items() if reqs}
