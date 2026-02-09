# ontology/jd_requirements.py

from typing import List

# Keywords that indicate evaluative JD content
ACTION_KEYWORDS = [
    "write", "build", "develop", "design", "implement", "work",
    "debug", "test", "deploy", "learn", "assist", "create",
    "train", "evaluate", "optimize", "collect", "preprocess"
]

SKILL_KEYWORDS = [
    "python", "api", "apis", "database", "sql",
    "flask", "django", "oop", "git", "testing",
    "machine learning", "ml", "pandas", "numpy",
    "scikit", "statistics", "data"
]

NEGATIVE_PATTERNS = [
    "company overview",
    "professional development",
    "position",
    "entry-level",
    "fresher",
    "roles responsibilities",
    "day-to-day",
    "location",
    "guide",
    "phase"
]


SECTION_HINTS = [
    "required skills",
    "responsibilities",
    "day-to-day",
    "roles",
    "tasks",
    "skills"
]


def is_requirement_sentence(sentence: str) -> bool:
    s = sentence.lower()

    # Reject non-evaluative content
    if any(p in s for p in NEGATIVE_PATTERNS):
        return False

    if len(s.split()) < 4:
        return False

    has_action = any(k in s for k in ACTION_KEYWORDS)
    has_skill = any(k in s for k in SKILL_KEYWORDS)

    return has_action and has_skill



def extract_jd_requirements(jd_sentences: List[str]) -> List[str]:
    """
    Filter JD sentences to only role-relevant requirements.
    """
    requirements = []

    for s in jd_sentences:
        if is_requirement_sentence(s):
            requirements.append(s.strip())

    # De-duplicate while preserving order
    seen = set()
    refined = []
    for r in requirements:
        if r not in seen:
            refined.append(r)
            seen.add(r)

    return refined
