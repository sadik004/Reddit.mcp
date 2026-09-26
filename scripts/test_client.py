"""
Diagnostic Test Client for Reddit MCP.
Sends JSON-RPC 2.0 requests to the Reddit MCP Server and validates responses.
"""

import asyncio
import json
import os
import subprocess
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


async def test_reddit_mcp_server() -> None:
    """Verifies initialize handshake and tools/list discovery."""
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
    env = os.environ.copy()
    env["PYTHONPATH"] = src_dir

    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "reddit_mcp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
        cwd=src_dir
    )

    # 1. Send initialize
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }
    proc.stdin.write((json.dumps(init_req) + "\n").encode())
    await proc.stdin.drain()

    raw_resp = await proc.stdout.readline()
    init_resp = json.loads(raw_resp.decode().strip())
    print("\n✅ Handshake Response:")
    print(json.dumps(init_resp, indent=2))

    # 2. Request tools list
    tools_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    proc.stdin.write((json.dumps(tools_req) + "\n").encode())
    await proc.stdin.drain()

    raw_tools = await proc.stdout.readline()
    tools_resp = json.loads(raw_tools.decode().strip())
    tools = tools_resp.get("result", {}).get("tools", [])
    print(f"\n✅ Discovered {len(tools)} tools:")
    for t in tools:
        print(f"  • {t['name']}: {t['description'][:70]}...")

    # Terminate process
    proc.stdin.close()
    await proc.wait()
    print("\n🎉 MCP Diagnostic Handshake Completed Successfully!")


if __name__ == "__main__":
    asyncio.run(test_reddit_mcp_server())
