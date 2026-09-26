"""
Reddit MCP (Model Context Protocol) Server.
Standalone human-mimetic behavioral automation server for Reddit.
"""

from reddit_mcp.config import RedditConfig
from reddit_mcp.engine.client import RedditAutomationClient
from reddit_mcp.server import RedditMcpServer

__version__ = "0.1.0"
__all__ = ["RedditConfig", "RedditAutomationClient", "RedditMcpServer", "__version__"]
