from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import List
import os
import shutil
from pathlib import Path

from api.models import AnalysisResponse, UploadResponse, HealthResponse, JDUploadResponse
from api.service import AnalysisService

router = APIRouter()
analysis_service = AnalysisService()

# Storage directories
TEMP_JD_DIR = Path("temp_jd")
TEMP_JD_DIR.mkdir(exist_ok=True)

TEMP_RESUMES_DIR = Path("temp_resumes")
TEMP_RESUMES_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("temp_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)

# Store JD state in memory (for current session)
jd_state = {
    "uploaded": False,
    "filename": None,
    "processed": False
}


def check_jd_exists() -> bool:
    """Check if JD data exists in persistent storage"""
    jd_data_file = STORAGE_DIR / "jd_data.json"
    jd_embeddings_file = STORAGE_DIR / "jd_embeddings.npy"
    return jd_data_file.exists() and jd_embeddings_file.exists()


def cleanup_all_files():
    """Clean up all temporary files and persistent storage"""
    try:
        for directory in [TEMP_JD_DIR, TEMP_RESUMES_DIR, OUTPUT_DIR, STORAGE_DIR]:
            if directory.exists():
                shutil.rmtree(directory)
                directory.mkdir(exist_ok=True)
    except Exception as e:
        print(f"Cleanup error: {e}")


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "model_loaded": analysis_service.is_model_loaded()
    }


@router.post("/upload-jd", response_model=JDUploadResponse)
async def upload_job_description(file: UploadFile = File(...)):
    """
    Step 1: Upload Job Description PDF
    
    This must be done before uploading resumes.
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files allowed. Got: {file.filename}"
        )
    
    # Clean previous JD
    cleanup_all_files()
    
    # Save JD file
    jd_path = TEMP_JD_DIR / file.filename
    
    with open(jd_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Update JD state
    jd_state["uploaded"] = True
    jd_state["filename"] = file.filename
    jd_state["processed"] = False
    
    # Process JD immediately
    try:
        await analysis_service.process_jd(str(TEMP_JD_DIR))
        jd_state["processed"] = True
        
        return {
            "message": f"Job Description uploaded and processed successfully",
            "filename": file.filename,
            "status": "ready",
            "next_step": "Upload resumes using POST /upload-resumes"
        }
    
    except Exception as e:
        jd_state["uploaded"] = False
        jd_state["processed"] = False
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process JD: {str(e)}"
        )


@router.post("/upload-resumes", response_model=AnalysisResponse)
async def upload_and_analyze_resumes(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Step 2: Upload Resumes and Get Analysis
    
    Requires JD to be uploaded first via POST /upload-jd
    Returns instant analysis against the uploaded JD.
    """
    # Check if JD is uploaded (in memory OR on disk)
    jd_exists = jd_state["uploaded"] and jd_state["processed"] or check_jd_exists()
    
    if not jd_exists:
        raise HTTPException(
            status_code=400,
            detail="Job Description not uploaded. Please upload JD first using POST /upload-jd"
        )
    
    # Validate at least one resume
    if len(files) < 1:
        raise HTTPException(
            status_code=400,
            detail="At least 1 resume file required"
        )
    
    # Clean previous resumes
    if TEMP_RESUMES_DIR.exists():
        shutil.rmtree(TEMP_RESUMES_DIR)
    TEMP_RESUMES_DIR.mkdir(exist_ok=True)
    
    # Save resume files
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files allowed. Got: {file.filename}"
            )
        
        file_path = TEMP_RESUMES_DIR / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    
    try:
        # Run analysis
        results = await analysis_service.analyze_resumes(
            str(TEMP_JD_DIR),
            str(TEMP_RESUMES_DIR),
            str(OUTPUT_DIR)
        )
        
        # Verify files were created
        ranking_pdf = OUTPUT_DIR / "candidate_ranking_report.pdf"
        analysis_pdf = OUTPUT_DIR / "analysis_output.pdf"
        xai_txt = OUTPUT_DIR / "xai_explanations.txt"
        
        print(f"✅ Analysis complete. Files created:")
        print(f"  Ranking PDF: {ranking_pdf.exists()}")
        print(f"  Analysis PDF: {analysis_pdf.exists()}")
        print(f"  XAI TXT: {xai_txt.exists()}")
        
        return results
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/jd-status")
async def get_jd_status():
    """Check if Job Description is uploaded and ready"""
    # Check both memory and persistent storage
    in_memory = jd_state["uploaded"] and jd_state["processed"]
    on_disk = check_jd_exists()
    is_ready = in_memory or on_disk
    
    return {
        "uploaded": jd_state["uploaded"],
        "filename": jd_state["filename"],
        "processed": jd_state["processed"],
        "persisted": on_disk,
        "ready_for_resumes": is_ready
    }


@router.get("/download/ranking-report")
async def download_ranking_report():
    """Download the comprehensive ranking report PDF"""
    output_path = OUTPUT_DIR / "candidate_ranking_report.pdf"
    
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Ranking report not found. Run /upload-resumes first."
        )
    
    return FileResponse(
        path=str(output_path),
        media_type="application/pdf",
        filename="ranking_report.pdf",
        headers={"Cache-Control": "no-cache"}
    )


@router.get("/download/analysis-output")
async def download_analysis_output():
    """Download the sanitized analysis output PDF"""
    output_path = OUTPUT_DIR / "analysis_output.pdf"
    
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Analysis output not found. Run /upload-resumes first."
        )
    
    return FileResponse(
        path=str(output_path),
        media_type="application/pdf",
        filename="analysis_output.pdf",
        headers={"Cache-Control": "no-cache"}
    )


@router.get("/download/xai-report")
async def download_xai_report():
    """Download the XAI explanations text file"""
    output_path = OUTPUT_DIR / "xai_explanations.txt"
    
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail="XAI report not found. Run /upload-resumes first."
        )
    
    return FileResponse(
        path=str(output_path),
        media_type="text/plain",
        filename="xai_explanations.txt",
        headers={"Cache-Control": "no-cache"}
    )


@router.post("/clear")
async def clear_all_data():
    """Clear all uploaded data (JD + Resumes + Outputs)"""
    cleanup_all_files()
    jd_state["uploaded"] = False
    jd_state["filename"] = None
    jd_state["processed"] = False
    
    return {
        "message": "All data cleared successfully",
        "jd_status": "cleared",
        "resumes_status": "cleared"
    }


@router.delete("/clear-jd")
async def clear_job_description():
    """Clear only the Job Description"""
    if TEMP_JD_DIR.exists():
        shutil.rmtree(TEMP_JD_DIR)
        TEMP_JD_DIR.mkdir(exist_ok=True)
    
    jd_state["uploaded"] = False
    jd_state["filename"] = None
    jd_state["processed"] = False
    
    return {
        "message": "Job Description cleared. Upload new JD to continue."
    }


@router.delete("/clear-resumes")
async def clear_resumes():
    """Clear only the Resumes (keeps JD)"""
    if TEMP_RESUMES_DIR.exists():
        shutil.rmtree(TEMP_RESUMES_DIR)
        TEMP_RESUMES_DIR.mkdir(exist_ok=True)
    
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
        OUTPUT_DIR.mkdir(exist_ok=True)
    
    return {
        "message": "Resumes cleared. JD is still active. Upload new resumes to re-analyze."
    }


@router.get("/debug/files")
async def debug_files():
    """Debug endpoint to check file existence"""
    return {
        "jd_state": jd_state,
        
        "jd_dir": str(TEMP_JD_DIR),
        "jd_dir_exists": TEMP_JD_DIR.exists(),
        "jd_files": list(str(f) for f in TEMP_JD_DIR.glob("*")) if TEMP_JD_DIR.exists() else [],
        
        "resumes_dir": str(TEMP_RESUMES_DIR),
        "resumes_dir_exists": TEMP_RESUMES_DIR.exists(),
        "resume_files": list(str(f) for f in TEMP_RESUMES_DIR.glob("*")) if TEMP_RESUMES_DIR.exists() else [],
        
        "output_dir": str(OUTPUT_DIR),
        "output_dir_exists": OUTPUT_DIR.exists(),
        "output_files": list(str(f) for f in OUTPUT_DIR.glob("*")) if OUTPUT_DIR.exists() else [],
        
        "ranking_pdf_exists": (OUTPUT_DIR / "candidate_ranking_report.pdf").exists(),
        "analysis_pdf_exists": (OUTPUT_DIR / "analysis_output.pdf").exists(),
        "xai_txt_exists": (OUTPUT_DIR / "xai_explanations.txt").exists()
    }
