"""
Gradio UI components and styling for the Architecture Reviewer application.
"""

import gradio as gr
from typing import List, Tuple

from config import GEMINI_FLASH, GEMINI_PRO, DEFAULT_LM_STUDIO_HOST
from core_logic import EXAMPLE_PLAN


# Custom CSS for full-page layout
CUSTOM_CSS = """
.gradio-container {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 20px !important;
}

.main-header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.input-section {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    border: 1px solid #dee2e6;
}

.output-section {
    background: #ffffff;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #dee2e6;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.model-selector {
    margin-bottom: 15px;
}

.analyze-button {
    width: 100%;
    padding: 12px;
    font-size: 16px;
    margin-top: 15px;
}

.lm-studio-config {
    background: #f0f8ff;
    border: 1px solid #b6d7ff;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
}

.connection-status {
    font-size: 14px;
    padding: 8px;
    border-radius: 4px;
    margin-top: 10px;
}

footer {
    display: none !important;
}

/* Make the layout responsive */
@media (max-width: 768px) {
    .gradio-container {
        padding: 10px !important;
    }
}
"""


class UIComponents:
    """Container for UI components and their event handlers."""
    
    def __init__(self):
        """Initialize UI components."""
        self.lm_studio_client = None
        self.google_client = None
        
    def create_header(self) -> gr.Column:
        """Create the main header section."""
        with gr.Column(elem_classes="main-header") as header:
            gr.Markdown("# 🤖 GenAI Architecture Reviewer")
            gr.Markdown("Enter your system architecture plan in Markdown. The AI will analyze it for scalability, reliability, security, and more.")
        return header
    
    def create_provider_selector(self) -> gr.Radio:
        """Create the provider selection radio buttons."""
        return gr.Radio(
            ["Google GenAI", "LM Studio (Local)"],
            label="🔌 Inference Provider",
            value="Google GenAI",
            info="Choose between cloud (Google) or local (LM Studio) inference.",
            elem_classes="model-selector"
        )
    
    def create_lm_studio_config(self) -> Tuple[gr.Column, gr.Textbox, gr.Button, gr.Markdown, gr.Button]:
        """Create the LM Studio configuration section."""
        with gr.Column(visible=False) as lm_studio_config:
            gr.Markdown("### 🔧 LM Studio Configuration")
            
            with gr.Row():
                lm_studio_host = gr.Textbox(
                    label="LM Studio Host",
                    value=DEFAULT_LM_STUDIO_HOST,
                    placeholder="localhost:1234",
                    info="Enter the host:port where LM Studio is running",
                    scale=3
                )
                test_connection_btn = gr.Button(
                    "Test Connection",
                    variant="secondary",
                    scale=1
                )
            
            connection_status = gr.Markdown(
                value="Click 'Test Connection' to verify LM Studio is running.",
                elem_id="connection-status"
            )
            
            refresh_models_btn = gr.Button(
                "🔄 Refresh Models",
                variant="secondary",
                size="sm"
            )
        
        return lm_studio_config, lm_studio_host, test_connection_btn, connection_status, refresh_models_btn
    
    def create_model_selector(self) -> gr.Radio:
        """Create the model selection radio buttons."""
        return gr.Radio(
            [GEMINI_FLASH, GEMINI_PRO],
            label="🔧 Select Model",
            value=GEMINI_PRO,
            info="Pro is more thorough but slower; Flash is faster.",
            elem_classes="model-selector"
        )
    
    def create_input_section(self) -> Tuple[gr.Code, gr.Button]:
        """Create the input section with markdown editor and submit button."""
        input_markdown = gr.Code(
            label="📋 Architecture Plan (Markdown)", 
            language="markdown",
            value=EXAMPLE_PLAN, 
            lines=30,
            max_lines=50
        )
        
        submit_button = gr.Button(
            "🚀 Analyze Plan", 
            variant="primary",
            elem_classes="analyze-button"
        )
        
        return input_markdown, submit_button
    
    def create_output_section(self) -> gr.Markdown:
        """Create the output section for displaying results."""
        gr.Markdown("## 📊 Analysis Results")
        return gr.Markdown(
            label="",
            value="Click 'Analyze Plan' to get started...",
            elem_id="output-analysis"
        )
    
    def update_model_choices(self, provider: str, lm_studio_models: List[str]) -> gr.Radio:
        """Update model choices based on provider selection."""
        if provider == "Google GenAI":
            return gr.Radio(
                choices=[GEMINI_FLASH, GEMINI_PRO],
                value=GEMINI_PRO,
                label="🔧 Select Model",
                info="Pro is more thorough but slower; Flash is faster."
            )
        else:  # LM Studio
            return gr.Radio(
                choices=lm_studio_models,
                value=lm_studio_models[0] if lm_studio_models else "local-model",
                label="🔧 Select Model",
                info="Local models from LM Studio. Make sure LM Studio is running."
            )
    
    def update_ui_visibility(self, provider: str) -> gr.Column:
        """Update UI visibility based on provider selection."""
        show_lm_config = provider == "LM Studio (Local)"
        return gr.Column(visible=show_lm_config)
    
    def refresh_models_display(self, models: List[str]) -> gr.Radio:
        """Refresh the model display with new models."""
        if models and models != ["local-model"]:
            return gr.Radio(
                choices=models,
                value=models[0],
                label="🔧 Select Model",
                info="Local models from LM Studio. Make sure LM Studio is running."
            )
        else:
            return gr.Radio(
                choices=["local-model"],
                value="local-model",
                label="🔧 Select Model",
                info="No models found. Please check your LM Studio connection."
            )


def create_gradio_interface() -> gr.Blocks:
    """Create the main Gradio interface."""
    return gr.Blocks(css=CUSTOM_CSS, title="GenAI Architecture Reviewer")
