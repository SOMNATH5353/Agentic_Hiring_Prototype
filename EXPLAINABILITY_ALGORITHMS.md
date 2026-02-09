# Explainability Algorithms Used

## 1. **Additive Feature Attribution** (SHAP-inspired)
Linear weighted contribution scoring to show impact of each metric.

## 2. **Attention-Based Semantic Matching** (Transformer-inspired)
Cosine similarity with Sentence-BERT embeddings to highlight matching skills.

## 3. **Waterfall Decomposition Analysis** (LIME-inspired)
Sequential feature contribution breakdown showing cumulative score impact.

## 4. **Counterfactual Reasoning** (Minimal Perturbation Analysis)
"What-if" scenarios showing what needs to change for different outcomes.

## 5. **Skill Gap Analysis** (Set Difference Method)
Identifies missing requirements by comparing JD vs resume skills.

## 6. **Variance-Based Confidence Scoring**
Measures decision reliability using score consistency analysis.

## 7. **Rule-Based Decision Transparency**
Explicit if-else logic (not black-box ML) for full auditability.

---

## Technologies Used:
- **Sentence-BERT** (all-MiniLM-L6-v2 model)
- **Cosine Similarity** for semantic matching
- **Linear Regression** for feature weights
- **Statistical Variance** for confidence

---

## Compliance:
✅ GDPR Article 22 (Right to Explanation)
✅ EU AI Act (Transparency Requirements)  
✅ IEEE 7000 (Ethical AI Standards)
