import os
from pathlib import Path
from typing import Dict, List

from ingestion.loader import load_text
from ingestion.preprocess import preprocess_text
from ontology.jd_requirements import extract_jd_requirements
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
from agent_policy.ranking import rank_candidates, calculate_composite_score
from explainability.xai_report import generate_xai_explanation
from utils.pdf_writer import write_analysis_pdf
from utils.ranking_pdf_writer import write_ranking_pdf


# Heuristic to identify JD
JD_KEYWORDS = [
    "job description", "responsibilities", "requirements",
    "we are hiring", "skills required", "role", "eligibility", "position"
]


def is_job_description(text: str) -> bool:
    text_lower = text.lower()
    score = sum(1 for kw in JD_KEYWORDS if kw in text_lower)
    return score >= 2


class AnalysisService:
    def __init__(self):
        self.embedder = None
        self.required_language = "python"
        # Cache JD processing results
        self.jd_sentences = None
        self.jd_requirements = None
        self.jd_embeddings = None
    
    def is_model_loaded(self) -> bool:
        return self.embedder is not None
    
    def _ensure_embedder(self):
        if self.embedder is None:
            self.embedder = SemanticEmbedder()
    
    async def process_jd(self, jd_dir: str):
        """
        Process Job Description and cache results.
        Called when JD is uploaded via POST /upload-jd
        """
        self._ensure_embedder()
        
        # Load JD file
        pdf_files = list(Path(jd_dir).glob("*.pdf"))
        
        if len(pdf_files) != 1:
            raise ValueError("Exactly 1 JD PDF file required")
        
        jd_file = pdf_files[0]
        jd_text = load_text(str(jd_file))
        
        # Check if it's a valid JD
        if not is_job_description(jd_text):
            raise ValueError("Uploaded file does not appear to be a Job Description")
        
        # Preprocess and extract requirements
        self.jd_sentences = preprocess_text(jd_text)
        self.jd_requirements = extract_jd_requirements(self.jd_sentences)
        
        # Generate embeddings
        self.jd_embeddings = self.embedder.encode(self.jd_requirements)
        
        print(f"✅ JD processed: {len(self.jd_requirements)} requirements extracted")
    
    
    async def analyze_resumes(self, jd_dir: str, resumes_dir: str, output_dir: str) -> Dict:
        """
        Analyze resumes against previously uploaded JD.
        Uses cached JD data from process_jd().
        """
        self._ensure_embedder()
        
        # Ensure JD is processed
        if self.jd_requirements is None or self.jd_embeddings is None:
            # Process JD if not already done
            await self.process_jd(jd_dir)
        
        # Load resume files
        pdf_files = list(Path(resumes_dir).glob("*.pdf"))
        
        if len(pdf_files) < 1:
            raise ValueError("At least 1 resume PDF file required")
        
        # Get JD filename for reference
        jd_files = list(Path(jd_dir).glob("*.pdf"))
        jd_file = str(jd_files[0]) if jd_files else "JD.pdf"
        
        # Preprocess resumes
        parsed_resumes = {}
        for resume_file in pdf_files:
            resume_text = load_text(str(resume_file))
            clean_sentences = preprocess_text(resume_text)
            parsed_resumes[resume_file.name] = clean_sentences
        
        # Generate analysis output PDF
        write_analysis_pdf(
            output_path=str(Path(output_dir) / "analysis_output.pdf"),
            jd_sentences=self.jd_sentences,
            resumes=parsed_resumes
        )
        
        # Evaluate candidates
        jd_embeddings = self.jd_embeddings
        
        candidates_data = []
        xai_reports = {}
        
        for resume_name, resume_sentences in parsed_resumes.items():
            resume_embeddings = self.embedder.encode(resume_sentences)
            
            semantic_matches = compute_semantic_matches(
                jd_sentences=self.jd_sentences,
                jd_embeddings=jd_embeddings,
                resume_sentences=resume_sentences,
                resume_embeddings=resume_embeddings,
                threshold=0.55
            )
            
            # Calculate scores with ML→Python inference
            rfs = combined_role_fit_score(
                semantic_matches, 
                resume_sentences, 
                self.jd_requirements
            )
            css = capability_strength_score(resume_sentences)
            gps = growth_potential_score(resume_sentences)
            dcs = domain_compatibility_score(self.jd_requirements, resume_sentences)
            elc = execution_language_score(self.required_language, resume_sentences)
            
            # Decision
            action = decide_action(rfs, css, gps, dcs, elc)
            explanation = explain_decision(action, rfs, css, gps, dcs, elc)
            composite = calculate_composite_score(rfs, css, gps, dcs, elc)
            
            # XAI explanation
            xai_explanation = generate_xai_explanation(
                candidate_name=resume_name,
                rfs=rfs, css=css, gps=gps, dcs=dcs, elc=elc,
                action=action,
                composite_score=composite,
                semantic_matches=semantic_matches,
                jd_requirements=self.jd_requirements,
                resume_sentences=resume_sentences
            )
            
            xai_reports[resume_name] = xai_explanation
            
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
        
        # Rank candidates
        ranked_candidates = rank_candidates(candidates_data)
        
        # Save XAI report
        with open(Path(output_dir) / "xai_explanations.txt", "w", encoding="utf-8") as f:
            f.write("EXPLAINABLE AI CANDIDATE ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            for candidate in ranked_candidates:
                if candidate['name'] in xai_reports:
                    f.write(xai_reports[candidate['name']])
                    f.write("\n\n")
        
        # Generate ranking PDF
        write_ranking_pdf(
            output_path=str(Path(output_dir) / "candidate_ranking_report.pdf"),
            ranked_candidates=ranked_candidates,
            jd_file=jd_file
        )
        
        # Format response
        summary = {
            'hire': sum(1 for c in ranked_candidates if 'SELECT_FAST_TRACK' in str(c['action'])),
            'interview': sum(1 for c in ranked_candidates if 'INTERVIEW' in str(c['action'])),
            'pool': sum(1 for c in ranked_candidates if 'POOL' in str(c['action'])),
            'reject': sum(1 for c in ranked_candidates if 'REJECT' in str(c['action']))
        }
        
        return {
            "job_description": Path(jd_file).name,
            "total_candidates": len(ranked_candidates),
            "candidates": [
                {
                    "name": c['name'],
                    "scores": {
                        "role_fit": c['rfs'],
                        "capability_strength": c['css'],
                        "growth_potential": c['gps'],
                        "domain_compatibility": c['dcs'],
                        "execution_language": c['elc'],
                        "composite_score": c['composite_score']
                    },
                    "action": str(c['action']).split('.')[-1],
                    "explanation": c['explanation'],
                    "rank": str(c['rank']),
                    "tier": c['tier']
                }
                for c in ranked_candidates
            ],
            "summary": summary
        }
