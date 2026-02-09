# ingestion/loader.py

from pathlib import Path
import pdfplumber
import warnings
import logging

# Suppress FontBBox warnings from pdfplumber/pdfminer
warnings.filterwarnings('ignore', message='.*FontBBox.*')
logging.getLogger('pdfminer').setLevel(logging.ERROR)


def load_text(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    elif path.suffix.lower() == ".pdf":
        return _load_pdf_with_spacing(path)

    else:
        raise ValueError("Unsupported file type.")


def _load_pdf_with_spacing(path: Path) -> str:
    """
    Extract text with proper spacing and line breaks preserved.
    """
    text_blocks = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            # Extract text with layout preserved
            page_text = page.extract_text(layout=False, x_tolerance=2, y_tolerance=3)
            
            if page_text:
                text_blocks.append(page_text)

    # Join pages with double newline
    return "\n\n".join(text_blocks)
