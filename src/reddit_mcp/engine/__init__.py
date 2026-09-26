"""
Reddit automation engine package.
"""

from reddit_mcp.engine.browser import BrowserPoolManager
from reddit_mcp.engine.mouse import MouseController
from reddit_mcp.engine.keyboard import KeyboardController
from reddit_mcp.engine.locators import RedditLocators
from reddit_mcp.engine.client import RedditAutomationClient

__all__ = [
    "BrowserPoolManager",
    "MouseController",
    "KeyboardController",
    "RedditLocators",
    "RedditAutomationClient",
]
