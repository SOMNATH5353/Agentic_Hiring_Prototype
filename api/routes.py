from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import List
import os
import shutil
from pathlib import Path

from api.models import AnalysisResponse, UploadResponse, HealthResponse
from api.service import AnalysisService

router = APIRouter()
analysis_service = AnalysisService()

# Single shared directory for temporary processing
TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("temp_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def cleanup_temp_files():
    """Clean up temporary files"""
    try:
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR)
            TEMP_DIR.mkdir(exist_ok=True)
        if OUTPUT_DIR.exists():
            shutil.rmtree(OUTPUT_DIR)
            OUTPUT_DIR.mkdir(exist_ok=True)
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


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_candidates(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload and analyze candidates in one step.
    Upload JD + resumes, get instant analysis.
    
    Minimum: 2 files (1 JD + 1+ resumes)
    """
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 files required (1 JD + 1+ resumes)"
        )
    
    # Clean previous files first
    cleanup_temp_files()
    
    # Save uploaded files
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files allowed. Got: {file.filename}"
            )
        
        file_path = TEMP_DIR / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    
    try:
        # Run analysis - pass OUTPUT_DIR as string
        results = await analysis_service.analyze_files(str(TEMP_DIR), str(OUTPUT_DIR))
        
        # Verify files were created
        ranking_pdf = OUTPUT_DIR / "candidate_ranking_report.pdf"
        analysis_pdf = OUTPUT_DIR / "analysis_output.pdf"
        xai_txt = OUTPUT_DIR / "xai_explanations.txt"
        
        print(f"Files created:")
        print(f"  Ranking PDF: {ranking_pdf.exists()} - {ranking_pdf}")
        print(f"  Analysis PDF: {analysis_pdf.exists()} - {analysis_pdf}")
        print(f"  XAI TXT: {xai_txt.exists()} - {xai_txt}")
        
        # Optional: Schedule cleanup later
        # if background_tasks:
        #     background_tasks.add_task(cleanup_temp_files_delayed, 3600)
        
        return results
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/download/ranking-report")
async def download_ranking_report():
    """Download the comprehensive ranking report PDF"""
    output_path = OUTPUT_DIR / "candidate_ranking_report.pdf"
    
    print(f"Looking for ranking report at: {output_path}")
    print(f"File exists: {output_path.exists()}")
    
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Ranking report not found at {output_path}. Run /analyze first."
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
    
    print(f"Looking for analysis output at: {output_path}")
    print(f"File exists: {output_path.exists()}")
    
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Analysis output not found at {output_path}. Run /analyze first."
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
    
    print(f"Looking for XAI report at: {output_path}")
    print(f"File exists: {output_path.exists()}")
    
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"XAI report not found at {output_path}. Run /analyze first."
        )
    
    return FileResponse(
        path=str(output_path),
        media_type="text/plain",
        filename="xai_explanations.txt",
        headers={"Cache-Control": "no-cache"}
    )


@router.post("/clear")
async def clear_temp_files():
    """Manually clear temporary files"""
    cleanup_temp_files()
    return {"message": "Temporary files cleared successfully"}


@router.get("/debug/files")
async def debug_files():
    """Debug endpoint to check file existence"""
    return {
        "temp_dir": str(TEMP_DIR),
        "temp_dir_exists": TEMP_DIR.exists(),
        "temp_files": list(str(f) for f in TEMP_DIR.glob("*")) if TEMP_DIR.exists() else [],
        
        "output_dir": str(OUTPUT_DIR),
        "output_dir_exists": OUTPUT_DIR.exists(),
        "output_files": list(str(f) for f in OUTPUT_DIR.glob("*")) if OUTPUT_DIR.exists() else [],
        
        "ranking_pdf_exists": (OUTPUT_DIR / "candidate_ranking_report.pdf").exists(),
        "analysis_pdf_exists": (OUTPUT_DIR / "analysis_output.pdf").exists(),
        "xai_txt_exists": (OUTPUT_DIR / "xai_explanations.txt").exists()
    }
