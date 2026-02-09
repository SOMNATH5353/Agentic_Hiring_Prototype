from typing import Dict, List
from explainability.feature_importance import (
    calculate_feature_contributions,
    generate_waterfall_explanation,
    explain_top_matches,
    explain_skill_gaps,
    generate_counterfactual_explanation
)


def generate_xai_explanation(
    candidate_name: str,
    rfs: float,
    css: float,
    gps: float,
    dcs: float,
    elc: int,
    action,
    composite_score: float,
    semantic_matches: List[Dict],
    jd_requirements: List[str],
    resume_sentences: List[str]
) -> str:
    """
    Generate comprehensive explainable AI report for a candidate.
    """
    report = "\n" + "=" * 80 + "\n"
    report += f"EXPLAINABLE AI ANALYSIS: {candidate_name}\n"
    report += "=" * 80 + "\n\n"
    
    # 1. Feature Contribution Analysis (SHAP-like)
    report += "📊 FEATURE CONTRIBUTION ANALYSIS\n"
    report += "-" * 80 + "\n"
    contributions = calculate_feature_contributions(rfs, css, gps, dcs, elc)
    report += generate_waterfall_explanation(contributions, composite_score)
    
    # 2. Top Matching Skills (Attention Mechanism)
    report += "\n🎯 SEMANTIC SIMILARITY ANALYSIS\n"
    report += "-" * 80 + "\n"
    report += explain_top_matches(semantic_matches, top_n=5)
    
    # 3. Skill Gap Analysis
    report += "\n🔍 SKILL GAP ANALYSIS\n"
    report += "-" * 80 + "\n"
    report += explain_skill_gaps(jd_requirements, resume_sentences, semantic_matches)
    
    # 4. Counterfactual Explanations
    report += "\n🔮 COUNTERFACTUAL ANALYSIS\n"
    report += "-" * 80 + "\n"
    report += generate_counterfactual_explanation(rfs, css, gps, dcs, elc, action)
    
    # 5. Decision Rationale Summary
    report += "\n📝 DECISION SUMMARY\n"
    report += "-" * 80 + "\n"
    report += f"Final Decision: {action.value}\n"
    report += f"Composite Score: {composite_score:.4f}\n"
    report += f"Confidence Level: {_calculate_confidence(rfs, css, gps, dcs, elc)}\n"
    report += "\nKey Factors:\n"
    
    # Identify top 3 positive and negative factors
    sorted_contribs = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    report += "\nStrengths:\n"
    for feature, score in sorted_contribs[:3]:
        if score > 0.1:
            report += f"  ✓ {feature}: {score:.4f}\n"
    
    report += "\nAreas for Improvement:\n"
    for feature, score in sorted_contribs[-3:]:
        if score < 0.15:
            report += f"  ⚠ {feature}: {score:.4f}\n"
    
    report += "\n" + "=" * 80 + "\n"
    
    return report


def _calculate_confidence(rfs, css, gps, dcs, elc) -> str:
    """
    Calculate confidence level based on score variance.
    """
    scores = [rfs, css, gps, dcs, float(elc)]
    avg = sum(scores) / len(scores)
    variance = sum((x - avg) ** 2 for x in scores) / len(scores)
    
    if variance < 0.05:
        return "HIGH (scores are consistent)"
    elif variance < 0.15:
        return "MEDIUM (some score variation)"
    else:
        return "LOW (high score variation - decision may be uncertain)"
