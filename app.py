from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime

from api.routes import router
from config import (
    API_TITLE, API_VERSION, API_DESCRIPTION,
    ALLOWED_ORIGINS, IS_PRODUCTION
)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs" if not IS_PRODUCTION else None,  # Disable docs in production if needed
    redoc_url="/redoc" if not IS_PRODUCTION else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["analysis"])

@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests for monitoring"""
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    
    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    
    return response

@app.on_event("startup")
async def startup_event():
    """Preload model on startup for faster first request"""
    if IS_PRODUCTION:
        from api.service import AnalysisService
        service = AnalysisService()
        service._ensure_embedder()
        print("✅ Model loaded and ready!")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic Hiring API",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/api/v1/"
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=not IS_PRODUCTION,
        log_level="info"
    )
