"""
Generate API Documentation PDF with Deployed Render URL
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime


def generate_deployed_api_docs(output_path="Deployed_API_Documentation.pdf"):
    """
    Generate comprehensive API documentation PDF with Render deployment URL
    """
    # Your deployed Render URL
    BASE_URL = "https://agentic-hiring-prototype.onrender.com/api/v1"
    
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
    
    url_style = ParagraphStyle(
        'URLStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#2980b9'),
        fontName='Courier',
        leftIndent=15
    )
    
    # ==================== TITLE PAGE ====================
    content.append(Spacer(1, 1*inch))
    
    content.append(Paragraph("🚀 AGENTIC HIRING API", title_style))
    content.append(Paragraph("Production Deployment Documentation", subtitle_style))
    
    content.append(Spacer(1, 0.3*inch))
    
    # Deployment info
    deploy_data = [
        ['🌐 Base URL:', BASE_URL],
        ['🏢 Hosting:', 'Render Cloud Platform'],
        ['📅 Generated:', datetime.now().strftime('%B %d, %Y at %H:%M UTC')],
        ['📦 Version:', '1.0.0'],
        ['🔧 Framework:', 'FastAPI + Python 3.11'],
        ['🤖 AI Model:', 'Sentence-BERT (MiniLM-L6-v2)'],
        ['🔒 HTTPS:', 'Enabled (Let\'s Encrypt)'],
        ['📊 Status:', 'https://agentic-hiring-prototype.onrender.com/api/v1/']
    ]
    
    deploy_table = Table(deploy_data, colWidths=[2*inch, 4.5*inch])
    deploy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    content.append(deploy_table)
    
    content.append(PageBreak())
    
    # ==================== QUICK START ====================
    content.append(Paragraph("⚡ QUICK START", section_style))
    content.append(Spacer(1, 16))
    
    quickstart_text = f"""
<b>Test the API immediately:</b><br/><br/>

1. <b>Health Check:</b><br/>
   <font face="Courier" size="8">curl {BASE_URL}/</font><br/><br/>

2. <b>Upload Job Description:</b><br/>
   <font face="Courier" size="8">curl -X POST "{BASE_URL}/upload-jd" \\<br/>
   -F "file=@your_jd.pdf"</font><br/><br/>

3. <b>Upload Resumes &amp; Analyze:</b><br/>
   <font face="Courier" size="8">curl -X POST "{BASE_URL}/upload-resumes" \\<br/>
   -F "files=@resume1.pdf" \\<br/>
   -F "files=@resume2.pdf"</font><br/><br/>

4. <b>Download Ranking Report:</b><br/>
   <font face="Courier" size="8">curl -O "{BASE_URL}/download/ranking-report"</font>
"""
    
    content.append(Paragraph(quickstart_text, ParagraphStyle('quickstart', parent=styles['Normal'], fontSize=9, leading=13, leftIndent=10)))
    
    content.append(PageBreak())
    
    # ==================== ALL ENDPOINTS ====================
    content.append(Paragraph("📋 COMPLETE API REFERENCE", section_style))
    content.append(Spacer(1, 20))
    
    endpoints = [
        {
            'num': '1',
            'name': 'Health Check',
            'method': 'GET',
            'path': '/',
            'full_url': f'{BASE_URL}/',
            'description': 'Check if the API server is running and model is loaded.',
            'request': 'None',
            'response': '''{"status": "healthy", "version": "1.0.0", "model_loaded": true}''',
            'status': '200 OK'
        },
        {
            'num': '2',
            'name': 'Upload Job Description',
            'method': 'POST',
            'path': '/upload-jd',
            'full_url': f'{BASE_URL}/upload-jd',
            'description': 'Upload and process a job description PDF. Must be done before uploading resumes.',
            'request': 'Content-Type: multipart/form-data\nfield: "file" (PDF)',
            'response': '''{"message": "Job Description uploaded successfully", "filename": "jd.pdf", "status": "ready", "next_step": "Upload resumes"}''',
            'status': '200 OK | 400 Bad Request'
        },
        {
            'num': '3',
            'name': 'Check JD Status',
            'method': 'GET',
            'path': '/jd-status',
            'full_url': f'{BASE_URL}/jd-status',
            'description': 'Check if job description is uploaded and ready for resume analysis.',
            'request': 'None',
            'response': '''{"uploaded": true, "filename": "jd.pdf", "processed": true, "ready_for_resumes": true}''',
            'status': '200 OK'
        },
        {
            'num': '4',
            'name': 'Upload Resumes & Analyze',
            'method': 'POST',
            'path': '/upload-resumes',
            'full_url': f'{BASE_URL}/upload-resumes',
            'description': 'Upload multiple resume PDFs and get instant AI-powered analysis with rankings, scores, and recommendations.',
            'request': 'Content-Type: multipart/form-data\nfield: "files" (multiple PDFs)',
            'response': '''{"job_description": "jd.pdf", "total_candidates": 3, "candidates": [...], "summary": {"hire": 1, "interview": 2, "pool": 0, "reject": 0}}''',
            'status': '200 OK | 400 Bad Request'
        },
        {
            'num': '5',
            'name': 'Download Ranking Report',
            'method': 'GET',
            'path': '/download/ranking-report',
            'full_url': f'{BASE_URL}/download/ranking-report',
            'description': 'Download comprehensive PDF report with candidate rankings, detailed scores, tiers, and recommendations.',
            'request': 'None',
            'response': 'PDF File (ranking_report.pdf)',
            'status': '200 OK | 404 Not Found'
        },
        {
            'num': '6',
            'name': 'Download Analysis Output',
            'method': 'GET',
            'path': '/download/analysis-output',
            'full_url': f'{BASE_URL}/download/analysis-output',
            'description': 'Download sanitized analysis PDF with PII-redacted job description and resumes.',
            'request': 'None',
            'response': 'PDF File (analysis_output.pdf)',
            'status': '200 OK | 404 Not Found'
        },
        {
            'num': '7',
            'name': 'Download XAI Report',
            'method': 'GET',
            'path': '/download/xai-report',
            'full_url': f'{BASE_URL}/download/xai-report',
            'description': 'Download explainable AI analysis with feature attribution, semantic matches, skill gaps, and counterfactuals.',
            'request': 'None',
            'response': 'Text File (xai_explanations.txt)',
            'status': '200 OK | 404 Not Found'
        },
        {
            'num': '8',
            'name': 'Clear All Data',
            'method': 'POST',
            'path': '/clear',
            'full_url': f'{BASE_URL}/clear',
            'description': 'Clear all uploaded data including job description, resumes, and generated reports.',
            'request': 'None',
            'response': '''{"message": "All data cleared successfully"}''',
            'status': '200 OK'
        },
        {
            'num': '9',
            'name': 'Clear Job Description Only',
            'method': 'DELETE',
            'path': '/clear-jd',
            'full_url': f'{BASE_URL}/clear-jd',
            'description': 'Clear only the job description while keeping resumes.',
            'request': 'None',
            'response': '''{"message": "Job Description cleared"}''',
            'status': '200 OK'
        },
        {
            'num': '10',
            'name': 'Clear Resumes Only',
            'method': 'DELETE',
            'path': '/clear-resumes',
            'full_url': f'{BASE_URL}/clear-resumes',
            'description': 'Clear only resumes while keeping the job description active.',
            'request': 'None',
            'response': '''{"message": "Resumes cleared. JD still active"}''',
            'status': '200 OK'
        },
        {
            'num': '11',
            'name': 'Debug File Status',
            'method': 'GET',
            'path': '/debug/files',
            'full_url': f'{BASE_URL}/debug/files',
            'description': 'Debug endpoint to check file existence and status (development/testing only).',
            'request': 'None',
            'response': '''{"jd_state": {...}, "jd_files": [...], "resume_files": [...], "output_files": [...]}''',
            'status': '200 OK'
        }
    ]
    
    for endpoint in endpoints:
        # Endpoint header
        method_color = {
            'GET': '#27ae60',
            'POST': '#3498db',
            'DELETE': '#e74c3c'
        }.get(endpoint['method'], '#95a5a6')
        
        header_text = f"<b>{endpoint['num']}. {endpoint['name']}</b>"
        content.append(Paragraph(header_text, ParagraphStyle('epheader', parent=section_style, fontSize=13)))
        content.append(Spacer(1, 8))
        
        # Method and path
        method_data = [[
            Paragraph(f"<b>{endpoint['method']}</b>", ParagraphStyle('m', parent=styles['Normal'], textColor=colors.HexColor(method_color), fontSize=10, fontName='Helvetica-Bold')),
            Paragraph(endpoint['path'], ParagraphStyle('p', parent=styles['Normal'], fontSize=10, fontName='Courier'))
        ]]
        
        method_table = Table(method_data, colWidths=[1*inch, 5*inch])
        method_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#ecf0f1')),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        content.append(method_table)
        content.append(Spacer(1, 8))
        
        # Full URL
        content.append(Paragraph("<b>Full URL:</b>", styles['Normal']))
        content.append(Paragraph(endpoint['full_url'], url_style))
        content.append(Spacer(1, 8))
        
        # Description
        content.append(Paragraph(f"<b>Description:</b><br/>{endpoint['description']}", ParagraphStyle('d', parent=styles['Normal'], fontSize=9, leading=13)))
        content.append(Spacer(1, 8))
        
        # Request
        content.append(Paragraph("<b>Request:</b>", styles['Normal']))
        content.append(Paragraph(f"<font face='Courier' size='8'>{endpoint['request']}</font>", ParagraphStyle('req', parent=styles['Normal'], leftIndent=15, fontSize=8)))
        content.append(Spacer(1, 8))
        
        # Response
        content.append(Paragraph("<b>Response:</b>", styles['Normal']))
        content.append(Paragraph(f"<font face='Courier' size='7'>{endpoint['response']}</font>", ParagraphStyle('res', parent=styles['Normal'], leftIndent=15, fontSize=7, leading=9)))
        content.append(Spacer(1, 8))
        
        # Status
        content.append(Paragraph(f"<b>Status:</b> <font face='Courier' size='9'>{endpoint['status']}</font>", styles['Normal']))
        
        content.append(Spacer(1, 16))
        
        if int(endpoint['num']) % 3 == 0 and int(endpoint['num']) < 11:
            content.append(PageBreak())
    
    # Build PDF
    doc.build(content)
    print(f"✅ Deployed API documentation generated: {output_path}")
    print(f"📍 Base URL: {BASE_URL}")


if __name__ == "__main__":
    generate_deployed_api_docs()
