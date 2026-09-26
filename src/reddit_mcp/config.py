"""
Configuration settings for Reddit MCP.
"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedditConfig(BaseSettings):
    """Configuration settings for Reddit MCP Server."""
    
    model_config = SettingsConfigDict(
        env_prefix="REDDIT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    storage_state: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "storage_state.json",
        description="Path to Playwright storage_state.json containing auth cookies"
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode"
    )
    proxy_server: Optional[str] = Field(
        default=None,
        description="Proxy URL (e.g. http://127.0.0.1:8080)"
    )
    proxy_username: Optional[str] = Field(
        default=None,
        description="Proxy authentication username"
    )
    proxy_password: Optional[str] = Field(
        default=None,
        description="Proxy authentication password"
    )
    navigation_timeout_ms: int = Field(
        default=30000,
        description="Navigation timeout in milliseconds"
    )
    typing_min_delay_ms: int = Field(
        default=35,
        description="Minimum keystroke delay for human-like typing"
    )
    typing_max_delay_ms: int = Field(
        default=115,
        description="Maximum keystroke delay for human-like typing"
    )
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        description="Default browser User-Agent string"
    )
    viewport_width: int = Field(default=1920, description="Default browser viewport width")
    viewport_height: int = Field(default=1080, description="Default browser viewport height")
