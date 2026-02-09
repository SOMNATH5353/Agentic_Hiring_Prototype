# agent_policy/policy.py

from enum import Enum

class AgentAction(Enum):
    SELECT_FAST_TRACK = "Select for fast-track hiring"
    SCHEDULE_INTERVIEW = "Schedule interview"
    POOL_FOR_FUTURE = "Add to talent pool for future roles"
    REJECT_WITH_REASON = "Reject with explanation"


def decide_action(
    role_fit: float,
    capability_strength: float,
    growth_potential: float,
    domain_compatibility: float,
    execution_language: float
) -> AgentAction:
    """
    Enhanced agent decision policy.
    Gives fair consideration to ML developers for Python roles.
    """
    # Handle None values with defaults
    role_fit = role_fit if role_fit is not None else 0.0
    capability_strength = capability_strength if capability_strength is not None else 0.0
    growth_potential = growth_potential if growth_potential is not None else 0.0
    domain_compatibility = domain_compatibility if domain_compatibility is not None else 0.0
    execution_language = execution_language if execution_language is not None else 0
    
    # Hard reject: Missing required language (strict check)
    if execution_language == 0:
        return AgentAction.REJECT_WITH_REASON
    
    # Hard reject: Very low domain compatibility (wrong tech stack)
    if domain_compatibility < 0.4:
        return AgentAction.REJECT_WITH_REASON
    
    # Fast track: Strong role fit + good capabilities + language match
    if role_fit >= 0.6 and capability_strength >= 0.3 and execution_language == 1:
        return AgentAction.SELECT_FAST_TRACK
    
    # Interview: Good role fit with language match
    if role_fit >= 0.5 and execution_language == 1:
        return AgentAction.SCHEDULE_INTERVIEW
    
    # Interview: High growth potential + good domain fit + language match
    if growth_potential >= 0.7 and domain_compatibility >= 0.7 and execution_language == 1:
        return AgentAction.SCHEDULE_INTERVIEW
    
    # Interview: Strong domain match + decent capability (ML dev for Python role)
    # This catches ML developers who have perfect domain fit but low direct role matches
    if domain_compatibility >= 0.9 and capability_strength >= 0.5 and execution_language == 1:
        return AgentAction.SCHEDULE_INTERVIEW
    
    # Interview: High domain + capability + language (even with low role fit)
    if domain_compatibility >= 0.8 and capability_strength >= 0.5 and execution_language == 1:
        return AgentAction.SCHEDULE_INTERVIEW
    
    # Pool for future: Has language + decent skills but weak on multiple dimensions
    if execution_language == 1 and domain_compatibility >= 0.6 and (capability_strength >= 0.4 or growth_potential >= 0.6):
        return AgentAction.POOL_FOR_FUTURE
    
    # Default reject
    return AgentAction.REJECT_WITH_REASON
