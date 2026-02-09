from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime


def generate_api_documentation_pdf(output_path="API_Documentation.pdf"):
    """
    Generate comprehensive API documentation PDF
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    styles = getSampleStyleSheet()
    content = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#6c757d'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        spaceAfter=20
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.white,
        backColor=colors.HexColor('#2c3e50'),
        borderPadding=10,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    endpoint_style = ParagraphStyle(
        'Endpoint',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#2980b9'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    # ==================== TITLE PAGE ====================
    content.append(Spacer(1, 1*inch))
    
    # Title
    content.append(Paragraph("🚀 AGENTIC HIRING API", title_style))
    content.append(Paragraph(
        "RESTful API Documentation", 
        subtitle_style
    ))
    
    content.append(Spacer(1, 0.3*inch))
    
    # Info box
    info_data = [
        ['📦 Version:', '1.0.0'],
        ['🌐 Base URL:', 'http://localhost:8000/api/v1'],
        ['📅 Generated:', datetime.now().strftime('%B %d, %Y')],
        ['🔧 Framework:', 'FastAPI + Python 3.11+'],
        ['🤖 AI Model:', 'Sentence-BERT (all-MiniLM-L6-v2)']
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    content.append(info_table)
    
    content.append(PageBreak())
    
    # ==================== API ENDPOINTS ====================
    
    # API Endpoints data
    endpoints = [
        {
            'name': 'Health Check',
            'method': 'GET',
            'path': '/',
            'description': 'Check if the API server is running and model is loaded.',
            'request': 'No body required',
            'response': '''
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true
}''',
            'status_codes': '200: Success'
        },
        {
            'name': 'Analyze Candidates',
            'method': 'POST',
            'path': '/analyze',
            'description': 'Upload job description + resumes and get instant AI analysis with rankings, scores, and recommendations.',
            'request': '''
Content-Type: multipart/form-data

files: [File] (minimum 2 PDFs)
- 1 Job Description PDF
- 1+ Resume PDFs''',
            'response': '''
{
  "job_description": "JD.pdf",
  "total_candidates": 3,
  "candidates": [
    {
      "name": "candidate.pdf",
      "scores": {
        "role_fit": 0.75,
        "capability_strength": 0.68,
        "growth_potential": 0.85,
        "domain_compatibility": 0.92,
        "execution_language": 1,
        "composite_score": 0.78
      },
      "action": "SELECT_FAST_TRACK",
      "explanation": "Strong candidate...",
      "rank": "1",
      "tier": "Excellent"
    }
  ],
  "summary": {
    "hire": 1,
    "interview": 1,
    "pool": 1,
    "reject": 0
  }
}''',
            'status_codes': '200: Success\n400: Invalid files\n500: Analysis failed'
        },
        {
            'name': 'Download Ranking Report',
            'method': 'GET',
            'path': '/download/ranking-report',
            'description': 'Download comprehensive PDF report with candidate rankings, detailed scores, and recommendations.',
            'request': 'No body required',
            'response': 'PDF file (ranking_report.pdf)',
            'status_codes': '200: Success\n404: Report not found (run /analyze first)'
        },
        {
            'name': 'Download Analysis Output',
            'method': 'GET',
            'path': '/download/analysis-output',
            'description': 'Download sanitized analysis PDF with PII-redacted job description and resumes.',
            'request': 'No body required',
            'response': 'PDF file (analysis_output.pdf)',
            'status_codes': '200: Success\n404: Output not found'
        },
        {
            'name': 'Download XAI Report',
            'method': 'GET',
            'path': '/download/xai-report',
            'description': 'Download explainable AI analysis text file with feature attribution, semantic matches, skill gaps, and counterfactuals.',
            'request': 'No body required',
            'response': 'Text file (xai_explanations.txt)',
            'status_codes': '200: Success\n404: Report not found'
        },
        {
            'name': 'Clear Temp Files',
            'method': 'POST',
            'path': '/clear',
            'description': 'Manually clear temporary uploaded files and generated outputs.',
            'request': 'No body required',
            'response': '''
{
  "message": "Temporary files cleared successfully"
}''',
            'status_codes': '200: Success'
        },
        {
            'name': 'Debug Files',
            'method': 'GET',
            'path': '/debug/files',
            'description': 'Debug endpoint to check file existence and status (development only).',
            'request': 'No body required',
            'response': '''
{
  "temp_dir": "temp_uploads/",
  "output_dir": "temp_outputs/",
  "ranking_pdf_exists": true,
  "analysis_pdf_exists": true,
  "xai_txt_exists": true
}''',
            'status_codes': '200: Success'
        }
    ]
    
    # Generate endpoint documentation
    for idx, endpoint in enumerate(endpoints, 1):
        # Section header
        method_color = {
            'GET': '#27ae60',
            'POST': '#3498db',
            'DELETE': '#e74c3c'
        }.get(endpoint['method'], '#95a5a6')
        
        # Endpoint title
        endpoint_header = f"{idx}. {endpoint['name']}"
        content.append(Paragraph(endpoint_header, section_style))
        content.append(Spacer(1, 10))
        
        # Method and path table
        method_data = [[
            Paragraph(f"<b>{endpoint['method']}</b>", ParagraphStyle('method', parent=styles['Normal'], textColor=colors.HexColor(method_color), fontSize=11)),
            Paragraph(f"<font color='#2c3e50'>{endpoint['path']}</font>", styles['Normal'])
        ]]
        
        method_table = Table(method_data, colWidths=[1*inch, 5*inch])
        method_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#ecf0f1')),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        content.append(method_table)
        content.append(Spacer(1, 10))
        
        # Description
        desc_style = ParagraphStyle('desc', parent=styles['Normal'], fontSize=10, leading=14)
        content.append(Paragraph(f"<b>Description:</b><br/>{endpoint['description']}", desc_style))
        content.append(Spacer(1, 10))
        
        # Request
        content.append(Paragraph("<b>Request:</b>", styles['Normal']))
        request_para = Paragraph(
            f"<font face='Courier' size='9'>{endpoint['request'].replace(chr(10), '<br/>')}</font>",
            ParagraphStyle('request', parent=styles['Normal'], leftIndent=15, fontSize=9, leading=12)
        )
        content.append(request_para)
        content.append(Spacer(1, 10))
        
        # Response
        content.append(Paragraph("<b>Response:</b>", styles['Normal']))
        response_para = Paragraph(
            f"<font face='Courier' size='8'>{endpoint['response'].replace(chr(10), '<br/>')}</font>",
            ParagraphStyle('response', parent=styles['Normal'], leftIndent=15, fontSize=8, leading=10)
        )
        content.append(response_para)
        content.append(Spacer(1, 10))
        
        # Status codes
        content.append(Paragraph("<b>Status Codes:</b>", styles['Normal']))
        status_para = Paragraph(
            f"<font face='Courier' size='9'>{endpoint['status_codes'].replace(chr(10), '<br/>')}</font>",
            ParagraphStyle('status', parent=styles['Normal'], leftIndent=15, fontSize=9)
        )
        content.append(status_para)
        content.append(Spacer(1, 20))
        
        # Separator
        if idx < len(endpoints):
            separator = Table([['']], colWidths=[6.5*inch], rowHeights=[0.03*inch])
            separator.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1'))
            ]))
            content.append(separator)
            content.append(Spacer(1, 20))
    
    # ==================== USAGE EXAMPLES ====================
    content.append(PageBreak())
    content.append(Paragraph("💡 USAGE EXAMPLES", section_style))
    content.append(Spacer(1, 16))
    
    # Python example
    content.append(Paragraph("<b>Python Example:</b>", endpoint_style))
    python_code = '''
import requests

# 1. Analyze candidates
files = [
    ('files', open('jd.pdf', 'rb')),
    ('files', open('resume1.pdf', 'rb')),
    ('files', open('resume2.pdf', 'rb'))
]
response = requests.post(
    'http://localhost:8000/api/v1/analyze',
    files=files
)
results = response.json()

# 2. Download reports
ranking_pdf = requests.get(
    'http://localhost:8000/api/v1/download/ranking-report'
)
with open('ranking.pdf', 'wb') as f:
    f.write(ranking_pdf.content)
'''
    content.append(Paragraph(
        f"<font face='Courier' size='8'>{python_code}</font>",
        ParagraphStyle('code', parent=styles['Normal'], leftIndent=15, fontSize=8, leading=11)
    ))
    
    content.append(Spacer(1, 20))
    
    # cURL example
    content.append(Paragraph("<b>cURL Example:</b>", endpoint_style))
    curl_code = '''
# Analyze
curl -X POST "http://localhost:8000/api/v1/analyze" \\
  -F "files=@jd.pdf" \\
  -F "files=@resume1.pdf" \\
  -F "files=@resume2.pdf"

# Download ranking report
curl -O "http://localhost:8000/api/v1/download/ranking-report"
'''
    content.append(Paragraph(
        f"<font face='Courier' size='8'>{curl_code}</font>",
        ParagraphStyle('code', parent=styles['Normal'], leftIndent=15, fontSize=8, leading=11)
    ))
    
    # Build PDF
    doc.build(content)
    print(f"✅ API documentation generated: {output_path}")


if __name__ == "__main__":
    generate_api_documentation_pdf()
