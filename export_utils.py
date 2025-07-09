"""
Export utilities for generating PDF and detailed reports.
"""

import os
import json
import datetime
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
import base64
from io import BytesIO

# PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch
import reportlab.platypus as platypus
import markdown
import pdfkit
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Project imports
from config import EXPORT_FORMATS, DEFAULT_EXPORT_FORMAT, EXPORT_OUTPUT_DIR, PDF_THEME, APP_TITLE

# Setup logging
logger = logging.getLogger(__name__)


class ExportManager:
    """Manager class for handling all export operations."""

    def __init__(self, output_dir: str = EXPORT_OUTPUT_DIR):
        """Initialize the export manager.
        
        Args:
            output_dir: Directory to save exports to
        """
        self.output_dir = output_dir
        self._ensure_export_directory()
        
        # Initialize Jinja for HTML templates
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def _ensure_export_directory(self) -> None:
        """Ensure the export directory exists."""
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
                logger.info(f"Created export directory: {self.output_dir}")
            except Exception as e:
                logger.error(f"Failed to create export directory: {str(e)}")
                raise
    
    def _generate_filename(self, prefix: str, extension: str) -> str:
        """Generate a timestamped filename for exports.
        
        Args:
            prefix: Prefix for the filename
            extension: File extension (without dot)
            
        Returns:
            Full path to the generated filename
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{extension}"
        return os.path.join(self.output_dir, filename)
    
    def export_analysis(self, 
                       analysis_data: Dict[str, Any], 
                       markdown_plan: str, 
                       model_used: str,
                       export_format: str = DEFAULT_EXPORT_FORMAT) -> str:
        """Export analysis results in the specified format.
        
        Args:
            analysis_data: The analysis data dictionary
            markdown_plan: The original architecture plan
            model_used: The model used for analysis
            export_format: Format to export as (PDF, HTML, Markdown)
            
        Returns:
            Path to the exported file
        """
        if export_format.upper() not in EXPORT_FORMATS:
            raise ValueError(f"Unsupported export format: {export_format}. Supported formats: {', '.join(EXPORT_FORMATS)}")
        
        if export_format.upper() == "PDF":
            return self.generate_pdf_report(analysis_data, markdown_plan, model_used)
        elif export_format.upper() == "HTML":
            return self.generate_html_report(analysis_data, markdown_plan, model_used)
        elif export_format.upper() == "MARKDOWN":
            return self.generate_markdown_report(analysis_data, markdown_plan, model_used)
        else:
            raise ValueError(f"Unhandled export format: {export_format}")
    
    def generate_pdf_report(self, 
                           analysis_data: Dict[str, Any], 
                           markdown_plan: str, 
                           model_used: str) -> str:
        """Generate a PDF report of the architecture analysis.
        
        Args:
            analysis_data: The analysis data dictionary
            markdown_plan: The original architecture plan
            model_used: The model used for analysis
            
        Returns:
            Path to the generated PDF file
        """
        output_path = self._generate_filename("architecture_analysis", "pdf")
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=PDF_THEME.get("page_margin", 50),
            leftMargin=PDF_THEME.get("page_margin", 50),
            topMargin=PDF_THEME.get("page_margin", 50),
            bottomMargin=PDF_THEME.get("page_margin", 50)
        )
        
        # Create styles
        styles = getSampleStyleSheet()
        
        # Custom styles based on theme
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName=PDF_THEME.get("title_font", "Helvetica-Bold"),
            fontSize=PDF_THEME.get("title_size", 24),
            textColor=colors.HexColor(PDF_THEME.get("primary_color", "#667eea")),
            spaceAfter=36
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontName=PDF_THEME.get("header_font", "Helvetica-Bold"),
            fontSize=PDF_THEME.get("header_size", 16),
            textColor=colors.HexColor(PDF_THEME.get("secondary_color", "#764ba2")),
            spaceAfter=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=PDF_THEME.get("body_font", "Helvetica"),
            fontSize=PDF_THEME.get("body_size", 11),
            textColor=colors.HexColor(PDF_THEME.get("text_color", "#333333")),
        )
        
        # Build the content
        content = []
        
        # Title
        content.append(Paragraph(APP_TITLE, title_style))
        content.append(Paragraph("Architecture Analysis Report", heading_style))
        content.append(Spacer(1, 0.25*inch))
        
        # Metadata
        content.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
        content.append(Paragraph(f"Model Used: {model_used}", normal_style))
        content.append(Spacer(1, 0.25*inch))
        
        # Executive Summary
        content.append(Paragraph("Executive Summary", heading_style))
        content.append(Paragraph(analysis_data.get("summaryOfReviewerObservations", "No summary provided."), normal_style))
        content.append(Spacer(1, 0.25*inch))
        
        # Plan Summary
        content.append(Paragraph("System Plan Overview", heading_style))
        content.append(Paragraph(analysis_data.get("planSummary", "No summary provided."), normal_style))
        content.append(Spacer(1, 0.25*inch))
        
        # Strengths
        content.append(Paragraph("Strengths", heading_style))
        strengths = analysis_data.get("strengths", [])
        if strengths:
            for strength in strengths:
                content.append(Paragraph(f"<b>{strength.get('dimension', '')}</b>: {strength.get('point', '')}", normal_style))
                content.append(Paragraph(f"<i>Rationale:</i> {strength.get('reason', '')}", normal_style))
                content.append(Spacer(1, 0.1*inch))
        else:
            content.append(Paragraph("No strengths identified.", normal_style))
        content.append(Spacer(1, 0.25*inch))
        
        # Areas for Improvement
        content.append(Paragraph("Areas for Improvement", heading_style))
        areas = analysis_data.get("areasForImprovement", [])
        if areas:
            for area in areas:
                severity = area.get("severity", "").upper()
                severity_color = "#FF0000" if severity == "CRITICAL" else "#FFA500" if severity == "HIGH" else "#FFCC00" if severity == "MEDIUM" else "#008000"
                
                content.append(Paragraph(f"<b>{area.get('area', '')}</b> - <font color='{severity_color}'>{severity}</font>", normal_style))
                content.append(Paragraph(f"<i>Concern:</i> {area.get('concern', '')}", normal_style))
                content.append(Paragraph(f"<i>Suggestion:</i> {area.get('suggestion', '')}", normal_style))
                content.append(Paragraph(f"<i>Impact:</i> {area.get('impact', '')}", normal_style))
                
                if area.get("tradeOffsConsidered"):
                    content.append(Paragraph(f"<i>Trade-offs:</i> {area.get('tradeOffsConsidered', '')}", normal_style))
                
                content.append(Spacer(1, 0.1*inch))
        else:
            content.append(Paragraph("No areas for improvement identified.", normal_style))
        content.append(Spacer(1, 0.25*inch))
        
        # Strategic Recommendations
        content.append(Paragraph("Strategic Recommendations", heading_style))
        recommendations = analysis_data.get("strategicRecommendations", [])
        if recommendations:
            for rec in recommendations:
                content.append(Paragraph(f"<b>{rec.get('recommendation', '')}</b>", normal_style))
                content.append(Paragraph(f"<i>Rationale:</i> {rec.get('rationale', '')}", normal_style))
                content.append(Paragraph(f"<i>Implications:</i> {rec.get('potentialImplications', '')}", normal_style))
                content.append(Spacer(1, 0.1*inch))
        else:
            content.append(Paragraph("No strategic recommendations provided.", normal_style))
        content.append(Spacer(1, 0.25*inch))
        
        # Next Steps
        content.append(Paragraph("Next Steps", heading_style))
        next_steps = analysis_data.get("nextStepsAndConsiderations", [])
        if next_steps:
            for i, step in enumerate(next_steps, 1):
                content.append(Paragraph(f"{i}. {step}", normal_style))
                content.append(Spacer(1, 0.05*inch))
        else:
            content.append(Paragraph("No next steps provided.", normal_style))
        content.append(Spacer(1, 0.25*inch))
        
        # Original Plan
        content.append(Paragraph("Original Architecture Plan", heading_style))
        content.append(Paragraph(markdown_plan, normal_style))
        
        # Build the PDF
        doc.build(content)
        
        logger.info(f"Generated PDF report: {output_path}")
        return output_path
    
    def generate_html_report(self, 
                            analysis_data: Dict[str, Any], 
                            markdown_plan: str, 
                            model_used: str) -> str:
        """Generate an HTML report of the architecture analysis.
        
        Args:
            analysis_data: The analysis data dictionary
            markdown_plan: The original architecture plan
            model_used: The model used for analysis
            
        Returns:
            Path to the generated HTML file
        """
        output_path = self._generate_filename("architecture_analysis", "html")
        
        # Create templates directory if it doesn't exist
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        # Check if template exists, create it if not
        template_path = os.path.join(templates_dir, 'report_template.html')
        if not os.path.exists(template_path):
            self._create_default_html_template(template_path)
            
        # Prepare template data
        template_data = {
            "app_title": APP_TITLE,
            "generated_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            "model_used": model_used,
            "analysis": analysis_data,
            "original_plan": markdown_plan,
            "primary_color": PDF_THEME.get("primary_color", "#667eea"),
            "secondary_color": PDF_THEME.get("secondary_color", "#764ba2"),
        }
        
        # Render template
        template = self.jinja_env.get_template('report_template.html')
        html_content = template.render(**template_data)
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML report: {output_path}")
        return output_path

    def _create_default_html_template(self, template_path: str) -> None:
        """Create a default HTML template file if it doesn't exist."""
        default_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_title }} - Report</title>
    <style>
        :root {
            --primary-color: {{ primary_color }};
            --secondary-color: {{ secondary_color }};
            --text-color: #333333;
            --background-color: #ffffff;
            --light-bg-color: #f8f9fa;
            --border-color: #dee2e6;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
            margin: 0;
            padding: 0;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        h1, h2, h3 {
            color: var(--secondary-color);
        }
        
        .section {
            background-color: var(--light-bg-color);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .metadata {
            font-style: italic;
            margin-bottom: 15px;
            color: #666;
        }
        
        .strength, .improvement, .recommendation, .next-step {
            padding: 15px;
            border-left: 4px solid var(--primary-color);
            background-color: rgba(var(--primary-color-rgb), 0.05);
            margin-bottom: 15px;
        }
        
        .strength h4, .improvement h4, .recommendation h4 {
            margin-top: 0;
            color: var(--primary-color);
        }
        
        .severity {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
            color: white;
        }
        
        .severity-CRITICAL { background-color: #dc3545; }
        .severity-HIGH { background-color: #fd7e14; }
        .severity-MEDIUM { background-color: #ffc107; color: #212529; }
        .severity-LOW { background-color: #28a745; }
        
        .label {
            font-weight: bold;
        }
        
        .original-plan {
            font-family: monospace;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #dee2e6;
        }
        
        @media print {
            .no-print {
                display: none;
            }
            
            .section {
                break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ app_title }}</h1>
            <h2>Architecture Analysis Report</h2>
        </div>
        
        <div class="metadata">
            <p>Generated: {{ generated_date }} | Model: {{ model_used }}</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <p>{{ analysis.summaryOfReviewerObservations }}</p>
        </div>
        
        <div class="section">
            <h2>System Plan Overview</h2>
            <p>{{ analysis.planSummary }}</p>
        </div>
        
        <div class="section">
            <h2>Strengths</h2>
            {% if analysis.strengths %}
                {% for strength in analysis.strengths %}
                <div class="strength">
                    <h4>{{ strength.dimension }}</h4>
                    <p><span class="label">Point:</span> {{ strength.point }}</p>
                    <p><span class="label">Rationale:</span> {{ strength.reason }}</p>
                </div>
                {% endfor %}
            {% else %}
                <p>No strengths identified.</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>Areas for Improvement</h2>
            {% if analysis.areasForImprovement %}
                {% for area in analysis.areasForImprovement %}
                <div class="improvement">
                    <h4>{{ area.area }} <span class="severity severity-{{ area.severity }}">{{ area.severity }}</span></h4>
                    <p><span class="label">Concern:</span> {{ area.concern }}</p>
                    <p><span class="label">Suggestion:</span> {{ area.suggestion }}</p>
                    <p><span class="label">Impact:</span> {{ area.impact }}</p>
                    {% if area.tradeOffsConsidered %}
                    <p><span class="label">Trade-offs:</span> {{ area.tradeOffsConsidered }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <p>No areas for improvement identified.</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>Strategic Recommendations</h2>
            {% if analysis.strategicRecommendations %}
                {% for rec in analysis.strategicRecommendations %}
                <div class="recommendation">
                    <h4>{{ rec.recommendation }}</h4>
                    <p><span class="label">Rationale:</span> {{ rec.rationale }}</p>
                    <p><span class="label">Implications:</span> {{ rec.potentialImplications }}</p>
                </div>
                {% endfor %}
            {% else %}
                <p>No strategic recommendations provided.</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>Next Steps</h2>
            {% if analysis.nextStepsAndConsiderations %}
                <ol>
                    {% for step in analysis.nextStepsAndConsiderations %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ol>
            {% else %}
                <p>No next steps provided.</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>Original Architecture Plan</h2>
            <div class="original-plan">{{ original_plan }}</div>
        </div>
        
        <div class="no-print" style="text-align: center; margin-top: 40px;">
            <button onclick="window.print()">Print/Save as PDF</button>
        </div>
    </div>
</body>
</html>'''
        
        # Create templates directory if it doesn't exist
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        # Write template file
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(default_template)
        
        logger.info(f"Created default HTML template: {template_path}")
    
    def generate_markdown_report(self, 
                               analysis_data: Dict[str, Any], 
                               markdown_plan: str, 
                               model_used: str) -> str:
        """Generate a Markdown report of the architecture analysis.
        
        Args:
            analysis_data: The analysis data dictionary
            markdown_plan: The original architecture plan
            model_used: The model used for analysis
            
        Returns:
            Path to the generated Markdown file
        """
        output_path = self._generate_filename("architecture_analysis", "md")
        
        # Build markdown content
        md_content = []
        
        # Header
        md_content.append(f"# {APP_TITLE}")
        md_content.append("## Architecture Analysis Report")
        md_content.append("")
        
        # Metadata
        md_content.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        md_content.append(f"**Model Used:** {model_used}")
        md_content.append("")
        
        # Executive Summary
        md_content.append("## Executive Summary")
        md_content.append(analysis_data.get("summaryOfReviewerObservations", "No summary provided."))
        md_content.append("")
        
        # Plan Summary
        md_content.append("## System Plan Overview")
        md_content.append(analysis_data.get("planSummary", "No summary provided."))
        md_content.append("")
        
        # Strengths
        md_content.append("## Strengths")
        strengths = analysis_data.get("strengths", [])
        if strengths:
            for strength in strengths:
                md_content.append(f"### {strength.get('dimension', '')}")
                md_content.append(f"**Point:** {strength.get('point', '')}")
                md_content.append(f"**Rationale:** {strength.get('reason', '')}")
                md_content.append("")
        else:
            md_content.append("No strengths identified.")
            md_content.append("")
        
        # Areas for Improvement
        md_content.append("## Areas for Improvement")
        areas = analysis_data.get("areasForImprovement", [])
        if areas:
            for area in areas:
                md_content.append(f"### {area.get('area', '')} - {area.get('severity', '').upper()}")
                md_content.append(f"**Concern:** {area.get('concern', '')}")
                md_content.append(f"**Suggestion:** {area.get('suggestion', '')}")
                md_content.append(f"**Impact:** {area.get('impact', '')}")
                
                if area.get("tradeOffsConsidered"):
                    md_content.append(f"**Trade-offs:** {area.get('tradeOffsConsidered', '')}")
                
                md_content.append("")
        else:
            md_content.append("No areas for improvement identified.")
            md_content.append("")
        
        # Strategic Recommendations
        md_content.append("## Strategic Recommendations")
        recommendations = analysis_data.get("strategicRecommendations", [])
        if recommendations:
            for rec in recommendations:
                md_content.append(f"### {rec.get('recommendation', '')}")
                md_content.append(f"**Rationale:** {rec.get('rationale', '')}")
                md_content.append(f"**Implications:** {rec.get('potentialImplications', '')}")
                md_content.append("")
        else:
            md_content.append("No strategic recommendations provided.")
            md_content.append("")
        
        # Next Steps
        md_content.append("## Next Steps")
        next_steps = analysis_data.get("nextStepsAndConsiderations", [])
        if next_steps:
            for i, step in enumerate(next_steps, 1):
                md_content.append(f"{i}. {step}")
        else:
            md_content.append("No next steps provided.")
        md_content.append("")
        
        # Original Plan
        md_content.append("## Original Architecture Plan")
        md_content.append("```markdown")
        md_content.append(markdown_plan)
        md_content.append("```")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        
        logger.info(f"Generated Markdown report: {output_path}")
        return output_path
    
    def generate_base64_pdf(self,
                           analysis_data: Dict[str, Any], 
                           markdown_plan: str, 
                           model_used: str) -> str:
        """Generate a PDF report and return it as a base64 string.
        
        Args:
            analysis_data: The analysis data dictionary
            markdown_plan: The original architecture plan
            model_used: The model used for analysis
            
        Returns:
            Base64 encoded PDF content
        """
        pdf_path = self.generate_pdf_report(analysis_data, markdown_plan, model_used)
        
        # Read the PDF file and convert to base64
        with open(pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
            base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
        
        return base64_pdf


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing or replacing unsafe characters.
    
    Args:
        filename: The original filename
        
    Returns:
        Sanitized filename
    """
    # Replace characters that are unsafe for filenames
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    return filename

# Export format constants
PDF_FORMAT = "PDF"
HTML_FORMAT = "HTML" 
MARKDOWN_FORMAT = "Markdown"
