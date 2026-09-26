"""
Command-line interface entry point for Reddit MCP server.
"""

import asyncio
import logging
import sys
from reddit_mcp.server import RedditMcpServer
from reddit_mcp.config import RedditConfig


def main() -> None:
    """Configures logging and starts the stdio MCP server."""
    # Ensure stdout is exclusively reserved for JSON-RPC messages; logs go to stderr
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    config = RedditConfig()
    server = RedditMcpServer(config)

    try:
        asyncio.run(server.run_stdio())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Reddit MCP server stopped by user.")


if __name__ == "__main__":
    main()
