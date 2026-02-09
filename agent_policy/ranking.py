from typing import List, Dict, Tuple
from agent_policy.policy import AgentAction

def calculate_composite_score(rfs, css, gps, dcs, elc) -> float:
    """
    Calculate weighted composite score for ranking.
    Updated weights to value domain compatibility more for ML/DS candidates.
    
    Weights prioritize:
    - Domain Compatibility (30%): ↑ Increased - ML expertise is highly valuable
    - Role Fit (30%): Remains important but shares top priority
    - Capability Strength (20%): Experience matters
    - Execution Language (15%): Must have required language
    - Growth Potential (5%): Nice to have for future
    """
    weights = {
        'dcs': 0.30,  # ↑ Increased from 0.25
        'rfs': 0.30,  # ↑ Increased from 0.35
        'css': 0.20,  # Same
        'elc': 0.15,  # Same
        'gps': 0.05   # Same
    }
    
    # Normalize ELC to 0-1 scale (it's 0 or 1)
    elc_normalized = elc
    
    composite = (
        weights['rfs'] * rfs +
        weights['dcs'] * dcs +
        weights['css'] * css +
        weights['elc'] * elc_normalized +
        weights['gps'] * gps
    )
    
    return round(composite, 4)


def apply_tiebreakers(candidates: List[Dict]) -> List[Dict]:
    """
    Apply tiebreaker rules when composite scores are equal.
    
    Tiebreaker priority:
    1. Action priority (SELECT_FAST_TRACK > SCHEDULE_INTERVIEW > POOL > REJECT)
    2. Domain Compatibility Score (higher is better)
    3. Role Fit Score (higher is better)
    4. Capability Strength Score (higher is better)
    5. Alphabetical by filename (last resort)
    """
    # Define action priority
    action_priority = {
        AgentAction.SELECT_FAST_TRACK: 4,
        AgentAction.SCHEDULE_INTERVIEW: 3,
        AgentAction.POOL_FOR_FUTURE: 2,
        AgentAction.REJECT_WITH_REASON: 1
    }
    
    def tiebreaker_key(candidate):
        return (
            -candidate['composite_score'],  # Higher score first
            -action_priority.get(candidate['action'], 0),  # Better action first
            -candidate['dcs'],  # Higher domain compatibility
            -candidate['rfs'],  # Higher role fit
            -candidate['css'],  # Higher capability
            candidate['name']  # Alphabetical as last resort
        )
    
    return sorted(candidates, key=tiebreaker_key)


def rank_candidates(candidates_data: List[Dict]) -> List[Dict]:
    """
    Rank all candidates with composite scores and handle ties.
    
    Input format:
    [
        {
            'name': 'candidate.pdf',
            'rfs': 0.5,
            'css': 0.6,
            'gps': 0.7,
            'dcs': 0.8,
            'elc': 1,
            'action': AgentAction.SCHEDULE_INTERVIEW,
            'explanation': '...'
        },
        ...
    ]
    
    Returns ranked list with added fields:
    - composite_score: weighted score
    - rank: 1-based ranking (with ties marked)
    - tier: 'Excellent', 'Good', 'Marginal', 'Rejected'
    """
    # Calculate composite scores
    for candidate in candidates_data:
        candidate['composite_score'] = calculate_composite_score(
            candidate['rfs'],
            candidate['css'],
            candidate['gps'],
            candidate['dcs'],
            candidate['elc']
        )
    
    # Apply tiebreakers and sort
    ranked = apply_tiebreakers(candidates_data)
    
    # Assign ranks (handle ties)
    current_rank = 1
    for i, candidate in enumerate(ranked):
        if i > 0 and ranked[i]['composite_score'] == ranked[i-1]['composite_score']:
            # Same score as previous = tied rank
            candidate['rank'] = f"{current_rank}T"  # T for Tie
        else:
            if i > 0:
                current_rank = i + 1
            candidate['rank'] = current_rank
        
        # Assign tier based on composite score
        score = candidate['composite_score']
        if score >= 0.7:
            candidate['tier'] = 'Excellent'
        elif score >= 0.5:
            candidate['tier'] = 'Good'
        elif score >= 0.3:
            candidate['tier'] = 'Marginal'
        else:
            candidate['tier'] = 'Rejected'
    
    return ranked


def generate_ranking_report(ranked_candidates: List[Dict]) -> str:
    """
    Generate a formatted ranking report.
    """
    report = "\n" + "="*80 + "\n"
    report += "📊 CANDIDATE RANKING REPORT\n"
    report += "="*80 + "\n\n"
    
    for candidate in ranked_candidates:
        rank_str = f"#{candidate['rank']}"
        report += f"{rank_str:>5} | {candidate['name']:<25} | Score: {candidate['composite_score']:.4f} | {candidate['tier']}\n"
        report += f"      | Action: {candidate['action'].value}\n"
        report += f"      | RFS: {candidate['rfs']:.3f} | CSS: {candidate['css']:.3f} | GPS: {candidate['gps']:.3f} | DCS: {candidate['dcs']:.3f} | ELC: {candidate['elc']}\n"
        
        # Show tiebreaker info if tied
        if isinstance(candidate['rank'], str) and 'T' in str(candidate['rank']):
            report += f"      | ⚠️  Tied with other candidate(s) - ranked by domain compatibility and role fit\n"
        
        report += f"      | Reason: {candidate['explanation'][:100]}...\n"
        report += "-" * 80 + "\n"
    
    report += "\n" + "="*80 + "\n"
    report += "TIER DEFINITIONS:\n"
    report += "  • Excellent (≥0.7): Top candidates, recommend immediate action\n"
    report += "  • Good (≥0.5): Solid candidates, worth interviewing\n"
    report += "  • Marginal (≥0.3): Edge cases, consider for specific needs\n"
    report += "  • Rejected (<0.3): Not suitable for current role\n"
    report += "="*80 + "\n"
    
    return report
