from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


def write_analysis_pdf(output_path, jd_sentences, resumes):
    # Set up document with proper margins
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
    
    # Custom styles for better formatting
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=12,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=32
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#6c757d'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        spaceAfter=30,
        spaceBefore=8
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.white,
        spaceAfter=16,
        spaceBefore=24,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#2c3e50'),
        borderPadding=(12, 12, 12, 12),
        leading=22
    )
    
    subsection_style = ParagraphStyle(
        'SubSection',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        spaceBefore=16,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderPadding=0,
        leftIndent=0,
        leading=18
    )
    
    intro_style = ParagraphStyle(
        'IntroText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#6c757d'),
        fontName='Helvetica-Oblique',
        alignment=TA_CENTER,
        spaceAfter=20,
        spaceBefore=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontSize=10,
        leading=16,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_LEFT,
        leftIndent=0,
        rightIndent=10,
        spaceAfter=8,
        spaceBefore=0,
        bulletIndent=10,
        bulletFontName='Helvetica',
        bulletFontSize=10
    )
    
    # Title Page with decorative elements
    content.append(Spacer(1, 0.8*inch))
    
    # Add decorative top border
    title_border = Table([['']], colWidths=[6.5*inch], rowHeights=[0.1*inch])
    title_border.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3498db')),
        ('ROUNDEDCORNERS', [10, 10, 10, 10])
    ]))
    content.append(title_border)
    content.append(Spacer(1, 0.4*inch))
    
    content.append(Paragraph("RECRUITMENT ANALYSIS REPORT", title_style))
    content.append(Paragraph(
        "Privacy-Protected Document | All PII Redacted", 
        subtitle_style
    ))
    
    content.append(Spacer(1, 0.5*inch))
    
    # Enhanced summary box with gradient effect
    summary_data = [
        ['📊 Total Resumes Analyzed:', str(len(resumes))],
        ['📋 Job Description Sections:', str(len(jd_sentences))],
        ['🔒 Privacy Status:', 'All PII Removed']
    ]
    summary_table = Table(summary_data, colWidths=[3.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8f9fa')])
    ]))
    content.append(summary_table)
    
    content.append(Spacer(1, 0.3*inch))
    
    # Add decorative bottom element
    content.append(title_border)
    
    content.append(PageBreak())
    
    # ==================== JOB DESCRIPTION SECTION ====================
    content.append(Paragraph("📑 JOB DESCRIPTION ANALYSIS", section_style))
    content.append(Spacer(1, 16))
    content.append(Paragraph(
        "The following job requirements have been extracted and sanitized for analysis:",
        intro_style
    ))
    content.append(Spacer(1, 12))
    
    # JD content with custom bullets
    for sentence in jd_sentences:
        # Escape special characters for ReportLab
        safe_sentence = sentence.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Use unicode bullet point character
        bullet_text = f"<font color='#3498db' size='12'>\u2022</font>  {safe_sentence}"
        content.append(Paragraph(bullet_text, bullet_style))
    
    content.append(Spacer(1, 30))
    content.append(PageBreak())
    
    # ==================== RESUME SECTION ====================
    content.append(Paragraph("👥 CANDIDATE RESUME ANALYSIS", section_style))
    content.append(Spacer(1, 20))
    
    for resume_idx, (resume_name, sentences) in enumerate(resumes.items(), 1):
        # Create a box around each candidate section
        candidate_items = []
        
        # Candidate header with badge
        badge_style = ParagraphStyle(
            'BadgeStyle',
            parent=subsection_style,
            fontSize=14,
            textColor=colors.white,
            backColor=colors.HexColor('#3498db'),
            borderPadding=8,
            alignment=TA_CENTER
        )
        candidate_items.append(Paragraph(f"🎯 CANDIDATE #{resume_idx}", badge_style))
        candidate_items.append(Spacer(1, 12))
        
        # File info table with better styling
        file_info_data = [[
            Paragraph('<b>Source File:</b>', styles['Normal']),
            Paragraph(resume_name, styles['Normal'])
        ]]
        file_info = Table(file_info_data, colWidths=[1.5*inch, 4.5*inch])
        file_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#90caf9'))
        ]))
        candidate_items.append(file_info)
        candidate_items.append(Spacer(1, 16))
        
        # Section label
        label_para = Paragraph(
            "<b>💼 Extracted Skills & Experience:</b>",
            ParagraphStyle('LabelStyle', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#2c3e50'), spaceAfter=10)
        )
        candidate_items.append(label_para)
        candidate_items.append(Spacer(1, 8))
        
        # Resume content with enhanced bullets
        for sentence in sentences:
            # Escape special characters
            safe_sentence = sentence.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Use unicode bullet with color
            bullet_text = f"<font color='#27ae60' size='12'>\u2713</font>  {safe_sentence}"
            candidate_items.append(Paragraph(bullet_text, bullet_style))
        
        # Keep candidate section together when possible
        content.extend(candidate_items)
        content.append(Spacer(1, 24))
        
        # Add decorative separator between resumes
        if resume_idx < len(resumes):
            separator = Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch])
            separator.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#bdc3c7')),
                ('ROUNDEDCORNERS', [5, 5, 5, 5])
            ]))
            content.append(separator)
            content.append(Spacer(1, 24))
    
    # Footer section
    content.append(Spacer(1, 0.4*inch))
    
    footer_border = Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch])
    footer_border.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3498db'))
    ]))
    content.append(footer_border)
    content.append(Spacer(1, 12))
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6c757d'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    content.append(Paragraph(
        "━━━ End of Analysis Report ━━━",
        footer_style
    ))
    content.append(Spacer(1, 6))
    content.append(Paragraph(
        "This document contains sanitized data with all personal identifiable information removed.",
        footer_style
    ))
    
    # Build the PDF
    doc.build(content)
