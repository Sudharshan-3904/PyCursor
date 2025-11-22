"""
API Model Handler for OpenAI, Anthropic, and Google Gemini
Supports multiple API providers with unified interface
"""

import os
from typing import Optional, Iterator, Union
from dataclasses import dataclass


@dataclass
class APIConfig:
    """Configuration for API models"""
    provider: str
    api_key: str
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2000


class APIModelHandler:
    """Unified handler for API-based LLM providers"""
    
    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config
        self._openai_client = None
        self._anthropic_client = None
        self._gemini_client = None
        
    def set_config(self, config: APIConfig):
        """Update the API configuration"""
        self.config = config
        self._openai_client = None
        self._anthropic_client = None
        self._gemini_client = None

    def configure(self, provider: str, api_key: Optional[str], model_name: Optional[str] = None) -> bool:
        """
        Configure the handler with provider details.
        Returns True if successful.
        """
        try:
            if not model_name:
                defaults = {
                    'openai': 'gpt-4',
                    'anthropic': 'claude-3-opus-20240229',
                    'gemini': 'gemini-pro'
                }
                model_name = defaults.get(provider, 'gpt-3.5-turbo')

            config = APIConfig(
                provider=provider,
                api_key=api_key if api_key else self.load_api_key_from_env(provider),
                model_name=model_name
            )
            self.set_config(config)
            return True
        except Exception as e:
            print(f"Configuration error: {e}")
            return False
    
    def _get_openai_client(self):
        """Lazy initialization of OpenAI client"""
        if self._openai_client is None:
            try:
                import openai
                self._openai_client = openai.OpenAI(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
            except Exception as e:
                raise Exception(f"Failed to initialize OpenAI client: {e}")
        return self._openai_client
    
    def _get_anthropic_client(self):
        """Lazy initialization of Anthropic client"""
        if self._anthropic_client is None:
            try:
                import anthropic
                self._anthropic_client = anthropic.Anthropic(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
            except Exception as e:
                raise Exception(f"Failed to initialize Anthropic client: {e}")
        return self._anthropic_client
    
    def _get_gemini_client(self):
        """Lazy initialization of Google Gemini client"""
        if self._gemini_client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.config.api_key)
                self._gemini_client = genai.GenerativeModel(self.config.model_name)
            except ImportError:
                raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")
            except Exception as e:
                raise Exception(f"Failed to initialize Gemini client: {e}")
        return self._gemini_client
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the configured API provider
        
        Args:
            prompt: User prompt/question
            system_prompt: Optional system prompt for context
            
        Returns:
            Generated response as string
        """
        if not self.config:
            raise ValueError("API configuration not set. Call set_config() first.")
        
        if self.config.provider == 'openai':
            return self._openai_response(prompt, system_prompt)
        elif self.config.provider == 'anthropic':
            return self._anthropic_response(prompt, system_prompt)
        elif self.config.provider == 'gemini':
            return self._gemini_response(prompt, system_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    def _openai_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using OpenAI API"""
        client = self._get_openai_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def _anthropic_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Anthropic Claude API"""
        client = self._get_anthropic_client()
        
        try:
            kwargs = {
                "model": self.config.model_name,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")
    
    def _gemini_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Google Gemini API"""
        model = self._get_gemini_client()
        
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": self.config.temperature,
                    "max_output_tokens": self.config.max_tokens,
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {e}")
    
    def stream_response(self, prompt: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """
        Stream response from API (for real-time display)
        
        Args:
            prompt: User prompt/question
            system_prompt: Optional system prompt
            
        Yields:
            Response chunks as they arrive
        """
        if not self.config:
            raise ValueError("API configuration not set")
        
        if self.config.provider == 'openai':
            yield from self._openai_stream(prompt, system_prompt)
        elif self.config.provider == 'anthropic':
            yield from self._anthropic_stream(prompt, system_prompt)
        elif self.config.provider == 'gemini':
            yield from self._gemini_stream(prompt, system_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    def _openai_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """Stream response from OpenAI"""
        client = self._get_openai_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"[OpenAI Stream Error: {e}]"
    
    def _anthropic_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """Stream response from Anthropic"""
        client = self._get_anthropic_client()
        
        try:
            kwargs = {
                "model": self.config.model_name,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            with client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"[Anthropic Stream Error: {e}]"
    
    def _gemini_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """Stream response from Gemini"""
        model = self._get_gemini_client()
        
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": self.config.temperature,
                    "max_output_tokens": self.config.max_tokens,
                },
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"[Gemini Stream Error: {e}]"
    
    @staticmethod
    def get_available_models(provider: str) -> list[str]:
        """Get list of available models for a provider"""
        models = {
            'openai': [
                'gpt-4-turbo-preview',
                'gpt-4',
                'gpt-3.5-turbo',
                'gpt-3.5-turbo-16k'
            ],
            'anthropic': [
                'claude-3-opus-20240229',
                'claude-3-sonnet-20240229',
                'claude-3-haiku-20240307',
                'claude-2.1',
                'claude-2.0'
            ],
            'gemini': [
                'gemini-pro',
                'gemini-pro-vision',
                'gemini-1.5-pro',
                'gemini-1.5-flash'
            ]
        }
        return models.get(provider, [])
    
    @staticmethod
    def load_api_key_from_env(provider: str) -> Optional[str]:
        """Load API key from environment variables"""
        env_vars = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'gemini': 'GOOGLE_API_KEY'
        }
        env_var = env_vars.get(provider)
        if env_var:
            return os.getenv(env_var)
        return None
