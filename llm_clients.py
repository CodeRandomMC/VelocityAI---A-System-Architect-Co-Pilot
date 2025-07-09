"""
LLM client implementations for Google GenAI and LM Studio.
"""

import json
import requests
from typing import Dict, Any, List, Tuple
from google import genai
from google.genai import types

from config import GOOGLE_API_KEY, DEFAULT_LM_STUDIO_HOST
from core_logic import ARCHITECT_SYSTEM_PROMPT


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass


class GoogleGenAIClient:
    """Client for Google GenAI API."""
    
    def __init__(self):
        """Initialize the Google GenAI client."""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Google GenAI client with error handling."""
        try:
            self.client = genai.Client(api_key=GOOGLE_API_KEY)
        except (ValueError, AssertionError) as e:
            print(f"WARNING: Could not initialize Google GenAI Client. Google GenAI features will be disabled.")
            print(f"Details: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if the client is available."""
        return self.client is not None
    
    def generate_analysis(self, markdown_plan: str, model_choice: str) -> str:
        """
        Generate architecture analysis using Google GenAI.
        
        Args:
            markdown_plan: The architecture plan to analyze
            model_choice: The model to use for analysis
            
        Returns:
            JSON response as string
            
        Raises:
            LLMClientError: If the client is not available or API call fails
        """
        if not self.client:
            raise LLMClientError("Google GenAI client not initialized. Please check your GOOGLE_API_KEY.")
        
        try:
            config = types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
                system_instruction=ARCHITECT_SYSTEM_PROMPT
            )
            
            full_prompt = f"Please analyze this architecture plan:\n\n{markdown_plan}"
            
            response = self.client.models.generate_content(
                model=f'models/{model_choice}',
                contents=full_prompt,
                config=config
            )
            
            return response.text or ""
        except Exception as e:
            raise LLMClientError(f"Google GenAI API error: {str(e)}")


class LMStudioClient:
    """Client for LM Studio local API."""
    
    def __init__(self, host: str = DEFAULT_LM_STUDIO_HOST):
        """Initialize the LM Studio client."""
        self.host = host
        self.base_url = self._get_base_url(host)
    
    def _get_base_url(self, host: str) -> str:
        """Construct the LM Studio base URL from host."""
        if not host.startswith("http"):
            host = f"http://{host}"
        if not host.endswith("/v1"):
            host = f"{host}/v1"
        return host
    
    def update_host(self, host: str):
        """Update the host and base URL."""
        self.host = host
        self.base_url = self._get_base_url(host)
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to LM Studio and return status.
        
        Returns:
            Tuple of (is_connected, status_message)
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                model_count = len(models.get("data", []))
                return True, f"✅ Connected successfully. Found {model_count} models."
            else:
                return False, f"❌ Connection failed: HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"❌ Cannot connect to LM Studio at {self.host}. Please ensure LM Studio is running."
        except requests.exceptions.Timeout:
            return False, f"❌ Connection timeout to {self.host}."
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """
        Get available models from LM Studio.
        
        Returns:
            List of available model names
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                return [model["id"] for model in models.get("data", [])]
            else:
                return ["local-model"]  # Fallback
        except:
            return ["local-model"]  # Fallback if LM Studio is not running
    
    def generate_analysis(self, markdown_plan: str, model_choice: str) -> str:
        """
        Generate architecture analysis using LM Studio.
        
        Args:
            markdown_plan: The architecture plan to analyze
            model_choice: The model to use for analysis
            
        Returns:
            JSON response as string
            
        Raises:
            LLMClientError: If the API call fails
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            # Format the prompt for chat completion
            messages = [
                {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
                {"role": "user", "content": f"Please analyze this architecture plan:\n\n{markdown_plan}"}
            ]
            
            # Define the JSON schema for the expected response format
            json_schema = {
                "type": "object",
                "properties": {
                    "summaryOfReviewerObservations": {
                        "type": "string",
                        "description": "A concise executive summary of the overall architectural strengths and key areas for focus"
                    },
                    "planSummary": {
                        "type": "string", 
                        "description": "Brief summary of what the system does as understood by Archimedes"
                    },
                    "strengths": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "dimension": {"type": "string"},
                                "point": {"type": "string"},
                                "reason": {"type": "string"}
                            },
                            "required": ["dimension", "point", "reason"]
                        }
                    },
                    "areasForImprovement": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "area": {"type": "string"},
                                "concern": {"type": "string"},
                                "suggestion": {"type": "string"},
                                "severity": {"type": "string", "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]},
                                "impact": {"type": "string"},
                                "tradeOffsConsidered": {"type": "string"}
                            },
                            "required": ["area", "concern", "suggestion", "severity"]
                        }
                    },
                    "strategicRecommendations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "recommendation": {"type": "string"},
                                "rationale": {"type": "string"},
                                "potentialImplications": {"type": "string"}
                            },
                            "required": ["recommendation", "rationale"]
                        }
                    },
                    "nextStepsAndConsiderations": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["summaryOfReviewerObservations", "planSummary", "strengths", "areasForImprovement", "strategicRecommendations", "nextStepsAndConsiderations"]
            }

            payload: Dict[str, Any] = {
                "model": model_choice,
                "messages": messages,
                "temperature": 0.2,
                "stream": False,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "architecture_analysis",
                        "schema": json_schema,
                        "strict": True
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120  # 2 minute timeout for local processing
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise LLMClientError(f"LM Studio API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise LLMClientError(f"Cannot connect to LM Studio at {self.host}. Please ensure LM Studio is running.")
        except requests.exceptions.Timeout:
            raise LLMClientError("LM Studio request timed out. The model might be too slow or the request too complex.")
        except Exception as e:
            raise LLMClientError(f"LM Studio API error: {str(e)}")


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create_google_client() -> GoogleGenAIClient:
        """Create a Google GenAI client."""
        return GoogleGenAIClient()
    
    @staticmethod
    def create_lm_studio_client(host: str = DEFAULT_LM_STUDIO_HOST) -> LMStudioClient:
        """Create an LM Studio client."""
        return LMStudioClient(host)
