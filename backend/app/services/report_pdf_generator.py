"""
PDF Generation Service for Prediction Reports
Uses ReportLab to generate publication-grade PDF documents.
"""

import os
import io
import re
import html
from datetime import datetime
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
    Table,
    TableStyle
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page counts and running headers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#6B7280'))

        # Running header on page 2 and beyond
        if self._pageNumber > 1:
            self.drawString(54, 750, "LOKĀNTRA  |  PREDICTION REPORT")
            self.setStrokeColor(colors.HexColor('#E5E7EB'))
            self.setLineWidth(0.6)
            self.line(54, 742, 558, 742)

        # Running footer on all pages
        self.setStrokeColor(colors.HexColor('#E5E7EB'))
        self.setLineWidth(0.6)
        self.line(54, 46, 558, 46)
        self.drawString(54, 32, "LOKĀNTRA Swarm Simulation Environment  •  Confidential Prediction Report")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


class ReportPDFGenerator:
    """Generates structured PDF reports matching Lokantra's black & white design system."""

    @classmethod
    def _sanitize_inline_markdown(cls, text: str) -> str:
        """Escape XML entities while preserving simple formatting (bold, italic, code)."""
        if not text:
            return ""

        # First escape XML special characters
        text = html.escape(text)

        # Re-convert escaped bold: &lt;b&gt; or **bold**
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

        # Re-convert escaped italic: *italic* or _italic_
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
        text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<i>\1</i>', text)

        # Inline code
        text = re.sub(r'`(.+?)`', r'<font face="Courier" color="#1F2937">\1</font>', text)

        return text

    @classmethod
    def _create_styles(cls) -> Dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()

        return {
            'ReportTag': ParagraphStyle(
                'ReportTag',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=8.5,
                leading=10,
                textColor=colors.HexColor('#111827'),
                spaceAfter=4
            ),
            'ReportId': ParagraphStyle(
                'ReportId',
                parent=styles['Normal'],
                fontName='Courier',
                fontSize=8.5,
                leading=10,
                textColor=colors.HexColor('#6B7280'),
                spaceAfter=12
            ),
            'MainTitle': ParagraphStyle(
                'MainTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=21,
                leading=26,
                textColor=colors.HexColor('#0A0A0A'),
                spaceAfter=10
            ),
            'SubTitle': ParagraphStyle(
                'SubTitle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10.5,
                leading=15,
                textColor=colors.HexColor('#4B5563'),
                spaceAfter=14
            ),
            'SectionBadge': ParagraphStyle(
                'SectionBadge',
                parent=styles['Normal'],
                fontName='Courier-Bold',
                fontSize=10,
                leading=12,
                textColor=colors.HexColor('#111827'),
                spaceAfter=2
            ),
            'SectionTitle': ParagraphStyle(
                'SectionTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=14,
                leading=18,
                textColor=colors.HexColor('#0A0A0A'),
                spaceAfter=8,
                keepWithNext=True
            ),
            'SubSectionTitle': ParagraphStyle(
                'SubSectionTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=11.5,
                leading=15,
                textColor=colors.HexColor('#1F2937'),
                spaceBefore=8,
                spaceAfter=6,
                keepWithNext=True
            ),
            'Body': ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9.5,
                leading=14.5,
                textColor=colors.HexColor('#1F2937'),
                spaceAfter=8
            ),
            'Bullet': ParagraphStyle(
                'Bullet',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9.5,
                leading=14,
                textColor=colors.HexColor('#1F2937'),
                leftIndent=16,
                firstLineIndent=-10,
                spaceAfter=4
            ),
            'Blockquote': ParagraphStyle(
                'Blockquote',
                parent=styles['Normal'],
                fontName='Helvetica-Oblique',
                fontSize=9,
                leading=13.5,
                textColor=colors.HexColor('#374151'),
                leftIndent=14,
                rightIndent=14,
                spaceBefore=6,
                spaceAfter=8
            ),
            'MetaTableText': ParagraphStyle(
                'MetaTableText',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor('#4B5563')
            )
        }

    @classmethod
    def _parse_markdown_section_to_flowables(
        cls,
        text: str,
        styles: Dict[str, ParagraphStyle]
    ) -> List[Any]:
        """Convert a section's markdown text into ReportLab flowables."""
        flowables = []
        if not text:
            return flowables

        lines = text.split('\n')
        i = 0
        current_paragraph_lines = []

        def flush_paragraph():
            nonlocal current_paragraph_lines
            if current_paragraph_lines:
                combined = " ".join(current_paragraph_lines).strip()
                if combined:
                    sanitized = cls._sanitize_inline_markdown(combined)
                    flowables.append(Paragraph(sanitized, styles['Body']))
                current_paragraph_lines = []

        while i < len(lines):
            line = lines[i].rstrip()
            stripped = line.strip()

            if not stripped:
                flush_paragraph()
                i += 1
                continue

            # Heading 1 or 2 (treated as subsection title if inside a section)
            if stripped.startswith('### '):
                flush_paragraph()
                title_text = cls._sanitize_inline_markdown(stripped[4:].strip())
                flowables.append(Paragraph(title_text, styles['SubSectionTitle']))
                i += 1
                continue
            elif stripped.startswith('## '):
                flush_paragraph()
                title_text = cls._sanitize_inline_markdown(stripped[3:].strip())
                flowables.append(Paragraph(title_text, styles['SubSectionTitle']))
                i += 1
                continue
            elif stripped.startswith('# '):
                flush_paragraph()
                title_text = cls._sanitize_inline_markdown(stripped[2:].strip())
                flowables.append(Paragraph(title_text, styles['SectionTitle']))
                i += 1
                continue

            # Horizontal rule
            if re.match(r'^(\*{3,}|-{3,}|_{3,})$', stripped):
                flush_paragraph()
                flowables.append(Spacer(1, 4))
                flowables.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E5E7EB'), spaceBefore=4, spaceAfter=8))
                i += 1
                continue

            # Blockquote
            if stripped.startswith('>'):
                flush_paragraph()
                quote_lines = []
                while i < len(lines) and lines[i].strip().startswith('>'):
                    q_line = lines[i].strip().lstrip('>').strip()
                    if q_line:
                        quote_lines.append(q_line)
                    i += 1
                quote_text = cls._sanitize_inline_markdown(" ".join(quote_lines))
                # Render blockquote with light grey background box
                quote_p = Paragraph(f'"{quote_text}"', styles['Blockquote'])
                quote_table = Table([[quote_p]], colWidths=[500])
                quote_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
                    ('LINELEFT', (0, 0), (0, -1), 2.5, colors.HexColor('#111827')),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ]))
                flowables.append(quote_table)
                flowables.append(Spacer(1, 6))
                continue

            # Bullet points (- or * or numbered 1.)
            bullet_match = re.match(r'^[-*]\s+(.+)$', stripped) or re.match(r'^\d+\.\s+(.+)$', stripped)
            if bullet_match:
                flush_paragraph()
                bullet_content = cls._sanitize_inline_markdown(bullet_match.group(1))
                flowables.append(Paragraph(f"&bull; {bullet_content}", styles['Bullet']))
                i += 1
                continue

            # Regular body text line
            current_paragraph_lines.append(stripped)
            i += 1

        flush_paragraph()
        return flowables

    @classmethod
    def generate_pdf(
        cls,
        report_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF from report dictionary.
        
        Args:
            report_data: Dictionary containing report information (outline, sections, metadata)
            output_path: Optional file path to write PDF to
            
        Returns:
            bytes: PDF file content
        """
        styles = cls._create_styles()
        buffer = io.BytesIO()

        # Page setup: Letter size with 54pt (0.75 in) margins
        doc = SimpleDocTemplate(
            output_path if output_path else buffer,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        flowables = []

        outline = report_data.get('outline') or {}
        title = outline.get('title') or report_data.get('title') or "Prediction Report"
        summary = outline.get('summary') or report_data.get('summary') or ""
        report_id = report_data.get('report_id') or "REF-REPORT"
        created_at = report_data.get('created_at') or datetime.now().strftime("%Y-%m-%d %H:%M")

        # Top Meta Header Table
        meta_left = f"<b>PREDICTION REPORT</b> &nbsp;&bull;&nbsp; <font color='#6B7280'>ID: {report_id}</font>"
        meta_right = f"<font color='#6B7280'>Generated: {created_at}</font>"
        
        header_table = Table(
            [[
                Paragraph(meta_left, styles['ReportTag']),
                Paragraph(meta_right, ParagraphStyle('RMeta', parent=styles['ReportTag'], alignment=2))
            ]],
            colWidths=[350, 154]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        flowables.append(header_table)
        flowables.append(Spacer(1, 6))

        # Main Title
        flowables.append(Paragraph(cls._sanitize_inline_markdown(title), styles['MainTitle']))

        # Executive Summary / Subtitle
        if summary:
            flowables.append(Paragraph(cls._sanitize_inline_markdown(summary), styles['SubTitle']))

        # Divider line
        flowables.append(HRFlowable(
            width="100%",
            thickness=1.0,
            color=colors.HexColor('#111827'),
            spaceBefore=4,
            spaceAfter=16
        ))

        # Sections
        sections = outline.get('sections') or []
        sections_content = report_data.get('sections_content') or {}

        # If sections_content is empty, try to parse from markdown_content
        full_md = report_data.get('markdown_content') or ""

        if sections:
            for idx, sec in enumerate(sections):
                sec_num = String_pad = f"{idx + 1:02d}"
                sec_title = sec.get('title', '')
                sec_content = sections_content.get(idx + 1) or sections_content.get(str(idx + 1)) or sec.get('content', '')

                # Section Header Block (kept together with its first paragraphs)
                sec_header_flowables = [
                    Paragraph(f"SECTION {sec_num}", styles['SectionBadge']),
                    Paragraph(cls._sanitize_inline_markdown(sec_title), styles['SectionTitle']),
                    HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E5E7EB'), spaceBefore=2, spaceAfter=8)
                ]

                # Parse body
                sec_body_flowables = cls._parse_markdown_section_to_flowables(sec_content, styles)

                if sec_body_flowables:
                    # Keep section header with first item
                    flowables.append(KeepTogether(sec_header_flowables + sec_body_flowables[:2]))
                    flowables.extend(sec_body_flowables[2:])
                else:
                    flowables.extend(sec_header_flowables)

                flowables.append(Spacer(1, 14))

        elif full_md:
            # Fallback: parse entire markdown document
            md_flowables = cls._parse_markdown_section_to_flowables(full_md, styles)
            flowables.extend(md_flowables)

        # Build document with NumberedCanvas
        doc.build(flowables, canvasmaker=NumberedCanvas)

        if output_path:
            with open(output_path, 'rb') as f:
                return f.read()
        else:
            return buffer.getvalue()
