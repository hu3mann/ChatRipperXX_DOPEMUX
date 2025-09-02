"""Simple Ollama client for query module to avoid complex dependencies."""

import logging
import json
from dataclasses import dataclass
from typing import Any

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)


@dataclass
class SimpleLLMConfig:
    """Simple configuration for LLM client."""
    model_name: str = "gemma2:9b-instruct-q4_K_M"
    temperature: float = 0.3
    max_output_tokens: int = 800
    timeout_seconds: int = 30
    ollama_base_url: str = "http://localhost:11434"


class SimpleOllamaClient:
    """Simple Ollama client for query processing."""
    
    def __init__(self, config: SimpleLLMConfig | None = None):
        """Initialize simple Ollama client.
        
        Args:
            config: LLM configuration
        """
        self.config = config or SimpleLLMConfig()
        
        if requests is None:
            raise ImportError("requests library required for Ollama client")
        
        logger.info(f"Initialized simple Ollama client with model: {self.config.model_name}")
    
    def generate(self, prompt: str) -> str:
        """Generate text using Ollama.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        try:
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_output_tokens,
                    "stop": ["Human:", "Assistant:", "Q:", "A:", "Question:", "Answer:"],
                }
            }
            
            response = requests.post(
                f"{self.config.ollama_base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
        
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {e}")
            raise
    
    def close(self) -> None:
        """Close client (no-op for requests-based client)."""
        pass