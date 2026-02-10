"""
Generate Technical Documentation PDF
Complete tech stack, architecture, and workflow documentation
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics import renderPDF
from datetime import datetime
import os


def create_architecture_diagram():
    """Create architecture diagram using ReportLab graphics"""
    d = Drawing(500, 400)
    
    # Colors
    blue = colors.HexColor('#3498db')
    green = colors.HexColor('#27ae60')
    orange = colors.HexColor('#e67e22')
    purple = colors.HexColor('#9b59b6')
    red = colors.HexColor('#e74c3c')
    
    # Client Layer
    d.add(Rect(50, 350, 120, 40, fillColor=blue, strokeColor=colors.black, strokeWidth=2))
    d.add(String(110, 370, "Client", textAnchor="middle", fontSize=12, fillColor=colors.white))
    d.add(String(110, 355, "(Web/Mobile)", textAnchor="middle", fontSize=9, fillColor=colors.white))
    
    # API Gateway
    d.add(Rect(200, 350, 120, 40, fillColor=green, strokeColor=colors.black, strokeWidth=2))
    d.add(String(260, 370, "FastAPI", textAnchor="middle", fontSize=12, fillColor=colors.white))
    d.add(String(260, 355, "REST API", textAnchor="middle", fontSize=9, fillColor=colors.white))
    
    # Processing Layer
    d.add(Rect(50, 250, 100, 60, fillColor=orange, strokeColor=colors.black, strokeWidth=2))
    d.add(String(100, 280, "Ingestion", textAnchor="middle", fontSize=10, fillColor=colors.white))
    d.add(String(100, 265, "PDF Parser", textAnchor="middle", fontSize=8, fillColor=colors.white))
    
    d.add(Rect(170, 250, 100, 60, fillColor=orange, strokeColor=colors.black, strokeWidth=2))
    d.add(String(220, 280, "Semantic", textAnchor="middle", fontSize=10, fillColor=colors.white))
    d.add(String(220, 265, "Embeddings", textAnchor="middle", fontSize=8, fillColor=colors.white))
    
    d.add(Rect(290, 250, 100, 60, fillColor=orange, strokeColor=colors.black, strokeWidth=2))
    d.add(String(340, 280, "Agent", textAnchor="middle", fontSize=10, fillColor=colors.white))
    d.add(String(340, 265, "Decision", textAnchor="middle", fontSize=8, fillColor=colors.white))
    
    # AI/ML Layer
    d.add(Rect(100, 150, 130, 60, fillColor=purple, strokeColor=colors.black, strokeWidth=2))
    d.add(String(165, 185, "Sentence-BERT", textAnchor="middle", fontSize=10, fillColor=colors.white))
    d.add(String(165, 170, "MiniLM-L6-v2", textAnchor="middle", fontSize=8, fillColor=colors.white))
    d.add(String(165, 155, "(384-dim)", textAnchor="middle", fontSize=8, fillColor=colors.white))
    
    d.add(Rect(250, 150, 130, 60, fillColor=purple, strokeColor=colors.black, strokeWidth=2))
    d.add(String(315, 185, "XAI Engine", textAnchor="middle", fontSize=10, fillColor=colors.white))
    d.add(String(315, 170, "SHAP-like", textAnchor="middle", fontSize=8, fillColor=colors.white))
    d.add(String(315, 155, "Explainability", textAnchor="middle", fontSize=8, fillColor=colors.white))
    
    # Storage/Output
    d.add(Rect(150, 50, 200, 60, fillColor=red, strokeColor=colors.black, strokeWidth=2))
    d.add(String(250, 85, "Output Generation", textAnchor="middle", fontSize=10, fillColor=colors.white))
    d.add(String(250, 70, "PDF Reports | Rankings", textAnchor="middle", fontSize=8, fillColor=colors.white))
    d.add(String(250, 55, "XAI Explanations", textAnchor="middle", fontSize=8, fillColor=colors.white))
    
    # Arrows
    # Client to API
    d.add(Line(170, 370, 200, 370, strokeWidth=2, strokeColor=colors.black))
    d.add(Circle(195, 370, 3, fillColor=colors.black))
    
    # API to Processing
    d.add(Line(100, 350, 100, 310, strokeWidth=2, strokeColor=colors.black))
    d.add(Line(220, 350, 220, 310, strokeWidth=2, strokeColor=colors.black))
    d.add(Line(340, 350, 340, 310, strokeWidth=2, strokeColor=colors.black))
    
    # Processing to ML
    d.add(Line(165, 250, 165, 210, strokeWidth=2, strokeColor=colors.black))
    d.add(Line(315, 250, 315, 210, strokeWidth=2, strokeColor=colors.black))
    
    # ML to Output
    d.add(Line(165, 150, 200, 110, strokeWidth=2, strokeColor=colors.black))
    d.add(Line(315, 150, 300, 110, strokeWidth=2, strokeColor=colors.black))
    
    return d


def generate_technical_docs(output_path="Technical_Documentation.pdf"):
    """Generate comprehensive technical documentation"""
    
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
        fontSize=28,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
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
    
    # ==================== TITLE PAGE ====================
    content.append(Spacer(1, 1*inch))
    content.append(Paragraph("🔧 AGENTIC HIRING SYSTEM", title_style))
    content.append(Paragraph("Technical Architecture & Stack Documentation", 
                            ParagraphStyle('sub', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.HexColor('#6c757d'))))
    content.append(Spacer(1, 0.5*inch))
    
    # Project info
    info_data = [
        ['Project:', 'Agentic Hiring Prototype'],
        ['Version:', '1.0.0'],
        ['Repository:', 'github.com/SOMNATH5353/Agentic_Hiring_Prototype'],
        ['Deployment:', 'https://agentic-hiring-prototype.onrender.com'],
        ['Generated:', datetime.now().strftime('%B %d, %Y')],
        ['Language:', 'Python 3.11+'],
        ['License:', 'MIT']
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    content.append(info_table)
    
    content.append(PageBreak())
    
    # ==================== TECH STACK ====================
    content.append(Paragraph("📚 TECHNOLOGY STACK", section_style))
    content.append(Spacer(1, 16))
    
    tech_stack = [
        ['Category', 'Technology', 'Version', 'Purpose'],
        ['Backend Framework', 'FastAPI', '0.109.0', 'REST API server with async support'],
        ['Server', 'Uvicorn', '0.27.0', 'ASGI server for production'],
        ['Language', 'Python', '3.11+', 'Core programming language'],
        ['', '', '', ''],
        ['AI/ML', 'Sentence-BERT', '2.2.2', 'Semantic text embeddings'],
        ['', 'PyTorch', '2.1.2', 'Deep learning framework (CPU)'],
        ['', 'Scikit-learn', '1.3.2', 'ML utilities & cosine similarity'],
        ['', 'NumPy', '1.24.3', 'Numerical computations'],
        ['', '', '', ''],
        ['NLP Model', 'all-MiniLM-L6-v2', '-', '384-dim embeddings, 80M params'],
        ['', '', '', ''],
        ['PDF Processing', 'pdfplumber', '0.10.3', 'PDF text extraction'],
        ['', 'ReportLab', '4.0.7', 'PDF report generation'],
        ['', '', '', ''],
        ['Data Validation', 'Pydantic', '2.5.3', 'Request/response validation'],
        ['', '', '', ''],
        ['Deployment', 'Render', '-', 'Cloud hosting platform'],
        ['', 'Docker', '-', 'Containerization (optional)'],
        ['', '', '', ''],
        ['Version Control', 'Git/GitHub', '-', 'Source code management'],
        ['', '', '', ''],
        ['Security', 'python-dotenv', '1.0.0', 'Environment variable management'],
        ['', 'HTTPS', '-', 'Encrypted communication'],
        ['', '', '', ''],
        ['File Handling', 'python-multipart', '0.0.9', 'Multipart form data'],
        ['', 'aiofiles', '23.2.1', 'Async file operations']
    ]
    
    tech_table = Table(tech_stack, colWidths=[1.5*inch, 1.8*inch, 1*inch, 2.2*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8)
    ]))
    content.append(tech_table)
    
    content.append(PageBreak())
    
    # ==================== ARCHITECTURE DIAGRAM ====================
    content.append(Paragraph("🏗️ SYSTEM ARCHITECTURE", section_style))
    content.append(Spacer(1, 16))
    
    # Add architecture diagram
    diagram = create_architecture_diagram()
    content.append(diagram)
    content.append(Spacer(1, 20))
    
    arch_desc = """
<b>Architecture Overview:</b><br/><br/>

<b>1. Client Layer:</b> Web/mobile applications interact via REST API<br/>
<b>2. API Gateway:</b> FastAPI handles requests, validation, and routing<br/>
<b>3. Processing Layer:</b><br/>
   • <b>Ingestion:</b> PDF parsing, text extraction, PII redaction<br/>
   • <b>Semantic:</b> Text embeddings using Sentence-BERT<br/>
   • <b>Agent:</b> Decision-making with explainable scoring<br/>
<b>4. AI/ML Layer:</b><br/>
   • <b>Sentence-BERT:</b> 384-dimensional semantic embeddings<br/>
   • <b>XAI Engine:</b> SHAP-like feature attribution<br/>
<b>5. Output Layer:</b> PDF reports, rankings, XAI explanations
"""
    content.append(Paragraph(arch_desc, ParagraphStyle('desc', parent=styles['Normal'], fontSize=9, leading=13)))
    
    content.append(PageBreak())
    
    # ==================== PROJECT STRUCTURE ====================
    content.append(Paragraph("📁 PROJECT STRUCTURE", section_style))
    content.append(Spacer(1, 16))
    
    structure_text = """
<font face="Courier" size="8">
Agentic_hiring/<br/>
├── api/<br/>
│   ├── __init__.py<br/>
│   ├── models.py          # Pydantic request/response models<br/>
│   ├── routes.py          # FastAPI endpoints (11 routes)<br/>
│   └── service.py         # Business logic layer<br/>
├── agent_policy/<br/>
│   ├── explanation.py     # Decision explanations<br/>
│   ├── policy.py          # Decision rules & AgentAction enum<br/>
│   ├── ranking.py         # Candidate ranking with tiebreakers<br/>
│   └── scores.py          # 5 scoring functions (RFS, CSS, GPS, DCS, ELC)<br/>
├── explainability/<br/>
│   ├── feature_importance.py  # SHAP-like attributions<br/>
│   └── xai_report.py          # Comprehensive XAI reports<br/>
├── ingestion/<br/>
│   ├── loader.py          # PDF text extraction<br/>
│   └── preprocess.py      # PII redaction & text cleaning<br/>
├── ontology/<br/>
│   └── jd_requirements.py # JD requirement extraction<br/>
├── semantic/<br/>
│   ├── embedder.py        # Sentence-BERT wrapper<br/>
│   └── similarity.py      # Cosine similarity matching<br/>
├── utils/<br/>
│   ├── pdf_writer.py             # Analysis output PDF<br/>
│   ├── ranking_pdf_writer.py     # Ranking report PDF<br/>
│   └── api_documentation_pdf.py  # API docs generator<br/>
├── data/                  # Input PDFs (JD + resumes)<br/>
├── temp_jd/              # Temporary JD storage<br/>
├── temp_resumes/         # Temporary resume storage<br/>
├── temp_outputs/         # Generated reports<br/>
├── app.py                # FastAPI application entry<br/>
├── main.py               # CLI version<br/>
├── config.py             # Configuration settings<br/>
├── requirements.txt      # Python dependencies<br/>
├── Dockerfile           # Docker containerization<br/>
├── .env                 # Environment variables (gitignored)<br/>
├── .gitignore           # Git ignore rules<br/>
└── README.md            # Project documentation
</font>
"""
    content.append(Paragraph(structure_text, styles['Normal']))
    
    content.append(PageBreak())
    
    # ==================== WORKFLOW ====================
    content.append(Paragraph("🔄 SYSTEM WORKFLOW", section_style))
    content.append(Spacer(1, 16))
    
    workflow_steps = [
        ['Step', 'Process', 'Technology', 'Output'],
        ['1', 'Upload JD PDF', 'FastAPI + pdfplumber', 'Text extracted'],
        ['2', 'PII Redaction', 'Regex patterns', 'Anonymized text'],
        ['3', 'Requirement Extraction', 'NLP heuristics', 'Key requirements list'],
        ['4', 'Generate Embeddings', 'Sentence-BERT (MiniLM)', '384-dim vectors'],
        ['5', 'Upload Resumes', 'FastAPI + pdfplumber', 'Multiple PDFs'],
        ['6', 'Resume Processing', 'Text cleaning + PII removal', 'Clean text'],
        ['7', 'Semantic Matching', 'Cosine similarity', 'Match scores (0-1)'],
        ['8', 'Score Calculation', '5 metrics (RFS, CSS, GPS, DCS, ELC)', 'Individual scores'],
        ['9', 'Composite Scoring', 'Weighted average (35%, 25%, 20%, 15%, 5%)', 'Final score'],
        ['10', 'Agent Decision', 'Rule-based policy', 'HIRE/INTERVIEW/POOL/REJECT'],
        ['11', 'XAI Generation', 'Feature attribution + counterfactuals', 'Explanations'],
        ['12', 'Ranking', 'Composite score + tiebreakers', 'Ranked list'],
        ['13', 'Report Generation', 'ReportLab PDF', '3 PDF reports + 1 TXT']
    ]
    
    workflow_table = Table(workflow_steps, colWidths=[0.6*inch, 1.5*inch, 2*inch, 2.4*inch])
    workflow_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
    ]))
    content.append(workflow_table)
    
    content.append(PageBreak())
    
    # ==================== XAI ALGORITHMS ====================
    content.append(Paragraph("🧠 EXPLAINABLE AI ALGORITHMS", section_style))
    content.append(Spacer(1, 16))
    
    xai_algorithms = [
        ['Algorithm', 'Inspiration', 'Implementation', 'Purpose'],
        ['Additive Feature Attribution', 'SHAP (Lundberg 2017)', 'Weighted linear sum', 'Show metric contributions'],
        ['Attention-Based Matching', 'Transformer attention', 'Cosine similarity on embeddings', 'Highlight matching skills'],
        ['Waterfall Analysis', 'LIME (Ribeiro 2016)', 'Sequential decomposition', 'Cumulative score impact'],
       ['Counterfactual Reasoning', 'Wachter et al. 2017', 'Minimal perturbation', '"What-if" scenarios'],
        ['Skill Gap Analysis', 'Set theory', 'Set difference', 'Identify missing skills'],
        ['Confidence Scoring', 'Ensemble methods', 'Score variance', 'Decision reliability'],
        ['Rule-Based Transparency', 'N/A', 'Explicit if-else logic', 'Full auditability']
    ]
    
    xai_table = Table(xai_algorithms, colWidths=[1.8*inch, 1.5*inch, 1.5*inch, 1.7*inch])
    xai_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
    ]))
    content.append(xai_table)
    
    content.append(Spacer(1, 16))
    
    # ==================== SCORING METRICS ====================
    content.append(Paragraph("📊 SCORING METRICS", section_style))
    content.append(Spacer(1, 16))
    
    metrics_text = """
<b>1. Role Fit Score (RFS) - 35% weight</b><br/>
   • Semantic similarity between JD requirements and resume<br/>
   • Uses cosine similarity on 384-dim embeddings<br/>
   • Threshold: 0.55 for matches<br/>
   • Includes ML→Python skill inference<br/><br/>

<b>2. Domain Compatibility Score (DCS) - 25% weight</b><br/>
   • Technical stack alignment<br/>
   • Keyword matching by category (Python, ML, Data, Web)<br/>
   • Penalties for wrong primary language<br/><br/>

<b>3. Capability Strength Score (CSS) - 20% weight</b><br/>
   • Experience indicators (expert, senior, years, projects)<br/>
   • Normalized by resume length<br/><br/>

<b>4. Execution Language Score (ELC) - 15% weight</b><br/>
   • Binary check for required programming language<br/>
   • Accepts ML/DS as Python equivalent<br/><br/>

<b>5. Growth Potential Score (GPS) - 5% weight</b><br/>
   • Learning indicators (certifications, courses, bootcamps)<br/>
   • Forward-looking assessment<br/><br/>

<b>Composite Score = Σ(score_i × weight_i)</b>
"""
    content.append(Paragraph(metrics_text, ParagraphStyle('metrics', parent=styles['Normal'], fontSize=9, leading=13)))
    
    content.append(PageBreak())
    
    # ==================== API ENDPOINTS ====================
    content.append(Paragraph("🌐 API ENDPOINTS SUMMARY", section_style))
    content.append(Spacer(1, 16))
    
    api_summary = [
        ['Method', 'Endpoint', 'Purpose'],
        ['GET', '/', 'Health check & model status'],
        ['POST', '/upload-jd', 'Upload job description PDF'],
        ['GET', '/jd-status', 'Check if JD is processed'],
        ['POST', '/upload-resumes', 'Upload resumes & get analysis'],
        ['GET', '/download/ranking-report', 'Download ranking PDF'],
        ['GET', '/download/analysis-output', 'Download analysis PDF'],
        ['GET', '/download/xai-report', 'Download XAI explanations'],
        ['POST', '/clear', 'Clear all data'],
        ['DELETE', '/clear-jd', 'Clear only JD'],
        ['DELETE', '/clear-resumes', 'Clear only resumes'],
        ['GET', '/debug/files', 'Debug file status']
    ]
    
    api_table = Table(api_summary, colWidths=[1*inch, 2.5*inch, 3*inch])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]))
    content.append(api_table)
    
    content.append(Spacer(1, 20))
    
    # ==================== DEPLOYMENT ====================
    content.append(Paragraph("☁️ DEPLOYMENT DETAILS", section_style))
    content.append(Spacer(1, 16))
    
    deploy_info = """
<b>Production URL:</b> https://agentic-hiring-prototype.onrender.com<br/><br/>

<b>Platform:</b> Render (Cloud PaaS)<br/>
<b>Instance:</b> Free tier (512MB RAM, 0.1 vCPU)<br/>
<b>Region:</b> US East (can be changed)<br/>
<b>SSL:</b> Automatic HTTPS via Let's Encrypt<br/>
<b>Build:</b> Docker container<br/>
<b>Auto-deploy:</b> Enabled from main branch<br/><br/>

<b>Environment Variables:</b><br/>
• ENV=production<br/>
• HF_TOKEN=[Hugging Face token]<br/>
• USE_LIGHTWEIGHT_MODEL=true<br/>
• PORT=8000<br/><br/>

<b>Performance Optimizations:</b><br/>
• CPU-only PyTorch (smaller footprint)<br/>
• Single worker process<br/>
• Lazy model loading<br/>
• Lightweight MiniLM model (80M params)
"""
    content.append(Paragraph(deploy_info, ParagraphStyle('deploy', parent=styles['Normal'], fontSize=9, leading=13)))
    
    content.append(PageBreak())
    
    # ==================== SECURITY & COMPLIANCE ====================
    content.append(Paragraph("🔒 SECURITY & COMPLIANCE", section_style))
    content.append(Spacer(1, 16))
    
    security_text = """
<b>Privacy Protection:</b><br/>
✅ PII Redaction: Emails, phones, URLs removed before processing<br/>
✅ No Data Storage: Uploaded files deleted after analysis<br/>
✅ Anonymized Reports: All outputs contain sanitized data only<br/><br/>

<b>Compliance:</b><br/>
✅ GDPR Article 22: Right to explanation provided<br/>
✅ EU AI Act: Transparent decision-making with audit trails<br/>
✅ IEEE 7000: Ethical AI standards followed<br/><br/>

<b>Security Measures:</b><br/>
✅ HTTPS encryption for all communications<br/>
✅ Environment variables for sensitive data<br/>
✅ Input validation using Pydantic<br/>
✅ File type restrictions (PDF only)<br/>
✅ Session-based temporary storage<br/>
✅ Automatic cleanup of temporary files<br/><br/>

<b>Bias Mitigation:</b><br/>
✅ No demographic data used in scoring<br/>
✅ Skills-based evaluation only<br/>
✅ Transparent scoring methodology<br/>
✅ Explainable AI for all decisions
"""
    content.append(Paragraph(security_text, ParagraphStyle('security', parent=styles['Normal'], fontSize=9, leading=13)))
    
    # Footer
    content.append(Spacer(1, 0.5*inch))
    footer_text = """
<font size="8" color="#6c757d">
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br/>
<b>Agentic Hiring System v1.0.0</b><br/>
Technical Documentation Generated: {}<br/>
Repository: https://github.com/SOMNATH5353/Agentic_Hiring_Prototype<br/>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</font>
""".format(datetime.now().strftime('%B %d, %Y at %H:%M UTC'))
    content.append(Paragraph(footer_text, ParagraphStyle('footer', parent=styles['Normal'], alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(content)
    print(f"✅ Technical documentation generated: {output_path}")


if __name__ == "__main__":
    generate_technical_docs()
