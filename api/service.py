import os
import json
import pickle
from pathlib import Path
from typing import Dict, List
import numpy as np

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
        
        # Persistent storage paths
        self.storage_dir = Path("storage")
        self.storage_dir.mkdir(exist_ok=True)
        self.jd_data_file = self.storage_dir / "jd_data.json"
        self.jd_embeddings_file = self.storage_dir / "jd_embeddings.npy"
    
    def is_model_loaded(self) -> bool:
        return self.embedder is not None
    
    def _ensure_embedder(self):
        if self.embedder is None:
            self.embedder = SemanticEmbedder()
    
    def _save_jd_data(self):
        """Save processed JD data to disk"""
        try:
            # Save text data as JSON
            jd_data = {
                "sentences": self.jd_sentences,
                "requirements": self.jd_requirements
            }
            with open(self.jd_data_file, "w", encoding="utf-8") as f:
                json.dump(jd_data, f, ensure_ascii=False, indent=2)
            
            # Save embeddings as numpy array
            np.save(self.jd_embeddings_file, self.jd_embeddings)
            
            print(f"✅ JD data saved to disk: {self.storage_dir}")
            return True
        except Exception as e:
            print(f"❌ Failed to save JD data: {e}")
            return False
    
    def _load_jd_data(self) -> bool:
        """Load processed JD data from disk"""
        try:
            # Check if files exist
            if not self.jd_data_file.exists() or not self.jd_embeddings_file.exists():
                return False
            
            # Load text data
            with open(self.jd_data_file, "r", encoding="utf-8") as f:
                jd_data = json.load(f)
                self.jd_sentences = jd_data["sentences"]
                self.jd_requirements = jd_data["requirements"]
            
            # Load embeddings
            self.jd_embeddings = np.load(self.jd_embeddings_file)
            
            print(f"✅ JD data loaded from disk: {len(self.jd_requirements)} requirements")
            return True
        except Exception as e:
            print(f"❌ Failed to load JD data: {e}")
            return False
    
    def _clear_jd_data(self):
        """Clear JD data from memory and disk"""
        self.jd_sentences = None
        self.jd_requirements = None
        self.jd_embeddings = None
        
        # Remove files
        if self.jd_data_file.exists():
            self.jd_data_file.unlink()
        if self.jd_embeddings_file.exists():
            self.jd_embeddings_file.unlink()
        
        print("🗑️  JD data cleared")
    
    async def process_jd(self, jd_dir: str):
        """
        Process Job Description and cache results.
        Called when JD is uploaded via POST /upload-jd
        """
        self._ensure_embedder()
        
        # Clear old JD data
        self._clear_jd_data()
        
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
        
        # Save to disk for persistence
        self._save_jd_data()
        
        print(f"✅ JD processed: {len(self.jd_requirements)} requirements extracted")
    
    
    async def analyze_resumes(self, jd_dir: str, resumes_dir: str, output_dir: str) -> Dict:
        """
        Analyze resumes against previously uploaded JD.
        Uses cached JD data from process_jd().
        """
        self._ensure_embedder()
        
        # Try to load JD data from memory, then from disk, then reprocess
        if self.jd_requirements is None or self.jd_embeddings is None:
            print("⚠️  JD not in memory, attempting to load from disk...")
            if not self._load_jd_data():
                print("⚠️  JD not on disk, reprocessing...")
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
