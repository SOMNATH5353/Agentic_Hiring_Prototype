from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime


def write_ranking_pdf(output_path, ranked_candidates, jd_file):
    """
    Generate a comprehensive ranking and analysis PDF report.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.6*inch,
        bottomMargin=0.6*inch
    )
    
    styles = getSampleStyleSheet()
    content = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=34
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#6c757d'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        spaceAfter=20
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.white,
        spaceAfter=12,
        spaceBefore=16,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#2c3e50'),
        borderPadding=10,
        leading=20
    )
    
    # ==================== TITLE PAGE ====================
    content.append(Spacer(1, 0.5*inch))
    
    # Top decorative line
    top_line = Table([['']], colWidths=[7*inch], rowHeights=[0.15*inch])
    top_line.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3498db')),
        ('ROUNDEDCORNERS', [10, 10, 10, 10])
    ]))
    content.append(top_line)
    content.append(Spacer(1, 0.3*inch))
    
    content.append(Paragraph("🏆 CANDIDATE RANKING REPORT", title_style))
    content.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        subtitle_style
    ))
    
    content.append(Spacer(1, 0.2*inch))
    
    # Executive Summary Table
    summary_data = [
        ['📋 Job Description:', jd_file.split('\\')[-1] if '\\' in jd_file else jd_file],
        ['👥 Total Candidates:', str(len(ranked_candidates))],
        ['✅ Recommended for Hire:', str(sum(1 for c in ranked_candidates if 'SELECT_FAST_TRACK' in str(c['action'])))],
        ['📞 Recommended for Interview:', str(sum(1 for c in ranked_candidates if 'INTERVIEW' in str(c['action'])))],
        ['💼 Talent Pool:', str(sum(1 for c in ranked_candidates if 'POOL' in str(c['action'])))],
        ['❌ Not Recommended:', str(sum(1 for c in ranked_candidates if 'REJECT' in str(c['action'])))]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
    ]))
    content.append(summary_table)
    
    content.append(Spacer(1, 0.3*inch))
    content.append(top_line)
    content.append(PageBreak())
    
    # ==================== RANKING TABLE ====================
    content.append(Paragraph("📊 OVERALL CANDIDATE RANKING", section_header_style))
    content.append(Spacer(1, 16))
    
    # Create ranking table
    ranking_data = [['Rank', 'Candidate', 'Score', 'Tier', 'Decision']]
    
    for candidate in ranked_candidates:
        rank_display = f"#{candidate['rank']}"
        name_display = candidate['name'][:30]  # Truncate long names
        score_display = f"{candidate['composite_score']:.4f}"
        tier_display = candidate['tier']
        action_display = str(candidate['action']).split('.')[-1].replace('_', ' ')
        
        ranking_data.append([
            rank_display,
            name_display,
            score_display,
            tier_display,
            action_display
        ])
    
    ranking_table = Table(ranking_data, colWidths=[0.8*inch, 2.5*inch, 1*inch, 1.2*inch, 1.5*inch])
    
    table_style = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]
    
    # Color code by tier
    for i, candidate in enumerate(ranked_candidates, 1):
        tier = candidate['tier']
        if tier == 'Excellent':
            table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#27ae60')))
            table_style.append(('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'))
        elif tier == 'Good':
            table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#2980b9')))
        elif tier == 'Marginal':
            table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#f39c12')))
        else:
            table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#e74c3c')))
    
    ranking_table.setStyle(TableStyle(table_style))
    content.append(ranking_table)
    
    content.append(PageBreak())
    
    # ==================== DETAILED ANALYSIS ====================
    content.append(Paragraph("📈 DETAILED CANDIDATE ANALYSIS", section_header_style))
    content.append(Spacer(1, 20))
    
    for idx, candidate in enumerate(ranked_candidates, 1):
        # Candidate header
        candidate_header_style = ParagraphStyle(
            f'CandidateHeader{idx}',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.white,
            backColor=colors.HexColor('#3498db'),
            borderPadding=8,
            fontName='Helvetica-Bold'
        )
        
        rank_str = f"#{candidate['rank']}"
        content.append(Paragraph(
            f"{rank_str} | {candidate['name']} | Score: {candidate['composite_score']:.4f}",
            candidate_header_style
        ))
        content.append(Spacer(1, 10))
        
        # Score breakdown table
        score_data = [
            ['Metric', 'Score', 'Weight', 'Contribution'],
            ['Role Fit (RFS)', f"{candidate['rfs']:.3f}", '35%', f"{candidate['rfs'] * 0.35:.4f}"],
            ['Domain Compatibility (DCS)', f"{candidate['dcs']:.3f}", '25%', f"{candidate['dcs'] * 0.25:.4f}"],
            ['Capability Strength (CSS)', f"{candidate['css']:.3f}", '20%', f"{candidate['css'] * 0.20:.4f}"],
            ['Execution Language (ELC)', f"{candidate['elc']}", '15%', f"{candidate['elc'] * 0.15:.4f}"],
            ['Growth Potential (GPS)', f"{candidate['gps']:.3f}", '5%', f"{candidate['gps'] * 0.05:.4f}"]
        ]
        
        score_table = Table(score_data, colWidths=[2.2*inch, 1*inch, 1*inch, 1.3*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        content.append(score_table)
        content.append(Spacer(1, 10))
        
        # Decision and explanation
        decision_style = ParagraphStyle(
            'Decision',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            leftIndent=15,
            rightIndent=15
        )
        
        action_text = str(candidate['action']).split('.')[-1].replace('_', ' ')
        content.append(Paragraph(
            f"<b>Decision:</b> {action_text}",
            decision_style
        ))
        content.append(Spacer(1, 6))
        content.append(Paragraph(
            f"<b>Rationale:</b> {candidate['explanation']}",
            decision_style
        ))
        content.append(Spacer(1, 6))
        content.append(Paragraph(
            f"<b>Tier:</b> {candidate['tier']}",
            decision_style
        ))
        
        content.append(Spacer(1, 16))
        
        # Separator between candidates
        if idx < len(ranked_candidates):
            separator = Table([['']], colWidths=[6.5*inch], rowHeights=[0.03*inch])
            separator.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#bdc3c7'))
            ]))
            content.append(separator)
            content.append(Spacer(1, 16))
    
    # ==================== LEGEND/FOOTER ====================
    content.append(PageBreak())
    content.append(Paragraph("📚 SCORING METHODOLOGY", section_header_style))
    content.append(Spacer(1, 16))
    
    methodology_text = """
    <b>Composite Score Calculation:</b><br/>
    The final ranking score is calculated using a weighted average of five key metrics:<br/><br/>
    
    • <b>Role Fit Score (35%):</b> Measures how well the candidate's experience matches the job requirements based on semantic analysis.<br/>
    • <b>Domain Compatibility Score (25%):</b> Evaluates technical stack alignment and domain expertise.<br/>
    • <b>Capability Strength Score (20%):</b> Assesses professional experience, expertise level, and demonstrated capabilities.<br/>
    • <b>Execution Language Score (15%):</b> Binary check for required programming language proficiency (including equivalents like ML for Python).<br/>
    • <b>Growth Potential Score (5%):</b> Evaluates learning indicators, certifications, and adaptability.<br/><br/>
    
    <b>Tier Definitions:</b><br/>
    • <b><font color="#27ae60">Excellent (≥0.7):</font></b> Top-tier candidates recommended for immediate action<br/>
    • <b><font color="#2980b9">Good (≥0.5):</font></b> Solid candidates worth interviewing<br/>
    • <b><font color="#f39c12">Marginal (≥0.3):</font></b> Edge cases, consider for specific needs or talent pool<br/>
    • <b><font color="#e74c3c">Rejected (&lt;0.3):</font></b> Not suitable for current role<br/><br/>
    
    <b>Tiebreaker Rules:</b><br/>
    When candidates have identical composite scores, ranking is determined by:<br/>
    1. Action priority (HIRE > INTERVIEW > POOL > REJECT)<br/>
    2. Domain Compatibility Score (higher first)<br/>
    3. Role Fit Score (higher first)<br/>
    4. Capability Strength Score (higher first)<br/>
    5. Alphabetical order (last resort)
    """
    
    methodology_style = ParagraphStyle(
        'Methodology',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        leftIndent=10,
        rightIndent=10,
        alignment=TA_JUSTIFY
    )
    
    content.append(Paragraph(methodology_text, methodology_style))
    
    # Footer
    content.append(Spacer(1, 0.3*inch))
    footer_line = Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch])
    footer_line.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3498db'))
    ]))
    content.append(footer_line)
    content.append(Spacer(1, 10))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#6c757d'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    content.append(Paragraph(
        "━━━ End of Ranking Report ━━━<br/>"
        "This analysis is based on AI-powered evaluation with PII protection.<br/>"
        "All personal identifiable information has been redacted for privacy compliance.",
        footer_style
    ))
    
    # Build PDF
    doc.build(content)
