"""
Main application entry point for VelocityAI - A Systems Architect Toolset.
"""

import os
import json
import gradio as gr
import bleach
from typing import Generator, List, Dict, Any, Optional, Tuple

from config import (APP_HOST, APP_PORT, GEMINI_FLASH, GEMINI_PRO, 
                   DEFAULT_LM_STUDIO_HOST, EXPORT_FORMATS, DEFAULT_EXPORT_FORMAT)
from core_logic import validate_input, parse_analysis_response, format_analysis_response
from llm_clients import LLMClientFactory, LLMClientError
from ui_components import UIComponents, create_gradio_interface
from export_utils import ExportManager


def sanitize_markdown_output(content: str) -> str:
    """
    Sanitize markdown content to prevent XSS attacks.
    
    This function removes potentially dangerous HTML tags and attributes
    while preserving safe markdown formatting.
    
    Args:
        content (str): The raw markdown content from LLM
        
    Returns:
        str: Sanitized markdown content safe for rendering
    """
    # Define allowed HTML tags for markdown formatting
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',  # Headers
        'p', 'br', 'hr',                       # Paragraphs and breaks
        'strong', 'b', 'em', 'i', 'u', 's',   # Text formatting
        'ul', 'ol', 'li',                      # Lists
        'blockquote', 'pre', 'code',           # Code and quotes
        'table', 'thead', 'tbody', 'tr', 'th', 'td',  # Tables
        'a',                                   # Links (with limited attributes)
    ]
    
    # Define allowed attributes for specific tags
    allowed_attributes = {
        'a': ['href', 'title'],
        'code': ['class'],  # For syntax highlighting
        'pre': ['class'],   # For code blocks
    }
    
    # Sanitize the content
    cleaned_content = bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True  # Remove disallowed tags completely
    )
    
    # Additional protection: ensure URLs in links are safe
    cleaned_content = bleach.linkify(
        cleaned_content,
        callbacks=[bleach.callbacks.nofollow]  # Add rel="nofollow" to external links
    )
    
    return cleaned_content


class ArchitectureAnalyzer:
    """Main application class for architecture analysis."""
    
    def __init__(self):
        """Initialize the application."""
        self.google_client = LLMClientFactory.create_google_client()
        self.lm_studio_client = LLMClientFactory.create_lm_studio_client()
        self.ui = UIComponents()
        self.export_manager = ExportManager()
        self.last_analysis_result = None  # Store the last analysis result for export
    
    def analyze_architecture(self, markdown_plan: str, model_choice: str, provider: str, lm_studio_host: str = DEFAULT_LM_STUDIO_HOST) -> Generator[str, None, None]:
        """
        Analyze the architecture plan using the selected provider.
        
        Args:
            markdown_plan: The architecture plan in markdown format
            model_choice: The model to use for analysis
            provider: The provider to use ("Google GenAI" or "LM Studio (Local)")
            lm_studio_host: The LM Studio host (for local provider)
            
        Yields:
            Status messages and final analysis result
        """
        if not validate_input(markdown_plan):
            gr.Warning("Please enter an architecture plan to analyze.")
            yield sanitize_markdown_output("Please enter an architecture plan to analyze.")
            return

        # Show loading message
        yield sanitize_markdown_output(f"🤖 Analyzing your plan with {model_choice} via {provider}...")

        response_text = ""  # Initialize to avoid unbound variable issues
        self.last_analysis_result = None  # Reset last analysis result
        
        try:
            # Get the appropriate client and generate analysis
            if provider == "Google GenAI":
                if not self.google_client.is_available():
                    yield sanitize_markdown_output("**Error:** Google GenAI client not available. Please check your API key.")
                    return
                response_text = self.google_client.generate_analysis(markdown_plan, model_choice)
            elif provider == "LM Studio (Local)":
                # Update host if it has changed
                if lm_studio_host != self.lm_studio_client.host:
                    self.lm_studio_client.update_host(lm_studio_host)
                response_text = self.lm_studio_client.generate_analysis(markdown_plan, model_choice)
            else:
                yield sanitize_markdown_output(f"**Error:** Unknown provider: {provider}")
                return

            # Parse and format the response
            analysis_json = parse_analysis_response(response_text)
            formatted_output = format_analysis_response(analysis_json, model_choice)
            
            # Store the analysis results and original plan for export
            self.last_analysis_result = {
                "analysis_data": analysis_json,
                "markdown_plan": markdown_plan,
                "model_used": model_choice
            }
            
            yield sanitize_markdown_output(formatted_output)

        except json.JSONDecodeError:
            gr.Error("The AI returned an invalid JSON response. This can happen with complex inputs.")
            yield sanitize_markdown_output(f"**Error:** The AI response could not be parsed as JSON. Please try a slightly different input or a more powerful model.\n\n**Raw Response:**\n```\n{response_text}\n```")
        except LLMClientError as e:
            gr.Error(f"LLM Client error: {str(e)}")
            yield sanitize_markdown_output(f"**Error:** {str(e)}")
        except Exception as e:
            gr.Error(f"An unexpected error occurred: {str(e)}")
            yield sanitize_markdown_output(f"**Error:** An unexpected error occurred: {str(e)}")
    
    def test_lm_studio_connection(self, host: str) -> str:
        """Test connection to LM Studio."""
        # Update host if it has changed
        if host != self.lm_studio_client.host:
            self.lm_studio_client.update_host(host)
        
        _, message = self.lm_studio_client.test_connection()
        return sanitize_markdown_output(message)
    
    def get_lm_studio_models(self, host: str = DEFAULT_LM_STUDIO_HOST) -> List[str]:
        """Get available models from LM Studio."""
        # Update host if it has changed
        if host != self.lm_studio_client.host:
            self.lm_studio_client.update_host(host)
        
        return self.lm_studio_client.get_available_models()
    
    def update_model_choices(self, provider: str, host: str = DEFAULT_LM_STUDIO_HOST):
        """Update model choices based on provider selection."""
        if provider == "Google GenAI":
            return self.ui.update_model_choices(provider, [GEMINI_FLASH, GEMINI_PRO])
        else:  # LM Studio
            models = self.get_lm_studio_models(host)
            return self.ui.update_model_choices(provider, models)
    
    def refresh_models_for_host(self, host: str):
        """Refresh available models from LM Studio for a specific host."""
        models = self.get_lm_studio_models(host)
        return self.ui.refresh_models_display(models)
    
    def update_models_on_host_change(self, provider: str, host: str):
        """Update models when host changes for LM Studio."""
        if provider == "LM Studio (Local)":
            return self.refresh_models_for_host(host)
        else:
            return gr.Radio()  # No change for other providers
    
    def export_analysis_result(self, format_choice: str) -> str:
        """
        Export the last analysis result to the selected format.
        
        Args:
            format_choice: The format to export to (e.g., PDF, PNG, etc.)
            
        Returns:
            str: File path or URL to the exported file
        """
        if not self.last_analysis_result:
            return sanitize_markdown_output("**Error:** No analysis result available to export. Please run an analysis first.")
        
        # Get the export format class
        export_format = next((ef for ef in EXPORT_FORMATS if ef["label"] == format_choice), None)
        
        if not export_format:
            return sanitize_markdown_output(f"**Error:** Unknown export format: {format_choice}")
        
        try:
            # Perform the export
            file_path = self.export_manager.export_to_format(self.last_analysis_result, export_format["value"])
            return sanitize_markdown_output(f"✅ Export successful! [Download here]({file_path})")
        except Exception as e:
            return sanitize_markdown_output(f"**Error:** Failed to export analysis result: {str(e)}")
    
    def export_analysis(self, format_choice: str) -> str:
        """
        Export the last analysis result in the specified format.
        
        Args:
            format_choice: The format to export as (PDF, HTML, Markdown)
            
        Returns:
            Status message with path to the exported file
        """
        if not self.last_analysis_result:
            return sanitize_markdown_output("⚠️ No analysis results available for export. Please run an analysis first.")
        
        try:
            # Get export format data
            if format_choice not in EXPORT_FORMATS:
                return sanitize_markdown_output(f"⚠️ Unsupported export format: {format_choice}. Supported formats: {', '.join(EXPORT_FORMATS)}")
            
            # Extract data from last analysis
            analysis_data = self.last_analysis_result["analysis_data"]
            markdown_plan = self.last_analysis_result["markdown_plan"]
            model_used = self.last_analysis_result["model_used"]
            
            # Export to the selected format
            file_path = self.export_manager.export_analysis(
                analysis_data=analysis_data,
                markdown_plan=markdown_plan,
                model_used=model_used,
                export_format=format_choice
            )
            
            # Return a success message with file path
            if os.path.exists(file_path):
                return sanitize_markdown_output(f"✅ Analysis exported successfully as {format_choice}!\n\nFile saved to: `{file_path}`")
            else:
                return sanitize_markdown_output(f"⚠️ Export completed but file not found at: {file_path}")
                
        except Exception as e:
            return sanitize_markdown_output(f"⚠️ Export failed: {str(e)}")
    
    def get_export_preview(self, format_choice: str = "PDF") -> str:
        """
        Get a preview or download link for the export.
        
        Args:
            format_choice: The format to preview
            
        Returns:
            HTML content with preview or download link
        """
        if not self.last_analysis_result:
            return sanitize_markdown_output("⚠️ No analysis results available for preview. Please run an analysis first.")
        
        try:
            # Extract data from last analysis
            analysis_data = self.last_analysis_result["analysis_data"]
            markdown_plan = self.last_analysis_result["markdown_plan"]
            model_used = self.last_analysis_result["model_used"]
            
            # For PDF, generate a base64 preview
            if format_choice == "PDF":
                base64_pdf = self.export_manager.generate_base64_pdf(
                    analysis_data=analysis_data,
                    markdown_plan=markdown_plan,
                    model_used=model_used
                )
                
                # Return HTML with embedded PDF preview
                preview_html = f"""
                <div style="text-align: center;">
                    <h3>PDF Preview</h3>
                    <embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf">
                    <p>If the preview doesn't work, you can export the PDF using the export button.</p>
                </div>
                """
                return preview_html
            
            else:
                # For other formats, just show a message
                return sanitize_markdown_output(f"Preview not available for {format_choice} format. Use the export button to save the file.")
                
        except Exception as e:
            return sanitize_markdown_output(f"⚠️ Preview generation failed: {str(e)}")
    
    def create_app(self) -> gr.Blocks:
        """Create the main Gradio application."""
        with create_gradio_interface() as demo:
            # Create header
            self.ui.create_header()
            
            with gr.Row():
                # Input section
                with gr.Column(scale=1, elem_classes="input-section"):
                    gr.Markdown("## 📝 Input")
                    
                    # Provider selection
                    provider_selector = self.ui.create_provider_selector()
                    
                    # LM Studio configuration
                    lm_studio_config, lm_studio_host, test_connection_btn, connection_status, refresh_models_btn = self.ui.create_lm_studio_config()
                    
                    # Model selection
                    model_selector = self.ui.create_model_selector()
                    
                    # Input section
                    input_markdown, submit_button = self.ui.create_input_section()
                
                # Output section
                with gr.Column(scale=1, elem_classes="output-section"):
                    output_analysis, export_row, export_format, export_button, export_result = self.ui.create_output_section()
            
            # Event handlers
            provider_selector.change(
                fn=self.ui.update_ui_visibility,
                inputs=provider_selector,
                outputs=lm_studio_config
            )
            
            provider_selector.change(
                fn=self.update_model_choices,
                inputs=[provider_selector, lm_studio_host],
                outputs=model_selector
            )
            
            test_connection_btn.click(
                fn=self.test_lm_studio_connection,
                inputs=lm_studio_host,
                outputs=connection_status
            )
            
            refresh_models_btn.click(
                fn=self.refresh_models_for_host,
                inputs=lm_studio_host,
                outputs=model_selector
            )
            
            # Auto-refresh models when host changes
            lm_studio_host.change(
                fn=self.update_models_on_host_change,
                inputs=[provider_selector, lm_studio_host],
                outputs=model_selector
            )
            
            # Main analysis function
            submit_button.click(
                fn=self.analyze_architecture,
                inputs=[input_markdown, model_selector, provider_selector, lm_studio_host],
                outputs=output_analysis
            )
            
            # Clear any export preview when new analysis is run
            submit_button.click(
                fn=lambda: gr.HTML(value="", visible=False),
                inputs=[],
                outputs=export_result
            )
            
            # Export button click handler
            export_button.click(
                fn=self.export_analysis,
                inputs=export_format,
                outputs=export_result
            )
            
            # Show export result when clicked
            export_button.click(
                fn=lambda: gr.HTML(visible=True),
                inputs=[],
                outputs=export_result
            )
            
            # Hide export result when format changes
            export_format.change(
                fn=lambda x: gr.HTML(visible=False),
                inputs=export_format,
                outputs=export_result
            )
        
        return demo


def main():
    """Main entry point for the application."""
    app = ArchitectureAnalyzer()
    demo = app.create_app()
    
    demo.launch(
        server_name=APP_HOST,
        server_port=APP_PORT,
        share=False,
        debug=True,
        show_error=True,
        inbrowser=True,
        favicon_path=None,
        ssl_verify=False
    )


if __name__ == "__main__":
    main()
