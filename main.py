# main.py

import os

from ingestion.loader import load_text
from ingestion.preprocess import preprocess_text
from utils.pdf_writer import write_analysis_pdf
from utils.ranking_pdf_writer import write_ranking_pdf
from explainability.xai_report import generate_xai_explanation
from agent_policy.ranking import rank_candidates, generate_ranking_report, calculate_composite_score

from semantic.embedder import SemanticEmbedder
from semantic.similarity import compute_semantic_matches
from agent_policy.scores import (
    role_fit_score,
    combined_role_fit_score,  # ← ADD THIS
    capability_strength_score,
    growth_potential_score,
    domain_compatibility_score,
    execution_language_score
)
from agent_policy.policy import decide_action
from agent_policy.explanation import explain_decision
from agent_policy.ranking import rank_candidates, generate_ranking_report, calculate_composite_score

from ontology.jd_requirements import extract_jd_requirements

from agent_policy.scores import (
    role_fit_score,
    combined_role_fit_score,  # ← ADD THIS
    capability_strength_score,
    growth_potential_score,
    domain_compatibility_score,
    execution_language_score
)

from agent_policy.policy import decide_action
from agent_policy.explanation import explain_decision
from agent_policy.ranking import rank_candidates, generate_ranking_report, calculate_composite_score


DATA_DIR = "data"

# Heuristic keywords to identify Job Description
JD_KEYWORDS = [
    "job description",
    "responsibilities",
    "requirements",
    "we are hiring",
    "skills required",
    "role",
    "eligibility",
    "position"
]


def is_job_description(text: str) -> bool:
    """
    Explainable heuristic to distinguish JD from resumes.
    """
    text_lower = text.lower()
    score = sum(1 for kw in JD_KEYWORDS if kw in text_lower)
    return score >= 2


def main():
    # --------------------------------------------------
    # STEP 1: Load all PDFs
    # --------------------------------------------------
    pdf_files = [
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        raise RuntimeError("❌ No PDF files found in data folder.")

    # --------------------------------------------------
    # STEP 2: Identify JD vs Resumes
    # --------------------------------------------------
    jd_text = None
    jd_file = None
    resume_files = []

    for pdf in pdf_files:
        text = load_text(pdf)

        if is_job_description(text) and jd_text is None:
            jd_text = text
            jd_file = pdf
        else:
            resume_files.append((pdf, text))

    if jd_text is None:
        raise RuntimeError("❌ Job Description could not be identified.")

    print(f"\n✅ Job Description identified: {jd_file}")

    # --------------------------------------------------
    # STEP 3: Preprocess JD (PII-safe)
    # --------------------------------------------------
    jd_sentences = preprocess_text(jd_text)

    print("\n--- JOB DESCRIPTION (SANITIZED PREVIEW) ---")
    for s in jd_sentences[:8]:
        print("JD:", s)

    # --------------------------------------------------
    # STEP 4: Extract JD REQUIREMENTS (Evaluative Only)
    # --------------------------------------------------
    jd_requirements = extract_jd_requirements(jd_sentences)

    print("\n📌 JD REQUIREMENTS USED FOR EVALUATION:")
    for r in jd_requirements:
        print("REQ:", r)

    # --------------------------------------------------
    # STEP 5: Preprocess Resumes (PII-safe)
    # --------------------------------------------------
    parsed_resumes = {}

    for resume_file, resume_text in resume_files:
        clean_sentences = preprocess_text(resume_text)
        parsed_resumes[os.path.basename(resume_file)] = clean_sentences

    print(f"\n📄 {len(parsed_resumes)} resumes processed (PII removed).")

    # --------------------------------------------------
    # STEP 6: Store Unbiased Parsed Output (Audit PDF)
    # --------------------------------------------------
    output_pdf = "analysis_output.pdf"

    write_analysis_pdf(
        output_path=output_pdf,
        jd_sentences=jd_sentences,
        resumes=parsed_resumes
    )

    print(f"\n✅ Unbiased analysis saved to `{output_pdf}`")
    print("✅ No names, emails, phone numbers, or links were stored.")

    # --------------------------------------------------
    # STEP 7: AGENTIC EVALUATION
    # --------------------------------------------------
    print("\n🤖 Starting Agentic Evaluation...\n")

    embedder = SemanticEmbedder()
    jd_embeddings = embedder.encode(jd_requirements)
    
    # Determine required language from JD
    REQUIRED_LANGUAGE = "python"

    # Store all candidate data for ranking
    candidates_data = []
    xai_reports = {}  # Store XAI explanations

    for resume_name, resume_sentences in parsed_resumes.items():
        resume_embeddings = embedder.encode(resume_sentences)

        semantic_matches = compute_semantic_matches(
            jd_sentences=jd_requirements,
            jd_embeddings=jd_embeddings,
            resume_sentences=resume_sentences,
            resume_embeddings=resume_embeddings,
            threshold=0.55
        )

        # -------- AGENT SCORES --------
        # Use combined scoring that recognizes ML → Python transferability
        rfs = combined_role_fit_score(semantic_matches, resume_sentences, jd_requirements)
        css = capability_strength_score(resume_sentences)
        gps = growth_potential_score(resume_sentences)
        dcs = domain_compatibility_score(jd_requirements, resume_sentences)
        elc = execution_language_score(REQUIRED_LANGUAGE, resume_sentences)

        # -------- AGENT DECISION --------
        action = decide_action(rfs, css, gps, dcs, elc)
        explanation = explain_decision(action, rfs, css, gps, dcs, elc)
        composite = calculate_composite_score(rfs, css, gps, dcs, elc)

        # -------- EXPLAINABLE AI ANALYSIS --------
        xai_explanation = generate_xai_explanation(
            candidate_name=resume_name,
            rfs=rfs, css=css, gps=gps, dcs=dcs, elc=elc,
            action=action,
            composite_score=composite,
            semantic_matches=semantic_matches,
            jd_requirements=jd_requirements,
            resume_sentences=resume_sentences
        )
        
        xai_reports[resume_name] = xai_explanation

        # Store candidate data
        candidates_data.append({
            'name': resume_name,
            'rfs': rfs,
            'css': css,
            'gps': gps,
            'dcs': dcs,
            'elc': elc,
            'action': action,
            'explanation': explanation
        })

        # -------- OUTPUT --------
        print(f"📄 Candidate: {resume_name}")
        print(f"  Role Fit Score (RFS): {rfs}")
        print(f"  Capability Strength Score (CSS): {css}")
        print(f"  Growth Potential Score (GPS): {gps}")
        print(f"  Domain Compatibility Score (DCS): {dcs}")
        print(f"  Execution Language Score (ELC): {elc}")
        print(f"  🧠 Agent Action: {action}")
        print(f"  📝 Explanation: {explanation}")
        print(f"\n  🔍 XAI Analysis Available - see xai_explanations.txt\n")

    # --------------------------------------------------
    # STEP 8: RANK CANDIDATES WITH TIEBREAKERS
    # --------------------------------------------------
    print("\n🏆 Ranking candidates...\n")
    
    ranked_candidates = rank_candidates(candidates_data)
    ranking_report = generate_ranking_report(ranked_candidates)
    
    print(ranking_report)
    
    # Save ranking to text file
    with open("candidate_ranking.txt", "w", encoding="utf-8") as f:
        f.write(ranking_report)
    
    print("✅ Candidate ranking saved to 'candidate_ranking.txt'")
    
    # --------------------------------------------------
    # STEP 9: SAVE XAI EXPLANATIONS
    # --------------------------------------------------
    xai_output = "xai_explanations.txt"
    
    with open(xai_output, "w", encoding="utf-8") as f:
        f.write("EXPLAINABLE AI CANDIDATE ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        for resume_name in ranked_candidates:
            candidate_name = resume_name['name']
            if candidate_name in xai_reports:
                f.write(xai_reports[candidate_name])
                f.write("\n\n")
    
    print(f"✅ Explainable AI analysis saved to '{xai_output}'")
    
    # --------------------------------------------------
    # STEP 10: GENERATE COMPREHENSIVE RANKING PDF
    # --------------------------------------------------
    ranking_pdf = "candidate_ranking_report.pdf"
    
    write_ranking_pdf(
        output_path=ranking_pdf,
        ranked_candidates=ranked_candidates,
        jd_file=jd_file
    )
    
    print(f"✅ Comprehensive ranking report saved to '{ranking_pdf}'")
    print("✅ Agentic evaluation completed.")


if __name__ == "__main__":
    main()
