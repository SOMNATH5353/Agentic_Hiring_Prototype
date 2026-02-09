"""
Generate API Documentation PDF
Run this script to create comprehensive API documentation.
"""

from utils.api_documentation_pdf import generate_api_documentation_pdf

if __name__ == "__main__":
    print("🔧 Generating API Documentation PDF...")
    generate_api_documentation_pdf("API_Documentation.pdf")
    print("✅ Done! Check 'API_Documentation.pdf' in the project root.")
