"""
Main application entry point for the GenAI Architecture Reviewer.
"""

import json
import gradio as gr
from typing import Generator, List

from config import APP_HOST, APP_PORT, GEMINI_FLASH, GEMINI_PRO, DEFAULT_LM_STUDIO_HOST
from core_logic import validate_input, parse_analysis_response, format_analysis_response
from llm_clients import LLMClientFactory, LLMClientError
from ui_components import UIComponents, create_gradio_interface


class ArchitectureAnalyzer:
    """Main application class for architecture analysis."""
    
    def __init__(self):
        """Initialize the application."""
        self.google_client = LLMClientFactory.create_google_client()
        self.lm_studio_client = LLMClientFactory.create_lm_studio_client()
        self.ui = UIComponents()
    
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
            yield "Please enter an architecture plan to analyze."
            return

        # Show loading message
        yield f"🤖 Analyzing your plan with {model_choice} via {provider}..."

        response_text = ""  # Initialize to avoid unbound variable issues
        
        try:
            # Get the appropriate client and generate analysis
            if provider == "Google GenAI":
                if not self.google_client.is_available():
                    yield "**Error:** Google GenAI client not available. Please check your API key."
                    return
                response_text = self.google_client.generate_analysis(markdown_plan, model_choice)
            elif provider == "LM Studio (Local)":
                # Update host if it has changed
                if lm_studio_host != self.lm_studio_client.host:
                    self.lm_studio_client.update_host(lm_studio_host)
                response_text = self.lm_studio_client.generate_analysis(markdown_plan, model_choice)
            else:
                yield f"**Error:** Unknown provider: {provider}"
                return

            # Parse and format the response
            analysis_json = parse_analysis_response(response_text)
            formatted_output = format_analysis_response(analysis_json, model_choice)
            yield formatted_output

        except json.JSONDecodeError:
            gr.Error("The AI returned an invalid JSON response. This can happen with complex inputs.")
            yield f"**Error:** The AI response could not be parsed as JSON. Please try a slightly different input or a more powerful model.\n\n**Raw Response:**\n```\n{response_text}\n```"
        except LLMClientError as e:
            gr.Error(f"LLM Client error: {str(e)}")
            yield f"**Error:** {str(e)}"
        except Exception as e:
            gr.Error(f"An unexpected error occurred: {str(e)}")
            yield f"**Error:** An unexpected error occurred: {str(e)}"
    
    def test_lm_studio_connection(self, host: str) -> str:
        """Test connection to LM Studio."""
        # Update host if it has changed
        if host != self.lm_studio_client.host:
            self.lm_studio_client.update_host(host)
        
        _, message = self.lm_studio_client.test_connection()
        return message
    
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
                    output_analysis = self.ui.create_output_section()
            
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
