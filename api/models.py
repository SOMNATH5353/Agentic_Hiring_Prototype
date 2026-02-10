from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
from enum import Enum


class CandidateScore(BaseModel):
    """Individual candidate scores"""
    role_fit: float = Field(..., ge=0, le=1, description="Role Fit Score")
    capability_strength: float = Field(..., ge=0, le=1)
    growth_potential: float = Field(..., ge=0, le=1)
    domain_compatibility: float = Field(..., ge=0, le=1)
    execution_language: int = Field(..., ge=0, le=1)
    composite_score: float = Field(..., ge=0, le=1)


class CandidateResult(BaseModel):
    """Complete candidate evaluation result"""
    name: str
    scores: CandidateScore
    action: str
    explanation: str
    rank: Optional[str] = None
    tier: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    job_description: str
    total_candidates: int
    candidates: List[CandidateResult]
    summary: Dict[str, int]


class UploadResponse(BaseModel):
    """File upload response"""
    message: str
    total_files: int


class HealthResponse(BaseModel):
    """Health check response"""
    model_config = ConfigDict(protected_namespaces=())  # Allow model_ prefix
    
    status: str
    version: str
    model_loaded: bool  # This was causing the warning


class JDUploadResponse(BaseModel):
    """Job Description upload response"""
    message: str
    filename: str
    status: str
    next_step: str
