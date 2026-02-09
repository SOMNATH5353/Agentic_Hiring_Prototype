from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict
import os
import uuid
from pathlib import Path
import asyncio

from api.models import AnalysisResponse, UploadResponse, HealthResponse, CandidateResult, CandidateScore
from api.service import AnalysisService

router = APIRouter()
analysis_service = AnalysisService()

# Storage for uploaded files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Add this to track analysis progress
analysis_progress: Dict[str, Dict] = {}

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "model_loaded": analysis_service.is_model_loaded()
    }


@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload job description and resumes.
    At least one JD and one resume required.
    """
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 files required (1 JD + 1 resume)"
        )
    
    # Create session directory
    session_id = str(uuid.uuid4())
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)
    
    uploaded_files = []
    
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files allowed. Got: {file.filename}"
            )
        
        file_path = session_dir / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        uploaded_files.append(file.filename)
    
    return {
        "message": f"Successfully uploaded {len(uploaded_files)} files",
        "job_description_file": None,  # Will be detected in analysis
        "resume_files": uploaded_files,
        "total_files": len(uploaded_files),
        "session_id": session_id  # ← ADD THIS LINE
    }


@router.post("/analyze/{session_id}", response_model=AnalysisResponse)
async def analyze_candidates(session_id: str, background_tasks: BackgroundTasks):
    """
    Analyze uploaded candidates for a session.
    Returns complete evaluation results.
    """
    session_dir = UPLOAD_DIR / session_id
    
    if not session_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    # Initialize progress tracking
    analysis_progress[session_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting analysis..."
    }
    
    try:
        # Update progress
        analysis_progress[session_id] = {
            "status": "processing",
            "progress": 10,
            "message": "Loading files..."
        }
        
        # Run analysis
        results = await analysis_service.analyze_session(str(session_dir), session_id)
        
        # Mark as complete
        analysis_progress[session_id] = {
            "status": "complete",
            "progress": 100,
            "message": "Analysis complete"
        }
        
        # Schedule cleanup in background
        background_tasks.add_task(cleanup_old_sessions, session_id)
        
        return results
    
    except Exception as e:
        analysis_progress[session_id] = {
            "status": "error",
            "progress": 0,
            "message": str(e)
        }
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/progress/{session_id}")
async def get_analysis_progress(session_id: str):
    """Get the progress of ongoing analysis"""
    if session_id not in analysis_progress:
        return {
            "status": "not_started",
            "progress": 0,
            "message": "Analysis not started yet"
        }
    
    return analysis_progress[session_id]


@router.get("/download/{session_id}/ranking-report")
async def download_ranking_report(session_id: str):
    """Download the comprehensive ranking report PDF"""
    output_path = OUTPUT_DIR / session_id / "candidate_ranking_report.pdf"
    
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Ranking report not found. Please run analysis first using POST /analyze/{session_id}"
        )
    
    # Check if file is ready (not being written)
    import time
    max_wait = 30  # 30 seconds max wait
    waited = 0
    while waited < max_wait:
        try:
            # Try to open file to check if it's ready
            with open(output_path, 'rb') as f:
                f.read(1)
            break
        except:
            time.sleep(1)
            waited += 1
    
    return FileResponse(
        path=str(output_path),
        media_type="application/pdf",
        filename=f"ranking_report_{session_id}.pdf",
        headers={
            "Cache-Control": "public, max-age=3600",
            "X-Session-ID": session_id
        }
    )


@router.get("/download/{session_id}/analysis-output")
async def download_analysis_output(session_id: str):
    """Download the sanitized analysis output PDF"""
    output_path = OUTPUT_DIR / session_id / "analysis_output.pdf"
    
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Analysis output not found. Please run analysis first using POST /analyze/{session_id}"
        )
    
    return FileResponse(
        path=str(output_path),
        media_type="application/pdf",
        filename=f"analysis_output_{session_id}.pdf",
        headers={
            "Cache-Control": "public, max-age=3600"
        }
    )


@router.get("/download/{session_id}/xai-report")
async def download_xai_report(session_id: str):
    """Download the XAI explanations text file"""
    output_path = OUTPUT_DIR / session_id / "xai_explanations.txt"
    
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail="XAI report not found. Please run analysis first using POST /analyze/{session_id}"
        )
    
    return FileResponse(
        path=str(output_path),
        media_type="text/plain",
        filename=f"xai_explanations_{session_id}.txt",
        headers={
            "Cache-Control": "public, max-age=3600"
        }
    )


@router.get("/status/{session_id}")
async def get_session_status(session_id: str):
    """Check if analysis is complete and files are ready"""
    session_dir = UPLOAD_DIR / session_id
    output_dir = OUTPUT_DIR / session_id
    
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    status = {
        "session_id": session_id,
        "uploads_ready": session_dir.exists(),
        "analysis_complete": output_dir.exists(),
        "files_available": {}
    }
    
    if output_dir.exists():
        status["files_available"] = {
            "ranking_report": (output_dir / "candidate_ranking_report.pdf").exists(),
            "analysis_output": (output_dir / "analysis_output.pdf").exists(),
            "xai_report": (output_dir / "xai_explanations.txt").exists()
        }
    
    return status


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its files"""
    session_dir = UPLOAD_DIR / session_id
    output_dir = OUTPUT_DIR / session_id
    
    deleted = False
    
    if session_dir.exists():
        import shutil
        shutil.rmtree(session_dir)
        deleted = True
    
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
        deleted = True
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    return {"message": f"Session {session_id} deleted successfully"}


async def cleanup_old_sessions(session_id: str, age_hours: int = 24):
    """Background task to cleanup old sessions"""
    import time
    import shutil
    
    # Wait before cleanup
    time.sleep(3600)  # 1 hour
    
    # In production, implement proper age-based cleanup
    # For now, just a placeholder
    pass
