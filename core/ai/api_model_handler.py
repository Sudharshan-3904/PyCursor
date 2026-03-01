"""
Multi-Provider Cloud AI Integration Module.
Provides a unified interface for interacting with various commercial LLM APIs
including OpenAI (GPT series), Anthropic (Claude series), and Google (Gemini series).
"""

import os
from typing import Optional, Iterator, Union
from dataclasses import dataclass

@dataclass
class APIConfig:
    """
    Configuration parameters for cloud-based inference.
    Maps provider-specific requirements to a standardized internal format.
    """
    provider: str
    api_key: str
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2000

class APIModelHandler:
    """
    High-level orchestrator for cloud AI services.
    Handles client lazy-loading, credential management, and response streaming.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        Initializes the handler. Clients are deferred until active usage.
        """
        self.config = config
        self._openai = None
        self._anthropic = None
        self._gemini = None
        
    def set_config(self, config: APIConfig):
        """
        Standardizes on a single configuration injection point and resets active client handles.
        """
        self.config = config
        self._openai = self._anthropic = self._gemini = None

    def configure(self, provider: str, api_key: Optional[str] = None, model_name: Optional[str] = None, **kwargs) -> bool:
        """
        Convenience method to update configuration from raw parameters.
        Returns True if configuration was successful.
        """
        try:
            if not api_key:
                api_key = self.env_key_resolver(provider)
            
            if not model_name:
                models = self.get_supported_models(provider)
                model_name = models[0] if models else "gpt-4o"

            new_config = APIConfig(
                provider=provider,
                api_key=api_key or "",
                model_name=model_name,
                **kwargs
            )
            self.set_config(new_config)
            return True
        except Exception as e:
            print(f"[API Error] Configuration failed: {e}")
            return False

    def _get_openai_client(self):
        """
        Internal resolver for the OpenAI SDK client.
        """
        if self._openai is None:
            import openai
            self._openai = openai.OpenAI(api_key=self.config.api_key)
        return self._openai
    
    def _get_anthropic_client(self):
        """
        Internal resolver for the Anthropic SDK client.
        """
        if self._anthropic is None:
            import anthropic
            self._anthropic = anthropic.Anthropic(api_key=self.config.api_key)
        return self._anthropic
    
    def _get_gemini_client(self):
        """
        Internal resolver for the Google Generative AI model handle.
        """
        if self._gemini is None:
            import google.generativeai as genai
            genai.configure(api_key=self.config.api_key)
            self._gemini = genai.GenerativeModel(self.config.model_name)
        return self._gemini
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Main entry point for generating static (non-streaming) completions.
        Standardizes system prompt retrieval from assets if not provided.
        """
        if not self.config: raise ValueError("API Config not initialized.")
        
        if system_prompt is None:
            from core.utilities.utils import load_systemPrompt
            system_prompt = load_systemPrompt("generalPrompt.txt")
            
        provider = self.config.provider.lower()
        if provider == 'openai': return self._openai_request(prompt, system_prompt)
        if provider == 'anthropic': return self._anthropic_request(prompt, system_prompt)
        if provider == 'gemini': return self._gemini_request(prompt, system_prompt)
        
        raise ValueError(f"Provider '{provider}' is not currently supported.")
    
    def _openai_request(self, prompt: str, system: Optional[str]) -> str:
        """
        Executes a completion request against OpenAI's chat completions API.
        """
        messages = [{"role": "system", "content": system}] if system else []
        messages.append({"role": "user", "content": prompt})
        
        resp = self._get_openai_client().chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        return resp.choices[0].message.content
    
    def _anthropic_request(self, prompt: str, system: Optional[str]) -> str:
        """
        Executes a completion request against Anthropic's Messages API.
        """
        payload = {
            "model": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system: payload["system"] = system
        
        resp = self._get_anthropic_client().messages.create(**payload)
        return resp.content[0].text
    
    def _gemini_request(self, prompt: str, system: Optional[str]) -> str:
        """
        Executes a completion request against Google's Generative AI API.
        """
        full_input = f"{system}\n\n{prompt}" if system else prompt
        resp = self._get_gemini_client().generate_content(
            full_input,
            generation_config={"temperature": self.config.temperature, "max_output_tokens": self.config.max_tokens}
        )
        return resp.text

    @staticmethod
    def get_supported_models(provider: str) -> list:
        """
        Returns a hardcoded registry of recommended models for each supported cloud provider.
        """
        registry = {
            'openai': ['gpt-4-turbo-preview', 'gpt-4', 'gpt-4o', 'gpt-3.5-turbo'],
            'anthropic': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
            'gemini': ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
        }
        return registry.get(provider.lower(), [])

    @staticmethod
    def env_key_resolver(provider: str) -> Optional[str]:
        """
        Utility for retrieving API keys from standard environment variable names.
        """
        mapping = {'openai': 'OPENAI_API_KEY', 'anthropic': 'ANTHROPIC_API_KEY', 'gemini': 'GOOGLE_API_KEY'}
        return os.getenv(mapping.get(provider.lower(), ''))
