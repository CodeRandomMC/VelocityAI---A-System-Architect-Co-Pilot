import os
import json
import gradio as gr
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- Configuration and Setup ---
load_dotenv()

# Initialize Google GenAI client with error handling
try:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
except (ValueError, AssertionError) as e:
    print(f"WARNING: Could not initialize Google GenAI Client. Google GenAI features will be disabled.")
    print(f"Details: {e}")
    client = None

# Model constants
GEMINI_FLASH = 'gemini-2.5-flash'
GEMINI_PRO = 'gemini-2.5-pro'

# LM Studio configuration
DEFAULT_LM_STUDIO_HOST = "localhost:1234"
LM_STUDIO_MODELS = ["local-model"]  # This will be populated dynamically if needed

def get_lm_studio_base_url(host: str) -> str:
    """Construct the LM Studio base URL from host"""
    if not host.startswith("http"):
        host = f"http://{host}"
    if not host.endswith("/v1"):
        host = f"{host}/v1"
    return host

# The specialized system prompt for our Architecture Reviewer
ARCHITECT_SYSTEM_PROMPT = """
You are an expert Senior Principal Systems Architect with 20+ years of experience designing large-scale distributed systems. Your role is to review system architecture plans and provide detailed, actionable feedback.

When reviewing an architecture plan, analyze it across these dimensions:
1. **Scalability**: Can the system handle growth in users, data, and traffic?
2. **Reliability**: Are there single points of failure? What's the disaster recovery plan?
3. **Security**: Are there potential vulnerabilities? Is data properly protected?
4. **Performance**: Will the system meet performance requirements under load?
5. **Maintainability**: Is the code/system easy to modify and extend?
6. **Cost Efficiency**: Are resources used optimally?
7. **Observability**: Can you monitor, debug, and troubleshoot effectively?

Provide your analysis in this exact JSON format:
{
  "planSummary": "Brief 2-3 sentence summary of what the system does",
  "strengths": [
    {"point": "Specific strength", "reason": "Why this is good"}
  ],
  "areasForImprovement": [
    {
      "area": "Specific area (e.g., Database Design)",
      "concern": "What the problem is",
      "suggestion": "Specific actionable recommendation",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW"
    }
  ],
  "actionableKeyPoints": [
    "Specific next steps to take"
  ]
}

Be specific, practical, and focus on actionable recommendations. Consider real-world constraints and trade-offs.
"""

# --- Helper Functions for Different Providers ---

def call_gemini(markdown_plan: str, model_choice: str):
    """Call Google Gemini API"""
    if not client:
        raise Exception("Google GenAI client not initialized. Please check your GOOGLE_API_KEY.")
    
    config = types.GenerateContentConfig(
        temperature=0.2,
        response_mime_type="application/json",
        system_instruction=ARCHITECT_SYSTEM_PROMPT
    )
    
    full_prompt = f"Please analyze this architecture plan:\n\n{markdown_plan}"
    
    response = client.models.generate_content(
        model=f'models/{model_choice}',
        contents=full_prompt,
        config=config
    )
    
    return response.text or ""

def call_lm_studio(markdown_plan: str, model_choice: str, host: str = DEFAULT_LM_STUDIO_HOST):
    """Call LM Studio local API using OpenAI-compatible format"""
    try:
        lm_studio_base_url = get_lm_studio_base_url(host)
        
        # LM Studio uses OpenAI-compatible API format
        headers = {
            "Content-Type": "application/json"
        }
        
        # Format the prompt for chat completion
        messages = [
            {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Please analyze this architecture plan:\n\n{markdown_plan}"}
        ]
        
        payload: Dict[str, Any] = {
            "model": model_choice,
            "messages": messages,
            "temperature": 0.2,
            "stream": False,
            "response_format": {"type": "json_object"}  # Request JSON format
        }
        
        response = requests.post(
            f"{lm_studio_base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120  # 2 minute timeout for local processing
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"LM Studio API error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        raise Exception(f"Cannot connect to LM Studio at {host}. Please ensure LM Studio is running.")
    except requests.exceptions.Timeout:
        raise Exception("LM Studio request timed out. The model might be too slow or the request too complex.")
    except Exception as e:
        raise Exception(f"LM Studio API error: {str(e)}")

def get_available_lm_studio_models(host: str = DEFAULT_LM_STUDIO_HOST) -> List[str]:
    """Get available models from LM Studio"""
    try:
        lm_studio_base_url = get_lm_studio_base_url(host)
        response = requests.get(f"{lm_studio_base_url}/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            return [model["id"] for model in models.get("data", [])]
        else:
            return ["local-model"]  # Fallback
    except:
        return ["local-model"]  # Fallback if LM Studio is not running

def test_lm_studio_connection(host: str) -> tuple[bool, str]:
    """Test connection to LM Studio and return status"""
    try:
        lm_studio_base_url = get_lm_studio_base_url(host)
        response = requests.get(f"{lm_studio_base_url}/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            model_count = len(models.get("data", []))
            return True, f"✅ Connected successfully. Found {model_count} models."
        else:
            return False, f"❌ Connection failed: HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"❌ Cannot connect to LM Studio at {host}. Please ensure LM Studio is running."
    except requests.exceptions.Timeout:
        return False, f"❌ Connection timeout to {host}."
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# --- The Backend Logic  ---

def analyze_architecture(markdown_plan: str, model_choice: str, provider: str, lm_studio_host: str = DEFAULT_LM_STUDIO_HOST):
    """
    Analyzes the architecture plan using either Google GenAI or LM Studio
    based on the selected provider.
    """
    if not markdown_plan.strip():
        gr.Warning("Please enter an architecture plan to analyze.")
        return "Please enter an architecture plan to analyze."

    # Show a loading message in the UI immediately
    yield f"🤖 Analyzing your plan with {model_choice} via {provider}..."

    response_text = ""  # Initialize to avoid unbound variable issues
    
    try:
        # Call the appropriate provider
        if provider == "Google GenAI":
            response_text = call_gemini(markdown_plan, model_choice)
        elif provider == "LM Studio (Local)":
            response_text = call_lm_studio(markdown_plan, model_choice, lm_studio_host)
        else:
            yield f"**Error:** Unknown provider: {provider}"
            return
        
        if not response_text:
            yield "**Error:** Empty response from AI model. Please try again."
            return
            
        analysis_json = json.loads(response_text)

        # --- Format the JSON into beautiful markdown for display ---
        output_md = f"## 📝 Architecture Analysis (via {model_choice})\n\n"
        output_md += f"### 📜 Plan Summary\n{analysis_json['planSummary']}\n\n"
        
        if analysis_json.get('strengths'):
            output_md += f"### ✅ Strengths\n"
            for item in analysis_json['strengths']:
                output_md += f"- **{item['point']}:** {item['reason']}\n"
        
        if analysis_json.get('areasForImprovement'):
            output_md += f"\n### 🔍 Areas for Improvement\n"
            # Sort by severity to show critical items first
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            sorted_improvements = sorted(analysis_json['areasForImprovement'], key=lambda x: severity_order.get(x['severity'], 99))
            
            for item in sorted_improvements:
                output_md += f"- **[{item['severity']}] {item['area']}**\n"
                output_md += f"  - **Concern:** {item['concern']}\n"
                output_md += f"  - **Suggestion:** {item['suggestion']}\n"
        
        if analysis_json.get('actionableKeyPoints'):
            output_md += f"\n### 🚀 Actionable Key Points\n"
            for point in analysis_json['actionableKeyPoints']:
                output_md += f"- {point}\n"
        
        yield output_md

    except json.JSONDecodeError:
        gr.Error("The AI returned an invalid JSON response. This can happen with complex inputs.")
        yield f"**Error:** The AI response could not be parsed as JSON. Please try a slightly different input or a more powerful model.\n\n**Raw Response:**\n```\n{response_text}\n```"
    except Exception as e:
        gr.Error(f"An unexpected error occurred: {str(e)}")
        yield f"An unexpected error occurred: {str(e)}"

# --- 3. Example Plan for the UI ---
EXAMPLE_PLAN = """
# Project: Real-time User Analytics Dashboard

## 1. Overview
This system will track user clicks on a website and display them on a real-time dashboard.

## 2. Components
- **Frontend:** A React single-page application (SPA).
- **API:** A single Node.js monolith running on a single EC2 instance. It will have two endpoints:
  - `POST /event`: Receives click data.
  - `GET /dashboard`: Uses websockets to push data to the frontend.
- **Database:** A PostgreSQL database on the same EC2 instance as the API. It stores all click events in a single table.

## 3. Data Flow
1. User clicks on the website.
2. React app sends a request to `POST /event`.
3. The Node.js API writes the event to the PostgreSQL database.
4. The API also pushes the event over a websocket to all connected dashboard clients.
"""

# --- 4. Gradio UI ---
# Custom CSS for full-page layout
custom_css = """
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

with gr.Blocks(css=custom_css, title="VelocityAI - A Systems Architect Toolset") as demo:
    with gr.Column(elem_classes="main-header"):
        gr.Markdown("# 🚀 VelocityAI - A Systems Architect Toolset")
        gr.Markdown("Enter your system architecture plan in Markdown. The AI will analyze it for scalability, reliability, security, and more.")
    
    with gr.Row():
        with gr.Column(scale=1, elem_classes="input-section"):
            gr.Markdown("## 📝 Input")
            
            # Provider selection
            provider_selector = gr.Radio(
                ["Google GenAI", "LM Studio (Local)"],
                label="🔌 Inference Provider",
                value="Google GenAI",
                info="Choose between cloud (Google) or local (LM Studio) inference.",
                elem_classes="model-selector"
            )
            
            # LM Studio configuration section (initially hidden)
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
            
            # Model selection - will be updated based on provider
            model_selector = gr.Radio(
                [GEMINI_FLASH, GEMINI_PRO],
                label="🔧 Select Model",
                value=GEMINI_PRO,
                info="Pro is more thorough but slower; Flash is faster.",
                elem_classes="model-selector"
            )
            
            def update_model_choices(provider: str, host: str = DEFAULT_LM_STUDIO_HOST):
                if provider == "Google GenAI":
                    return gr.Radio(
                        choices=[GEMINI_FLASH, GEMINI_PRO],
                        value=GEMINI_PRO,
                        label="🔧 Select Model",
                        info="Pro is more thorough but slower; Flash is faster."
                    )
                else:  # LM Studio
                    lm_models = get_available_lm_studio_models(host)
                    return gr.Radio(
                        choices=lm_models,
                        value=lm_models[0] if lm_models else "local-model",
                        label="🔧 Select Model",
                        info="Local models from LM Studio. Make sure LM Studio is running."
                    )
            
            def update_ui_visibility(provider: str):
                """Update UI visibility based on provider selection"""
                show_lm_config = provider == "LM Studio (Local)"
                return gr.Column(visible=show_lm_config)
            
            def test_connection(host: str):
                """Test connection to LM Studio"""
                _, message = test_lm_studio_connection(host)
                return message
            
            def refresh_models_for_host(host: str):
                """Refresh available models from LM Studio for a specific host"""
                models = get_available_lm_studio_models(host)
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
            
            def update_models_on_host_change(provider: str, host: str):
                """Update models when host changes for LM Studio"""
                if provider == "LM Studio (Local)":
                    return refresh_models_for_host(host)
                else:
                    return gr.Radio()  # No change for other providers
            
            # Event handlers
            provider_selector.change(
                fn=update_ui_visibility,
                inputs=provider_selector,
                outputs=lm_studio_config
            )
            
            provider_selector.change(
                fn=update_model_choices,
                inputs=[provider_selector, lm_studio_host],
                outputs=model_selector
            )
            
            test_connection_btn.click(
                fn=test_connection,
                inputs=lm_studio_host,
                outputs=connection_status
            )
            
            refresh_models_btn.click(
                fn=refresh_models_for_host,
                inputs=lm_studio_host,
                outputs=model_selector
            )
            
            # Auto-refresh models when host changes
            lm_studio_host.change(
                fn=update_models_on_host_change,
                inputs=[provider_selector, lm_studio_host],
                outputs=model_selector
            )
            
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
            
        with gr.Column(scale=1, elem_classes="output-section"):
            gr.Markdown("## 📊 Analysis Results")
            output_analysis = gr.Markdown(
                label="",
                value="Click 'Analyze Plan' to get started...",
                elem_id="output-analysis"
            )

    submit_button.click(
        fn=analyze_architecture,
        inputs=[input_markdown, model_selector, provider_selector, lm_studio_host],
        outputs=output_analysis
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        inbrowser=True,
        favicon_path=None,
        ssl_verify=False
    )