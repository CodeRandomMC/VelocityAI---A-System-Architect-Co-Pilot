"""
Configuration constants and settings for VelocityAI - A Systems Architect Toolset.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model constants
GEMINI_FLASH = 'gemini-2.5-flash'
GEMINI_PRO = 'gemini-2.5-pro'

# LM Studio configuration
DEFAULT_LM_STUDIO_HOST = "localhost:1234"
LM_STUDIO_MODELS = ["local-model"]

# App configuration
APP_TITLE = "VelocityAI - A Systems Architect Toolset"
APP_PORT = 7860
APP_HOST = "0.0.0.0"

# Google API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Export configuration
EXPORT_FORMATS = ["PDF", "HTML", "Markdown"]
DEFAULT_EXPORT_FORMAT = "PDF"
EXPORT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
PDF_THEME = {
    "title_font": "Helvetica-Bold",
    "header_font": "Helvetica-Bold",
    "body_font": "Helvetica",
    "title_size": 24,
    "header_size": 16,
    "body_size": 11,
    "primary_color": "#667eea",
    "secondary_color": "#764ba2",
    "text_color": "#333333",
    "page_margin": 50,  # Points
    "logo_path": None,  # Set to a path if you want to include a logo
}
