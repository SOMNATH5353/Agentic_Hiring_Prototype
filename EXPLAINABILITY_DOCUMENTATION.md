# Explainability Algorithms & Techniques

This document explains the AI explainability methods used in the Agentic Hiring System.

## 1. **Feature Attribution (SHAP-like)**

### Algorithm: Additive Feature Attribution
**Location**: `explainability/feature_importance.py` → `calculate_feature_contributions()`

**Method**: Linear weighted contribution scoring
```python
contribution = feature_score × weight
composite_score = Σ(contribution_i)
```

**Weights**:
- Role Fit: 35% (highest impact)
- Domain Compatibility: 25%
- Capability Strength: 20%
- Execution Language: 15%
- Growth Potential: 5%

**Inspired by**: SHAP (SHapley Additive exPlanations)
- **Paper**: "A Unified Approach to Interpreting Model Predictions" (Lundberg & Lee, 2017)
- **Difference**: We use fixed weights instead of Shapley values for computational efficiency
- **Advantage**: Simpler, faster, transparent to users

---

## 2. **Attention Mechanism for Semantic Matching**

### Algorithm: Cosine Similarity with Attention Weights
**Location**: `semantic/similarity.py` → `compute_semantic_matches()`

**Method**: 
```python
similarity = cosine_similarity(jd_embedding, resume_embedding)
attention_score = softmax(similarity) if similarity >= threshold
```

**Technology**: Sentence-BERT embeddings (all-MiniLM-L6-v2)
- **Paper**: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks" (Reimers & Gurevych, 2019)
- **Embedding Dim**: 384
- **Similarity**: Cosine similarity in semantic space

**Explainability**:
- Shows **which JD requirements** matched **which resume experiences**
- Provides **similarity scores** (0-1) for each match
- Enables **traceability** of why a match was made

**Output**:
```
Top 5 Matching Skills:
1. Match Strength: 0.856 ████████████████
   JD Requirement: Python programming with ML frameworks
   Candidate Has:  Experienced in Python, TensorFlow, PyTorch
```

---

## 3. **Waterfall Analysis**

### Algorithm: Sequential Contribution Decomposition
**Location**: `explainability/feature_importance.py` → `generate_waterfall_explanation()`

**Method**: Shows cumulative impact of features
```
Baseline: 0.0000
+ Role Fit:              +0.2118  (total: 0.2118)
+ Domain Compatibility:  +0.2188  (total: 0.4306)
+ Capability Strength:   +0.0690  (total: 0.4996)
+ Execution Language:    +0.1500  (total: 0.6496)
+ Growth Potential:      +0.0500  (total: 0.6996)
────────────────────────────────────────────
Final Composite Score:   0.6996
```

**Inspired by**: LIME (Local Interpretable Model-agnostic Explanations)
- **Paper**: "Why Should I Trust You?" (Ribeiro et al., 2016)
- **Difference**: We decompose a formula rather than approximating a black-box model
- **Advantage**: Exact attribution, no approximation error

---

## 4. **Counterfactual Explanations**

### Algorithm: What-If Scenario Analysis
**Location**: `explainability/feature_importance.py` → `generate_counterfactual_explanation()`

**Method**: Minimal perturbation analysis
```python
# Test each feature independently
for feature in features:
    new_score = feature + delta
    new_decision = decide_action(new_score, ...)
    if new_decision != current_decision:
        report_counterfactual(feature, delta)
```

**Inspired by**: Wachter's Counterfactual Explanations
- **Paper**: "Counterfactual Explanations without Opening the Black Box" (Wachter et al., 2017)
- **Method**: Find minimal changes to flip the decision
- **Example**: "If Role Fit was 0.7+ → Decision would be SELECT_FAST_TRACK"

**Benefits**:
- Shows **actionable insights**: "What needs to improve?"
- **User-friendly**: Non-technical stakeholders understand "what-if"
- **Recourse**: Candidates know what to improve for future opportunities

---

## 5. **Skill Gap Analysis**

### Algorithm: Set Difference with Semantic Matching
**Location**: `explainability/feature_importance.py` → `explain_skill_gaps()`

**Method**:
```python
jd_requirements = set(JD skills)
resume_skills = set(matched resume skills)
gaps = jd_requirements - resume_skills
```

**Technology**: 
- Uses semantic embeddings to determine matches
- Threshold: 0.55 cosine similarity
- Unmatched requirements flagged as gaps

**Output**:
```
⚠️ Potential Skill Gaps (3 requirements not strongly matched):
1. Flask/Django web framework experience
2. AWS cloud deployment
3. Docker containerization
```

---

## 6. **Confidence Scoring**

### Algorithm: Variance-based Uncertainty Estimation
**Location**: `explainability/xai_report.py` → `_calculate_confidence()`

**Method**:
```python
variance = Σ(score_i - mean)² / n
confidence = HIGH if variance < 0.05
           = MEDIUM if variance < 0.15
           = LOW otherwise
```

**Inspired by**: Ensemble uncertainty in Random Forests
- High variance → Conflicting signals → Low confidence
- Low variance → Consistent scores → High confidence

**Example**:
```
Scores: [0.75, 0.68, 0.72, 0.70, 0.73]
Variance: 0.0008 → HIGH CONFIDENCE (scores are consistent)

Scores: [0.9, 0.2, 0.8, 0.3, 0.7]
Variance: 0.088 → LOW CONFIDENCE (high variation)
```

---

## 7. **Decision Tree Transparency**

### Algorithm: Explicit Rule-Based Decision Logic
**Location**: `agent_policy/policy.py` → `decide_action()`

**Method**: Transparent if-else rules (not a black-box ML model)
```python
if execution_language == 0:
    return REJECT  # Missing required language

if role_fit >= 0.6 and capability_strength >= 0.3:
    return SELECT_FAST_TRACK  # Strong match

if domain_compatibility >= 0.9 and capability_strength >= 0.5:
    return SCHEDULE_INTERVIEW  # ML dev for Python role

# ... more rules
```

**Benefits**:
- **Fully transparent**: Every decision can be traced
- **Auditable**: Meets legal requirements (GDPR, AI Act)
- **Debuggable**: Easy to understand and modify
- **Fair**: No hidden bias from opaque neural networks

---

## Summary: XAI Techniques Comparison

| Technique | Algorithm | Inspiration | Purpose |
|-----------|-----------|-------------|---------|
| **Feature Attribution** | Weighted linear sum | SHAP | Show contribution of each metric |
| **Semantic Attention** | Cosine similarity + embeddings | Transformer attention | Explain specific matches |
| **Waterfall Analysis** | Sequential decomposition | LIME | Visualize cumulative impact |
| **Counterfactuals** | Minimal perturbation | Wachter et al. | "What needs to change?" |
| **Skill Gap** | Set difference | N/A | Identify missing requirements |
| **Confidence** | Variance analysis | Ensemble methods | Uncertainty quantification |
| **Decision Rules** | Explicit logic | N/A | Full transparency |

---

## Key Papers & References

1. **SHAP**: Lundberg, S. M., & Lee, S. I. (2017). "A unified approach to interpreting model predictions." *NeurIPS*.

2. **LIME**: Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you? Explaining the predictions of any classifier." *KDD*.

3. **Sentence-BERT**: Reimers, N., & Gurevych, I. (2019). "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *EMNLP*.

4. **Counterfactuals**: Wachter, S., Mittelstadt, B., & Russell, C. (2017). "Counterfactual explanations without opening the black box." *Harvard JL & Tech*.

5. **Attention Mechanisms**: Vaswani, A., et al. (2017). "Attention is all you need." *NeurIPS*.

---

## Compliance & Ethics

### GDPR Article 22 (Right to Explanation)
✅ **Compliant**: System provides detailed explanations for all automated decisions

### EU AI Act (Transparency Requirements)
✅ **Compliant**: 
- Transparent decision logic
- Explainable scoring
- Human oversight possible
- Bias mitigation through PII removal

### IEEE 7000 (Ethical AI Standards)
✅ **Compliant**:
- Fairness: No direct use of protected attributes
- Transparency: Full visibility into decisions
- Accountability: Traceable decision paths
- Privacy: PII redaction before processing

---

## Future Enhancements

1. **SHAP Integration**: Replace linear weights with actual Shapley values
2. **LIME Integration**: Add local model explanations for edge cases
3. **Contrastive Explanations**: "Why this candidate over that one?"
4. **Fairness Metrics**: Demographic parity, equal opportunity analysis
5. **Interactive Explanations**: Web UI for drilling into specific decisions

---

## Usage Example

```python
from explainability.xai_report import generate_xai_explanation

xai_report = generate_xai_explanation(
    candidate_name="candidate.pdf",
    rfs=0.75, css=0.68, gps=0.85, dcs=0.92, elc=1,
    action=AgentAction.SELECT_FAST_TRACK,
    composite_score=0.78,
    semantic_matches=matches,
    jd_requirements=jd_reqs,
    resume_sentences=resume_sents
)

print(xai_report)
```

Output includes:
- Feature contributions (SHAP-like)
- Top semantic matches (Attention)
- Skill gaps
- Counterfactual scenarios
- Confidence assessment
- Decision rationale
