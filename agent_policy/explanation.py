# agent_policy/explanation.py

from agent_policy.policy import AgentAction


def explain_decision(
    action: AgentAction,
    role_fit: float,
    capability_strength: float,
    growth_potential: float,
    domain_compatibility: float,
    execution_language: float
) -> str:

    """
    Generate human-readable explanation.
    """
    # Handle None values
    role_fit = role_fit if role_fit is not None else 0.0
    capability_strength = capability_strength if capability_strength is not None else 0.0
    growth_potential = growth_potential if growth_potential is not None else 0.0
    domain_compatibility = domain_compatibility if domain_compatibility is not None else 0.0
    execution_language = execution_language if execution_language is not None else 0
    
    if action == AgentAction.SELECT_FAST_TRACK:
        return (
            f"Strong candidate with excellent role fit ({role_fit}), capability ({capability_strength}), "
            f"and domain compatibility ({domain_compatibility}). Has required programming language. "
            f"Recommended for fast-track hiring."
        )
    
    elif action == AgentAction.SCHEDULE_INTERVIEW:
        # ML developer case
        if domain_compatibility >= 0.9 and capability_strength >= 0.5:
            return (
                f"Strong ML/Python developer with excellent domain fit ({domain_compatibility}) "
                f"and capability ({capability_strength}). Growth potential: {growth_potential}. "
                f"Skills are highly transferable to this role. Recommend interview to assess specific project alignment."
            )
        
        if growth_potential >= 0.7 and domain_compatibility >= 0.7:
            return (
                f"Promising candidate with high growth potential ({growth_potential}) and strong domain fit ({domain_compatibility}). "
                f"Has required programming language. Recommend interview to assess potential and cultural fit."
            )
        
        if domain_compatibility >= 0.8 and capability_strength >= 0.5:
            return (
                f"Technically strong candidate with domain expertise ({domain_compatibility}) and capability ({capability_strength}). "
                f"Recommend interview to evaluate hands-on experience and project fit."
            )
        
        return (
            f"Good candidate with role fit ({role_fit}) and required language skills. "
            f"Domain compatibility: {domain_compatibility}. Recommend interview to assess experience depth."
        )
    
    elif action == AgentAction.POOL_FOR_FUTURE:
        return (
            f"Candidate has required language and relevant skills (domain: {domain_compatibility}, capability: {capability_strength}) "
            f"but doesn't meet current interview thresholds. Consider for future opportunities or different roles."
        )
    
    elif action == AgentAction.REJECT_WITH_REASON:
        reasons = []
        
        if execution_language == 0:
            reasons.append("missing required programming language (e.g., Java/C++ developer for Python role)")
        
        if domain_compatibility < 0.4:
            reasons.append(f"incompatible technical domain (score: {domain_compatibility})")
        
        if execution_language == 1 and domain_compatibility < 0.6 and capability_strength < 0.4:
            reasons.append("insufficient technical depth and domain alignment")
        
        if not reasons:
            reasons.append("does not meet minimum evaluation thresholds")
        
        return f"Not recommended: {'; '.join(reasons)}. "
    
    return "Unable to determine recommendation."
