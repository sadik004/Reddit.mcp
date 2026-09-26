"""
Unit tests for Reddit MCP Server protocol handling.
"""

import pytest
from reddit_mcp.server import RedditMcpServer
from reddit_mcp.config import RedditConfig


@pytest.mark.asyncio
async def test_mcp_initialize() -> None:
    server = RedditMcpServer(RedditConfig())
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    resp = await server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "reddit-mcp"
    assert "tools" in resp["result"]["capabilities"]


@pytest.mark.asyncio
async def test_mcp_tools_list() -> None:
    server = RedditMcpServer(RedditConfig())
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    resp = await server.handle_request(req)
    assert resp is not None
    tools = resp["result"]["tools"]
    assert len(tools) >= 15

    tool_names = [t["name"] for t in tools]
    assert "reddit_auth_status" in tool_names
    assert "reddit_get_profile" in tool_names
    assert "reddit_update_profile" in tool_names
    assert "reddit_submit_post" in tool_names
    assert "reddit_submit_comment" in tool_names
    assert "reddit_vote" in tool_names
    assert "reddit_save_post" in tool_names
    assert "reddit_read_thread" in tool_names
    assert "reddit_browse_subreddit" in tool_names
    assert "reddit_browse_user" in tool_names
    assert "reddit_search" in tool_names
    assert "reddit_send_message" in tool_names
    assert "reddit_check_inbox" in tool_names
    assert "reddit_hunt_leads" in tool_names
    assert "reddit_generate_pitch" in tool_names


@pytest.mark.asyncio
async def test_mcp_pitch_generator_tool_call() -> None:
    server = RedditMcpServer(RedditConfig())
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "reddit_generate_pitch",
            "arguments": {
                "post_id": "t3_test",
                "title": "Need help scraping dynamic infinite scroll page",
                "author": "target_client",
                "subreddit": "webscraping",
                "url": "https://reddit.com/r/webscraping/comments/test",
                "urgency_score": 8,
                "budget_intent": "High",
                "pain_points": ["Infinite scroll pagination issue"],
                "recommended_strategy": "Dynamic DOM wait"
            }
        }
    }
    resp = await server.handle_request(req)
    assert resp is not None
    assert "error" not in resp
    content = resp["result"]["content"][0]["text"]
    assert "behavioral-playwright" in content
    assert "target_client" in content


@pytest.mark.asyncio
async def test_mcp_unauthenticated_write_fast_fail() -> None:
    # Point to a guaranteed non-existent storage state
    config = RedditConfig(storage_state="non_existent_file.json")
    server = RedditMcpServer(config)
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "reddit_submit_post",
            "arguments": {
                "target": "r/test",
                "title": "Automated Test Post",
                "body": "Test Body Content"
            }
        }
    }
    resp = await server.handle_request(req)
    assert resp is not None
    assert "error" not in resp
    content = resp["result"]["content"][0]["text"]
    assert "Authentication required" in content
