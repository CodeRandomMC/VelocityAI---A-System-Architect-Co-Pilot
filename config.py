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
