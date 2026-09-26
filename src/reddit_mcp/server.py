"""
JSON-RPC 2.0 Stdio Model Context Protocol (MCP) Server for Reddit.
Engineered for cross-platform reliability, including Windows ProactorEventLoop compatibility.
"""

from __future__ import annotations
import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional
from pydantic import BaseModel

from reddit_mcp.config import RedditConfig
from reddit_mcp.engine.client import RedditAutomationClient
from reddit_mcp.tools.registry import ToolRegistry

logger = logging.getLogger("reddit_mcp.server")


class RedditMcpServer:
    """Production-grade MCP stdio server implementation."""

    def __init__(self, config: Optional[RedditConfig] = None):
        self.config = config or RedditConfig()
        self.client = RedditAutomationClient(self.config)
        self.registry = ToolRegistry(self.client)

    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processes an incoming JSON-RPC 2.0 request."""
        method = request.get("method")
        msg_id = request.get("id")
        params = request.get("params", {})

        # Handle Notifications (no response required)
        if method in ("notifications/initialized", "$/cancelRequest"):
            return None

        # 1. Initialize Handshake
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        }
                    },
                    "serverInfo": {
                        "name": "reddit-mcp",
                        "version": "0.1.0"
                    }
                }
            }

        # 2. Tools Discovery
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": self.registry.get_tools_manifest()
                }
            }

        # 3. Tool Execution
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            try:
                raw_result = await self.registry.execute_tool(tool_name, arguments)
                if isinstance(raw_result, BaseModel):
                    output_text = raw_result.model_dump_json(indent=2)
                elif isinstance(raw_result, (dict, list)):
                    output_text = json.dumps(raw_result, indent=2, default=str)
                else:
                    output_text = str(raw_result)

                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": output_text
                            }
                        ]
                    }
                }
            except Exception as exc:
                logger.exception(f"Error executing tool '{tool_name}'")
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "isError": True,
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error executing tool '{tool_name}': {str(exc)}"
                            }
                        ]
                    }
                }

        # 4. Ping
        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {}
            }

        # Method Not Found
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not found"
            }
        }

    async def run_stdio(self) -> None:
        """Runs the MCP server over standard input and output streams."""
        loop = asyncio.get_running_loop()

        while True:
            # Thread-pool executor reading avoids Windows ProactorEventLoop pipe deadlocks
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break

            line_str = line.strip()
            if not line_str:
                continue

            try:
                request = json.loads(line_str)
                response = await self.handle_request(request)
                if response is not None:
                    response_json = json.dumps(response)
                    sys.stdout.write(response_json + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError as exc:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Invalid JSON received: {exc}"
                    }
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
            except Exception as exc:
                logger.exception("Unexpected server runtime error")
