import numpy as np
from typing import List, Dict, Tuple


def calculate_feature_contributions(rfs, css, gps, dcs, elc) -> Dict[str, float]:
    """
    Calculate how much each feature contributed to the final score.
    Similar to SHAP values but simplified.
    """
    # Weights used in composite score
    weights = {
        'Role Fit': 0.35,
        'Domain Compatibility': 0.25,
        'Capability Strength': 0.20,
        'Execution Language': 0.15,
        'Growth Potential': 0.05
    }
    
    # Actual contributions
    contributions = {
        'Role Fit': rfs * weights['Role Fit'],
        'Domain Compatibility': dcs * weights['Domain Compatibility'],
        'Capability Strength': css * weights['Capability Strength'],
        'Execution Language': elc * weights['Execution Language'],
        'Growth Potential': gps * weights['Growth Potential']
    }
    
    return contributions


def generate_waterfall_explanation(contributions: Dict[str, float], 
                                   composite_score: float) -> str:
    """
    Generate a waterfall-style explanation showing how each feature
    contributed to the final score.
    """
    explanation = "Score Breakdown (Waterfall Analysis):\n"
    explanation += "=" * 60 + "\n"
    
    baseline = 0.0
    explanation += f"{'Baseline:':<30} {baseline:>6.4f}\n"
    explanation += "-" * 60 + "\n"
    
    # Sort by contribution (highest impact first)
    sorted_contributions = sorted(contributions.items(), 
                                 key=lambda x: abs(x[1]), 
                                 reverse=True)
    
    running_total = baseline
    for feature, contribution in sorted_contributions:
        running_total += contribution
        impact = "↑" if contribution > 0.15 else "→" if contribution > 0.05 else "↓"
        explanation += f"{feature + ':':<30} +{contribution:>6.4f}  {impact}  (total: {running_total:.4f})\n"
    
    explanation += "-" * 60 + "\n"
    explanation += f"{'Final Composite Score:':<30} {composite_score:>6.4f}\n"
    explanation += "=" * 60 + "\n"
    
    return explanation


def explain_top_matches(semantic_matches: List[Dict], top_n: int = 5) -> str:
    """
    Explain which JD requirements best matched the candidate's experience.
    """
    if not semantic_matches:
        return "No semantic matches found between JD and resume."
    
    explanation = f"\nTop {min(top_n, len(semantic_matches))} Matching Skills/Experience:\n"
    explanation += "=" * 80 + "\n"
    
    for i, match in enumerate(semantic_matches[:top_n], 1):
        similarity = match['similarity']
        # Fix key names - check actual structure from similarity.py
        jd_req = match.get('jd_text', match.get('jd_sentence', ''))[:80]
        resume_exp = match.get('resume_text', match.get('resume_sentence', ''))[:80]
        
        # Visual similarity indicator
        bars = "█" * int(similarity * 20)
        
        explanation += f"\n{i}. Match Strength: {similarity:.3f} {bars}\n"
        explanation += f"   JD Requirement: {jd_req}...\n"
        explanation += f"   Candidate Has:  {resume_exp}...\n"
    
    explanation += "\n" + "=" * 80 + "\n"
    
    return explanation


def explain_skill_gaps(jd_requirements: List[str], 
                      resume_sentences: List[str],
                      semantic_matches: List[Dict]) -> str:
    """
    Identify and explain skill gaps - what JD requirements were NOT matched.
    """
    # Get matched JD requirements - fix key name
    matched_jd = set()
    for match in semantic_matches:
        jd_text = match.get('jd_text', match.get('jd_sentence', ''))
        if jd_text:
            matched_jd.add(jd_text)
    
    # Find unmatched requirements
    gaps = [req for req in jd_requirements if req not in matched_jd]
    
    if not gaps:
        return "\n✅ All JD requirements have at least some matching experience!\n"
    
    explanation = f"\n⚠️  Potential Skill Gaps ({len(gaps)} requirements not strongly matched):\n"
    explanation += "=" * 80 + "\n"
    
    for i, gap in enumerate(gaps[:5], 1):  # Show top 5 gaps
        explanation += f"{i}. {gap[:100]}...\n"
    
    if len(gaps) > 5:
        explanation += f"\n... and {len(gaps) - 5} more unmatched requirements.\n"
    
    explanation += "=" * 80 + "\n"
    
    return explanation


def generate_counterfactual_explanation(rfs, css, gps, dcs, elc, action) -> str:
    """
    Generate "what-if" explanations: "If X was higher, the outcome would be..."
    """
    from agent_policy.policy import decide_action, AgentAction
    
    explanation = "\n🔮 Counterfactual Analysis (What would change the decision?):\n"
    explanation += "=" * 80 + "\n"
    
    # Test what happens if we boost each score
    scenarios = []
    
    # Scenario 1: Boost Role Fit
    if rfs < 0.7:
        new_action = decide_action(0.7, css, gps, dcs, elc)
        if new_action != action:
            scenarios.append(f"• If Role Fit was 0.7+ → Decision would be: {new_action.value}")
    
    # Scenario 2: Boost Domain Compatibility
    if dcs < 0.9:
        new_action = decide_action(rfs, css, gps, 0.9, elc)
        if new_action != action:
            scenarios.append(f"• If Domain Compatibility was 0.9+ → Decision would be: {new_action.value}")
    
    # Scenario 3: Boost Capability
    if css < 0.6:
        new_action = decide_action(rfs, 0.6, gps, dcs, elc)
        if new_action != action:
            scenarios.append(f"• If Capability Strength was 0.6+ → Decision would be: {new_action.value}")
    
    # Scenario 4: Add execution language if missing
    if elc == 0:
        new_action = decide_action(rfs, css, gps, dcs, 1)
        if new_action != action:
            scenarios.append(f"• If candidate had required language → Decision would be: {new_action.value}")
    
    if scenarios:
        for scenario in scenarios:
            explanation += scenario + "\n"
    else:
        explanation += "• No single score change would significantly alter the decision.\n"
        explanation += "  This indicates a robust evaluation.\n"
    
    explanation += "=" * 80 + "\n"
    
    return explanation
