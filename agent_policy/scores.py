# agent_policy/scores.py

from typing import List, Dict


# -------------------------------
# ROLE FIT SCORE
# -------------------------------
def role_fit_score(semantic_matches: List[Dict]) -> float:
    """
    Calculate role fit score based on semantic matches.
    Returns: float between 0 and 1
    """
    if not semantic_matches:
        return 0.0
    
    # Average similarity of top matches
    top_n = min(10, len(semantic_matches))
    if top_n == 0:
        return 0.0
    
    avg_score = sum(m['similarity'] for m in semantic_matches[:top_n]) / top_n
    return round(avg_score, 3)


# -------------------------------
# CAPABILITY STRENGTH SCORE
# -------------------------------
def capability_strength_score(resume_sentences: List[str]) -> float:
    """
    Calculate capability strength based on keywords.
    Returns: float between 0 and 1
    """
    if not resume_sentences:
        return 0.0
    
    strength_keywords = [
        'expert', 'advanced', 'proficient', 'experienced',
        'senior', 'lead', 'architect', 'specialist',
        'years', 'projects', 'deployed', 'production'
    ]
    
    matches = sum(
        1 for sent in resume_sentences
        for kw in strength_keywords
        if kw in sent.lower()
    )
    
    # Normalize by sentence count
    score = min(1.0, matches / max(1, len(resume_sentences)) * 5)
    return round(score, 3)


# -------------------------------
# GROWTH POTENTIAL SCORE
# -------------------------------
def growth_potential_score(resume_sentences: List[str]) -> float:
    """
    Calculate growth potential based on learning indicators.
    Returns: float between 0 and 1
    """
    if not resume_sentences:
        return 0.0
    
    growth_keywords = [
        'learning', 'course', 'certification', 'training',
        'bootcamp', 'internship', 'project', 'hackathon',
        'self-taught', 'passionate', 'eager', 'motivated'
    ]
    
    matches = sum(
        1 for sent in resume_sentences
        for kw in growth_keywords
        if kw in sent.lower()
    )
    
    # Normalize
    score = min(1.0, matches / max(1, len(resume_sentences)) * 5)
    return round(score, 3)


# -------------------------------
# DOMAIN COMPATIBILITY SCORE (NEW)
# -------------------------------
def domain_compatibility_score(
    jd_requirements: List[str],
    resume_sentences: List[str]
) -> float:
    """
    Calculate domain compatibility using keyword overlap.
    Returns: float between 0 and 1
    """
    if not jd_requirements or not resume_sentences:
        return 0.0
    
    # Extract keywords from JD and resume
    jd_text = ' '.join(jd_requirements).lower()
    resume_text = ' '.join(resume_sentences).lower()
    
    # Define technical keywords by category
    python_keywords = ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras']
    ml_keywords = ['machine learning', 'ml', 'data science', 'ai', 'deep learning', 'neural network', 'model training']
    data_keywords = ['data analysis', 'data processing', 'sql', 'postgresql', 'mongodb', 'data visualization']
    web_keywords = ['api', 'rest', 'http', 'web', 'backend', 'frontend']
    java_keywords = ['java', 'spring', 'hibernate', 'j2ee', 'maven', 'gradle']
    cpp_keywords = ['c++', 'cpp', 'stl', 'boost']
    
    # Count matches for each category
    def count_matches(keywords, jd_text, resume_text):
        jd_count = sum(1 for kw in keywords if kw in jd_text)
        resume_count = sum(1 for kw in keywords if kw in resume_text)
        # Return ratio of how many JD keywords are in resume
        return resume_count / jd_count if jd_count > 0 else 0
    
    # Calculate category scores
    python_score = count_matches(python_keywords, jd_text, resume_text)
    ml_score = count_matches(ml_keywords, jd_text, resume_text)
    data_score = count_matches(data_keywords, jd_text, resume_text)
    web_score = count_matches(web_keywords, jd_text, resume_text)
    
    # Check if resume is in wrong domain (Java/C++ when Python is required)
    java_in_resume = any(kw in resume_text for kw in java_keywords)
    cpp_in_resume = any(kw in resume_text for kw in cpp_keywords)
    python_in_jd = any(kw in jd_text for kw in python_keywords + ml_keywords)
    
    # Penalty for wrong primary language
    if python_in_jd and (java_in_resume or cpp_in_resume):
        # Check if they also have Python/ML skills
        has_python = any(kw in resume_text for kw in python_keywords + ml_keywords)
        if not has_python:
            # Pure Java/C++ dev for Python role = low compatibility
            return round(max(web_score * 0.3, 0.1), 3)
    
    # Average the relevant scores
    scores = [python_score, ml_score, data_score, web_score]
    relevant_scores = [s for s in scores if s > 0]
    
    if not relevant_scores:
        return 0.0
    
    final_score = sum(relevant_scores) / len(relevant_scores)
    return round(min(1.0, final_score), 3)


# -------------------------------
# EXECUTION LANGUAGE SCORE
# -------------------------------
def execution_language_score(
    required_language: str,
    resume_sentences: list[str]
) -> float:
    """
    Check if candidate has required programming language.
    Now more strict - only accepts actual language match or close equivalents.
    Returns: 1 if found, 0 if not found
    """
    if not resume_sentences or not required_language:
        return 0
    
    resume_text = ' '.join(resume_sentences).lower()
    required_language = required_language.lower()
    
    # Direct check first
    if required_language in resume_text:
        return 1
    
    # Limited equivalences - only accept truly compatible skills
    if required_language == 'python':
        # Accept if they have ML/Data Science (which implies Python)
        ml_indicators = ['machine learning', 'data science', 'tensorflow', 'pytorch', 
                        'keras', 'scikit-learn', 'pandas', 'numpy']
        if any(indicator in resume_text for indicator in ml_indicators):
            return 1
        return 0
    
    elif required_language == 'javascript':
        js_variants = ['javascript', 'typescript', 'node', 'nodejs', 'react', 'angular', 'vue']
        if any(variant in resume_text for variant in js_variants):
            return 1
        return 0
    
    elif required_language == 'java':
        java_indicators = ['java', 'spring', 'j2ee', 'kotlin']
        if any(indicator in resume_text for indicator in java_indicators):
            return 1
        return 0
    
    elif required_language == 'c++':
        cpp_indicators = ['c++', 'cpp']
        if any(indicator in resume_text for indicator in cpp_indicators):
            return 1
        return 0
    
    # No match found
    return 0
