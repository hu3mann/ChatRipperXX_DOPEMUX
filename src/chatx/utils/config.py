"""Configuration management for ChatX."""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = Field(..., description="LLM provider name")
    model: Optional[str] = Field(None, description="Model identifier")
    api_key: Optional[str] = Field(None, description="API key (use env var in production)")
    base_url: Optional[str] = Field(None, description="Base URL for API")
    max_retries: int = Field(3, description="Maximum retry attempts")
    timeout: int = Field(60, description="Request timeout in seconds")


class RedactionConfig(BaseModel):
    """Privacy redaction configuration."""
    strict_mode: bool = Field(True, description="Enable strict redaction mode")
    policy_file: Optional[Path] = Field(None, description="Path to privacy policy file")
    generate_report: bool = Field(True, description="Generate redaction reports")
    fail_on_leak: bool = Field(True, description="Fail if privacy leaks detected")


class Config(BaseModel):
    """Main ChatX configuration."""
    
    # General settings
    verbose: bool = Field(False, description="Enable verbose output")
    output_dir: Path = Field(Path("./output"), description="Default output directory")
    temp_dir: Optional[Path] = Field(None, description="Temporary directory")
    
    # LLM settings
    llm: LLMConfig = Field(
        default_factory=lambda: LLMConfig(provider="local"),
        description="LLM configuration"
    )
    
    # Privacy settings
    redaction: RedactionConfig = Field(
        default_factory=RedactionConfig,
        description="Redaction configuration"
    )
    
    # Processing settings
    batch_size: int = Field(10, description="Default batch size for processing")
    max_workers: int = Field(4, description="Maximum parallel workers")
    
    @classmethod
    def load(cls, config_path: Union[str, Path]) -> "Config":
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Config instance
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with config_path.open() as f:
                data = json.load(f)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}") from e
        except Exception as e:
            raise ValueError(f"Error loading config: {e}") from e
    
    def save(self, config_path: Union[str, Path]) -> None:
        """Save configuration to file.
        
        Args:
            config_path: Path where to save configuration
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with config_path.open("w") as f:
            json.dump(self.dict(), f, indent=2, default=str)
    
    @classmethod
    def default(cls) -> "Config":
        """Create default configuration.
        
        Returns:
            Config instance with default values
        """
        return cls()


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Load configuration from file or create default.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Config instance
    """
    if config_path is None:
        # Look for config in standard locations
        candidates = [
            Path("./chatx.json"),
            Path("~/.config/chatx/config.json").expanduser(),
            Path("~/.chatx.json").expanduser(),
        ]
        
        for candidate in candidates:
            if candidate.exists():
                config_path = candidate
                break
    
    if config_path and Path(config_path).exists():
        return Config.load(config_path)
    else:
        return Config.default()