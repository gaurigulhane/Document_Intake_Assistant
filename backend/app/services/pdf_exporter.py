import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class PDFExporter:
    @staticmethod
    def generate_pdf_bytes(data: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom styles
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#1E293B'),
            alignment=TA_CENTER
        )

        disclaimer_style = ParagraphStyle(
            'DisclaimerStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#DC2626'),
            alignment=TA_CENTER
        )

        section_title_style = ParagraphStyle(
            'SectionTitleStyle',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#2563EB'),
            spaceBefore=10,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155')
        )

        bold_label_style = ParagraphStyle(
            'BoldLabelStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#0F172A')
        )

        story = []

        # Title
        story.append(Paragraph("PERSONAL WISHES DOCUMENT", header_style))
        story.append(Spacer(1, 6))

        # Disclaimer Box
        story.append(Paragraph("FICTIONAL DOCUMENT — NOT LEGAL ADVICE", disclaimer_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

        def make_row(label: str, val: str):
            p_label = Paragraph(label, bold_label_style)
            p_val = Paragraph(val, body_style)
            return [p_label, p_val]

        # 1. Personal Details
        story.append(Paragraph("1. Personal Details", section_title_style))
        full_name = data.get("full_name") or "Not Provided"
        home_address = data.get("home_address") or "Not Provided"
        
        t1 = Table([
            make_row("Full Name:", full_name),
            make_row("Home Address:", home_address)
        ], colWidths=[140, 380])
        t1.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t1)
        story.append(Spacer(1, 10))

        # 2. Asset Scope
        story.append(Paragraph("2. Asset Scope", section_title_style))
        ww = data.get("covers_worldwide_assets")
        ww_str = "Yes - Covers worldwide assets" if ww is True else ("No - Primary country only" if ww is False else "Not Specified")
        t2 = Table([
            make_row("Covers Worldwide Assets:", ww_str)
        ], colWidths=[140, 380])
        t2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(t2)
        story.append(Spacer(1, 10))

        # 3. Family Details
        story.append(Paragraph("3. Family Details", section_title_style))
        has_kids = data.get("has_children")
        children = data.get("children") or []
        if has_kids is True:
            kids_str = f"Yes ({', '.join(children)})" if children else "Yes"
        elif has_kids is False:
            kids_str = "No children"
        else:
            kids_str = "Not Specified"
        t3 = Table([
            make_row("Children Status:", kids_str)
        ], colWidths=[140, 380])
        t3.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(t3)
        story.append(Spacer(1, 10))

        # 4. Executor
        story.append(Paragraph("4. Appointed Executor", section_title_style))
        exec_dict = data.get("executor") or {}
        e_name = exec_dict.get("name") or "Not Specified"
        e_rel = exec_dict.get("relationship") or "Not Specified"
        t4 = Table([
            make_row("Executor Name:", e_name),
            make_row("Relationship:", e_rel)
        ], colWidths=[140, 380])
        t4.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(t4)
        story.append(Spacer(1, 10))

        # 5. Specific Gifts
        story.append(Paragraph("5. Specific Gifts & Requests", section_title_style))
        gifts = data.get("specific_gifts") or []
        gifts_formatted = "<br/>".join([f"• {g}" for g in gifts]) if gifts else "None specified"
        t5 = Table([
            make_row("Specific Gifts:", gifts_formatted)
        ], colWidths=[140, 380])
        t5.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(t5)
        story.append(Spacer(1, 10))

        # 6. Additional Wishes
        story.append(Paragraph("6. Additional Wishes", section_title_style))
        wishes = data.get("additional_wishes") or "None specified"
        t6 = Table([
            make_row("Additional Wishes:", wishes)
        ], colWidths=[140, 380])
        t6.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(t6)
        story.append(Spacer(1, 20))

        # Footer Notice
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))
        story.append(Paragraph("Notice: This document is created for demonstration purposes as part of the LLM Technical Assessment.", ParagraphStyle('FootNote', parent=styles['Italic'], fontSize=8, textColor=colors.HexColor('#64748B'), alignment=TA_CENTER)))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
