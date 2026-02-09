from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Agentic Hiring API",
    description="AI-powered recruitment analysis system with explainability",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["analysis"])

@app.on_event("startup")
async def startup_event():
    """Preload model on startup"""
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

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in production
        workers=4,     # Multiple workers
        log_level="info"
    )
