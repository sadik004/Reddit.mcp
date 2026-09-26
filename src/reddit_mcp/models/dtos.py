"""
Pydantic v2 Data Transfer Objects (DTOs) for Reddit MCP.
Enforces strict schema validation across all human actions, posts, profiles, and reading layers.
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class RedditAuthStatusDTO(BaseModel):
    """Authentication and session telemetry DTO."""
    authenticated: bool = Field(description="Whether a valid authenticated session exists")
    username: Optional[str] = Field(default=None, description="Logged in username")
    total_karma: int = Field(default=0, description="Total account karma")
    post_karma: int = Field(default=0, description="Post/Link karma")
    comment_karma: int = Field(default=0, description="Comment karma")
    unread_count: int = Field(default=0, description="Unread notifications or messages count")
    is_mod: bool = Field(default=False, description="Whether the user moderates any subreddits")
    status_message: str = Field(description="Status description or diagnostic details")


class RedditSocialLinkDTO(BaseModel):
    """Social link attached to a Reddit profile."""
    platform: str = Field(description="Platform name (e.g. GitHub, Twitter, Portfolio, LinkedIn)")
    title: str = Field(description="Custom title or display text")
    url: str = Field(description="Target destination URL")


class RedditProfileDTO(BaseModel):
    """Detailed profile data for a Reddit user."""
    username: str = Field(description="Reddit username")
    display_name: Optional[str] = Field(default=None, description="Custom display name")
    bio: Optional[str] = Field(default=None, description="About me / bio text")
    total_karma: int = Field(default=0, description="Total karma")
    post_karma: int = Field(default=0, description="Post karma")
    comment_karma: int = Field(default=0, description="Comment karma")
    cake_day: Optional[str] = Field(default=None, description="Account creation date or age")
    avatar_url: Optional[str] = Field(default=None, description="Profile avatar picture URL")
    banner_url: Optional[str] = Field(default=None, description="Profile banner image URL")
    social_links: List[RedditSocialLinkDTO] = Field(default_factory=list, description="Associated social links")
    is_nsfw: bool = Field(default=False, description="Whether the profile is flagged 18+ NSFW")


class RedditProfileUpdateDTO(BaseModel):
    """Payload to update own Reddit profile settings."""
    display_name: Optional[str] = Field(default=None, description="Updated display name")
    bio: Optional[str] = Field(default=None, description="Updated About Me / Bio description")
    social_links: Optional[List[RedditSocialLinkDTO]] = Field(default=None, description="Updated list of social links")
    is_nsfw: Optional[bool] = Field(default=None, description="NSFW profile flag toggle")


class RedditProfileUpdateResultDTO(BaseModel):
    """Result of profile update operation."""
    success: bool = Field(description="Whether the update succeeded")
    username: Optional[str] = Field(default=None, description="Updated username")
    updated_fields: List[str] = Field(default_factory=list, description="List of updated field names")
    message: str = Field(description="Result summary or error explanation")


class RedditPostSubmissionDTO(BaseModel):
    """Payload to submit a new post to Reddit."""
    target: str = Field(
        description="Target destination: subreddit (e.g., 'webscraping', 'Python') or 'u/me' for own profile"
    )
    title: str = Field(min_length=1, max_length=300, description="Post title")
    body: Optional[str] = Field(default=None, description="Post markdown body (for text/self posts)")
    url: Optional[str] = Field(default=None, description="Target destination URL (for link posts)")
    flair: Optional[str] = Field(default=None, description="Flair text or flair template ID")
    is_nsfw: bool = Field(default=False, description="Mark as NSFW")
    is_spoiler: bool = Field(default=False, description="Mark as Spoiler")


class RedditPostResultDTO(BaseModel):
    """Result of submitting a post."""
    success: bool = Field(description="Whether the post was published")
    post_id: Optional[str] = Field(default=None, description="Full post identifier (e.g. t3_1abcxyz)")
    permalink: Optional[str] = Field(default=None, description="Direct URL to published post")
    title: str = Field(description="Post title")
    author: Optional[str] = Field(default=None, description="Author username")
    target: str = Field(description="Subreddit or profile destination")
    message: str = Field(description="Operational summary")


class RedditCommentSubmissionDTO(BaseModel):
    """Payload to submit a comment or reply."""
    post_id_or_url: str = Field(description="Target post ID or permalink URL")
    parent_comment_id: Optional[str] = Field(
        default=None,
        description="Parent comment ID (e.g. t1_...) to reply nestedly; None for top-level comment"
    )
    body: str = Field(min_length=1, description="Markdown comment text")


class RedditCommentResultDTO(BaseModel):
    """Result of submitting a comment."""
    success: bool = Field(description="Whether comment was published")
    comment_id: Optional[str] = Field(default=None, description="Created comment ID")
    post_id: str = Field(description="Parent post ID")
    permalink: Optional[str] = Field(default=None, description="Direct link to comment")
    author: Optional[str] = Field(default=None, description="Commenter username")
    body: str = Field(description="Comment body")
    message: str = Field(description="Operational summary")


class RedditVoteDTO(BaseModel):
    """Voting parameters."""
    target_id_or_url: str = Field(description="Post or comment identifier or permalink")
    direction: Literal[1, 0, -1] = Field(description="1 for upvote, -1 for downvote, 0 to clear vote")


class RedditActionResultDTO(BaseModel):
    """Generic atomic action result."""
    success: bool = Field(description="Operation success status")
    action: str = Field(description="Action name (e.g. vote, save, edit, delete)")
    target_id: str = Field(description="Target item identifier")
    message: str = Field(description="Operational summary")


class RedditCommentNodeDTO(BaseModel):
    """Hierarchical comment tree node."""
    comment_id: str = Field(description="Unique comment ID")
    author: str = Field(description="Author username")
    score: int = Field(default=0, description="Upvotes minus downvotes")
    created_utc: Optional[str] = Field(default=None, description="Creation timestamp")
    body: str = Field(description="Comment markdown content")
    depth: int = Field(default=0, description="Nesting level (0 = top-level)")
    parent_id: Optional[str] = Field(default=None, description="Parent ID (post or comment)")
    replies: List[RedditCommentNodeDTO] = Field(default_factory=list, description="Nested child replies")


class RedditThreadDTO(BaseModel):
    """Full thread extraction including nested discussion tree."""
    post_id: str = Field(description="Post identifier")
    title: str = Field(description="Post title")
    author: str = Field(description="Author username")
    subreddit: str = Field(description="Subreddit name")
    score: int = Field(default=0, description="Post score")
    upvote_ratio: Optional[float] = Field(default=None, description="Upvote ratio percentage")
    url: Optional[str] = Field(default=None, description="External URL if link post")
    permalink: str = Field(description="Reddit permalink")
    created_utc: Optional[str] = Field(default=None, description="Creation timestamp")
    flair: Optional[str] = Field(default=None, description="Post flair text")
    body: Optional[str] = Field(default=None, description="Selftext / markdown post body")
    total_comments: int = Field(default=0, description="Total comment count")
    comments: List[RedditCommentNodeDTO] = Field(default_factory=list, description="Hierarchical comment tree")


class RedditPostSummaryDTO(BaseModel):
    """Summarized post item for feeds, searches, and subreddit listings."""
    post_id: str = Field(description="Post ID")
    title: str = Field(description="Post title")
    author: str = Field(description="Author username")
    subreddit: str = Field(description="Subreddit name")
    score: int = Field(default=0, description="Post score")
    comments_count: int = Field(default=0, description="Number of comments")
    url: Optional[str] = Field(default=None, description="Target URL")
    permalink: str = Field(description="Reddit permalink")
    created_utc: Optional[str] = Field(default=None, description="Creation time")
    flair: Optional[str] = Field(default=None, description="Post flair")
    body_preview: Optional[str] = Field(default=None, description="Short snippet of post body")


class RedditSubredditBrowseDTO(BaseModel):
    """Subreddit listing result."""
    subreddit: str = Field(description="Subreddit name")
    sort: str = Field(description="Sorting mode (hot, new, top, rising)")
    time_filter: Optional[str] = Field(default=None, description="Time filter (day, week, month, year, all)")
    count: int = Field(description="Number of posts retrieved")
    posts: List[RedditPostSummaryDTO] = Field(default_factory=list, description="Retrieved posts")


class RedditSearchDTO(BaseModel):
    """Reddit search results container."""
    query: str = Field(description="Search query string")
    subreddit: Optional[str] = Field(default=None, description="Restricted subreddit, if any")
    sort: str = Field(default="relevance", description="Sorting criteria")
    time_filter: str = Field(default="all", description="Time filter")
    total_found: int = Field(description="Count of found posts")
    results: List[RedditPostSummaryDTO] = Field(default_factory=list, description="Search result posts")


class RedditUserHistoryDTO(BaseModel):
    """Overview of a Reddit user's recent activity."""
    username: str = Field(description="Target username")
    profile: Optional[RedditProfileDTO] = Field(default=None, description="Profile header details")
    recent_posts: List[RedditPostSummaryDTO] = Field(default_factory=list, description="Recent submitted posts")
    recent_comments: List[Dict[str, Any]] = Field(default_factory=list, description="Recent comments")


class RedditSendMessageDTO(BaseModel):
    """Payload to send a direct message (PM)."""
    recipient: str = Field(description="Recipient Reddit username")
    subject: str = Field(min_length=1, max_length=100, description="Message subject")
    body: str = Field(min_length=1, description="Message body in markdown")


class RedditInboxItemDTO(BaseModel):
    """Item retrieved from Reddit inbox."""
    item_id: str = Field(description="Message / notification ID")
    type: str = Field(description="Type: 'message', 'comment_reply', 'post_reply', 'username_mention'")
    author: str = Field(description="Sender or commenter username")
    subject: Optional[str] = Field(default=None, description="Subject line")
    body: str = Field(description="Message body text")
    context_url: Optional[str] = Field(default=None, description="Link to thread or comment")
    unread: bool = Field(default=True, description="Whether unread")
    created_utc: Optional[str] = Field(default=None, description="Timestamp")


class RedditLeadDTO(BaseModel):
    """Actionable client acquisition lead discovered on Reddit."""
    post_id: str = Field(description="Unique Reddit post identifier")
    title: str = Field(description="Post title")
    author: str = Field(description="Reddit author username")
    subreddit: str = Field(description="Subreddit source")
    url: str = Field(description="Direct URL to thread")
    urgency_score: int = Field(ge=1, le=10, description="Urgency rating (1-10)")
    budget_intent: str = Field(description="High / Medium / Low / Undefined")
    pain_points: List[str] = Field(default_factory=list, description="Identified technical hurdles")
    recommended_strategy: str = Field(
        default="Provide root cause analysis of anti-bot challenge and offer open-source behavioral proof.",
        description="Actionable behavioral scraping strategy"
    )


class RedditPitchDTO(BaseModel):
    """Context-aware, technical solution pitch for a client problem."""
    post_id: str = Field(description="Post ID being addressed")
    recipient: str = Field(description="Reddit author username")
    title: str = Field(description="Post title")
    technical_breakdown: str = Field(description="Root cause analysis of client's obstacle")
    proposed_architecture: str = Field(description="Behavioral automation architecture recommendation")
    code_proof_link: str = Field(default="https://github.com/sadik004/behavioral-playwright", description="Proof repository link")
    ready_to_send_pitch: str = Field(description="Ready-to-send authoritative technical reply")
