import os
from pathlib import Path

# Environment
ENV = os.getenv("ENV", "development")
IS_PRODUCTION = ENV == "production"

# Directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API Configuration
API_TITLE = "Agentic Hiring API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI-powered recruitment analysis with explainability"

# Model Configuration
DEFAULT_MODEL = "all-MiniLM-L6-v2"
HF_TOKEN = os.getenv("HF_TOKEN", None)

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# File limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES_PER_SESSION = 20

# Session cleanup
SESSION_EXPIRY_HOURS = 24
