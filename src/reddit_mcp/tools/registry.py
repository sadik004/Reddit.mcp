"""
Tool Registry and Dispatcher for Reddit MCP.
Exposes 16 typed, human-mimetic tools for Claude, Antigravity, Cursor, and any MCP client.
"""

import asyncio
from typing import Dict, Any, List, Callable, Awaitable
from reddit_mcp.engine.client import RedditAutomationClient
from reddit_mcp.models.dtos import (
    RedditProfileUpdateDTO,
    RedditPostSubmissionDTO,
    RedditCommentSubmissionDTO,
    RedditSendMessageDTO,
    RedditLeadDTO,
)


class ToolRegistry:
    """Registry maintaining tool schemas and executing handler functions."""

    def __init__(self, client: RedditAutomationClient):
        self.client = client
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[Any]]] = {}
        self._register_all_tools()

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Awaitable[Any]]
    ) -> None:
        """Registers an individual MCP tool."""
        self._tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": parameters,
        }
        self._handlers[name] = handler

    def get_tools_manifest(self) -> List[Dict[str, Any]]:
        """Returns the list of tool definitions for tools/list."""
        return list(self._tools.values())

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Executes a registered tool by name with arguments."""
        if name not in self._handlers:
            raise ValueError(f"Unknown tool: {name}")
        res = self._handlers[name](arguments)
        if asyncio.iscoroutine(res):
            return await res
        return res

    def _register_all_tools(self) -> None:
        """Registers all 16 human-mimetic Reddit tools."""

        # 1. reddit_auth_status
        self.register_tool(
            name="reddit_auth_status",
            description="Verify current Reddit session validity, extracting authenticated username, karma, and notification metrics.",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            handler=lambda args: self.client.check_auth()
        )

        # 2. reddit_get_profile
        self.register_tool(
            name="reddit_get_profile",
            description="Retrieve detailed profile information (display name, bio, karma breakdown, cake day, social links) for a user or current profile ('me').",
            parameters={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Reddit username to inspect, or 'me' / omitted for own authenticated profile"
                    }
                },
                "required": []
            },
            handler=lambda args: self.client.get_profile(args.get("username"))
        )

        # 3. reddit_update_profile
        self.register_tool(
            name="reddit_update_profile",
            description="Update own profile settings (display name, about bio description, NSFW flag) with human-mimetic typing.",
            parameters={
                "type": "object",
                "properties": {
                    "display_name": {"type": "string", "description": "New custom display name"},
                    "bio": {"type": "string", "description": "New bio / about text (max 200 chars)"},
                    "is_nsfw": {"type": "boolean", "description": "Toggle profile 18+ NSFW tag"}
                },
                "required": []
            },
            handler=lambda args: self.client.update_profile(RedditProfileUpdateDTO(**args))
        )

        # 4. reddit_submit_post
        self.register_tool(
            name="reddit_submit_post",
            description="Publish a post (text/markdown or link) to any subreddit or own profile ('u/me').",
            parameters={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Subreddit name (e.g. 'webscraping', 'Python') or 'u/me' for own profile"},
                    "title": {"type": "string", "description": "Post title"},
                    "body": {"type": "string", "description": "Post markdown body (for text posts)"},
                    "url": {"type": "string", "description": "Target destination URL (for link posts)"},
                    "flair": {"type": "string", "description": "Post flair text"},
                    "is_nsfw": {"type": "boolean", "default": False},
                    "is_spoiler": {"type": "boolean", "default": False}
                },
                "required": ["target", "title"]
            },
            handler=lambda args: self.client.submit_post(RedditPostSubmissionDTO(**args))
        )

        # 5. reddit_submit_comment
        self.register_tool(
            name="reddit_submit_comment",
            description="Submit a top-level comment on a post or a nested reply to an existing comment with human typing cadence.",
            parameters={
                "type": "object",
                "properties": {
                    "post_id_or_url": {"type": "string", "description": "Post identifier (t3_...) or permalink URL"},
                    "parent_comment_id": {"type": "string", "description": "Parent comment ID (t1_...) to reply nestedly; omitted for top-level"},
                    "body": {"type": "string", "description": "Markdown comment text"}
                },
                "required": ["post_id_or_url", "body"]
            },
            handler=lambda args: self.client.submit_comment(RedditCommentSubmissionDTO(**args))
        )

        # 6. reddit_vote
        self.register_tool(
            name="reddit_vote",
            description="Cast or clear an upvote (+1) or downvote (-1) on a post or comment.",
            parameters={
                "type": "object",
                "properties": {
                    "target_id_or_url": {"type": "string", "description": "Post or comment ID (t3_... / t1_...) or permalink URL"},
                    "direction": {"type": "integer", "enum": [1, 0, -1], "description": "1 = upvote, -1 = downvote, 0 = clear"}
                },
                "required": ["target_id_or_url", "direction"]
            },
            handler=lambda args: self.client.vote(args["target_id_or_url"], args["direction"])
        )

        # 7. reddit_save_post
        self.register_tool(
            name="reddit_save_post",
            description="Save or unsave a post or comment to account bookmarks.",
            parameters={
                "type": "object",
                "properties": {
                    "target_id_or_url": {"type": "string", "description": "Post or comment ID or permalink URL"},
                    "unsave": {"type": "boolean", "default": False, "description": "True to remove from saved"}
                },
                "required": ["target_id_or_url"]
            },
            handler=lambda args: self.client.save_post(args["target_id_or_url"], args.get("unsave", False))
        )

        # 8. reddit_read_thread
        self.register_tool(
            name="reddit_read_thread",
            description="Read a full Reddit thread and extract the complete hierarchical nested comment tree.",
            parameters={
                "type": "object",
                "properties": {
                    "thread_url_or_id": {"type": "string", "description": "Post URL or post ID (t3_...)"},
                    "max_depth": {"type": "integer", "default": 5, "description": "Maximum nesting depth to parse"}
                },
                "required": ["thread_url_or_id"]
            },
            handler=lambda args: self.client.read_thread(args["thread_url_or_id"], args.get("max_depth", 5))
        )

        # 9. reddit_browse_subreddit
        self.register_tool(
            name="reddit_browse_subreddit",
            description="Browse posts in a subreddit with sorting (hot, new, top, rising) and time filters.",
            parameters={
                "type": "object",
                "properties": {
                    "subreddit": {"type": "string", "description": "Subreddit name (e.g. 'webscraping', 'Python')"},
                    "sort": {"type": "string", "enum": ["hot", "new", "top", "rising"], "default": "hot"},
                    "time_filter": {"type": "string", "enum": ["hour", "day", "week", "month", "year", "all"]},
                    "limit": {"type": "integer", "default": 25, "maximum": 100}
                },
                "required": ["subreddit"]
            },
            handler=lambda args: self.client.browse_subreddit(
                subreddit=args["subreddit"],
                sort=args.get("sort", "hot"),
                time_filter=args.get("time_filter"),
                limit=args.get("limit", 25)
            )
        )

        # 10. reddit_browse_user
        self.register_tool(
            name="reddit_browse_user",
            description="Audit another user's submitted posts, comment activity, and public profile metrics.",
            parameters={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Reddit username without 'u/'"},
                    "limit": {"type": "integer", "default": 20}
                },
                "required": ["username"]
            },
            handler=lambda args: self.client.browse_user(args["username"], args.get("limit", 20))
        )

        # 11. reddit_search
        self.register_tool(
            name="reddit_search",
            description="Search Reddit posts across all communities or within a specified subreddit.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query terms"},
                    "subreddit": {"type": "string", "description": "Optional subreddit filter"},
                    "sort": {"type": "string", "enum": ["relevance", "hot", "top", "new", "comments"], "default": "relevance"},
                    "time_filter": {"type": "string", "enum": ["hour", "day", "week", "month", "year", "all"], "default": "all"},
                    "limit": {"type": "integer", "default": 25}
                },
                "required": ["query"]
            },
            handler=lambda args: self.client.search(
                query=args["query"],
                subreddit=args.get("subreddit"),
                sort=args.get("sort", "relevance"),
                time_filter=args.get("time_filter", "all"),
                limit=args.get("limit", 25)
            )
        )

        # 12. reddit_send_message
        self.register_tool(
            name="reddit_send_message",
            description="Send a private direct message (PM) to a Reddit user with human typing cadence.",
            parameters={
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Recipient Reddit username"},
                    "subject": {"type": "string", "description": "Message subject"},
                    "body": {"type": "string", "description": "Markdown message body"}
                },
                "required": ["recipient", "subject", "body"]
            },
            handler=lambda args: self.client.send_message(RedditSendMessageDTO(**args))
        )

        # 13. reddit_check_inbox
        self.register_tool(
            name="reddit_check_inbox",
            description="Check recent inbox notifications, private messages, and post/comment replies.",
            parameters={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 15}
                },
                "required": []
            },
            handler=lambda args: self.client.check_inbox(args.get("limit", 15))
        )

        # 14. reddit_hunt_leads
        self.register_tool(
            name="reddit_hunt_leads",
            description="Discover actionable freelance web scraping and browser automation leads across tech subreddits.",
            parameters={
                "type": "object",
                "properties": {
                    "subreddits": {"type": "array", "items": {"type": "string"}, "description": "Target subreddits"},
                    "keywords": {"type": "array", "items": {"type": "string"}, "description": "Search pain point terms"},
                    "min_urgency": {"type": "integer", "default": 5, "minimum": 1, "maximum": 10}
                },
                "required": []
            },
            handler=lambda args: self.client.hunt_leads(
                subreddits=args.get("subreddits"),
                keywords=args.get("keywords"),
                min_urgency=args.get("min_urgency", 5)
            )
        )

        # 15. reddit_generate_pitch
        self.register_tool(
            name="reddit_generate_pitch",
            description="Generate an authoritative, non-salesy technical solution pitch with GitHub proof for a discovered lead.",
            parameters={
                "type": "object",
                "properties": {
                    "post_id": {"type": "string"},
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "subreddit": {"type": "string"},
                    "url": {"type": "string"},
                    "urgency_score": {"type": "integer"},
                    "budget_intent": {"type": "string"},
                    "pain_points": {"type": "array", "items": {"type": "string"}},
                    "recommended_strategy": {"type": "string"}
                },
                "required": ["post_id", "title", "author", "subreddit", "url", "urgency_score", "budget_intent"]
            },
            handler=lambda args: self.client.generate_pitch(RedditLeadDTO(**args))
        )
