"""
Unit tests for Reddit MCP Pydantic v2 DTOs.
"""

import pytest
from reddit_mcp.models.dtos import (
    RedditAuthStatusDTO,
    RedditProfileDTO,
    RedditProfileUpdateDTO,
    RedditPostSubmissionDTO,
    RedditPostResultDTO,
    RedditCommentSubmissionDTO,
    RedditCommentNodeDTO,
    RedditThreadDTO,
    RedditLeadDTO,
    RedditPitchDTO,
)


def test_auth_status_dto() -> None:
    dto = RedditAuthStatusDTO(
        authenticated=True,
        username="web_architect",
        total_karma=1540,
        status_message="OK"
    )
    assert dto.authenticated is True
    assert dto.username == "web_architect"
    assert dto.total_karma == 1540


def test_profile_dto() -> None:
    dto = RedditProfileDTO(
        username="lead_dev",
        display_name="Sadik | Automation Architect",
        bio="Specializing in stealth web automation & behavioral playwright",
        total_karma=3400,
        social_links=[
            {"platform": "GitHub", "title": "Repo", "url": "https://github.com/sadik004"}
        ]
    )
    assert dto.username == "lead_dev"
    assert len(dto.social_links) == 1
    assert dto.social_links[0].platform == "GitHub"


def test_profile_update_dto() -> None:
    dto = RedditProfileUpdateDTO(
        display_name="Updated Name",
        bio="Updated Bio",
        is_nsfw=False
    )
    assert dto.display_name == "Updated Name"
    assert dto.bio == "Updated Bio"
    assert dto.is_nsfw is False


def test_post_submission_dto() -> None:
    dto = RedditPostSubmissionDTO(
        target="webscraping",
        title="Bypassing Cloudflare Turnstile with Behavioral Playwright",
        body="Here is a comprehensive breakdown of TLS & mouse physics...",
        is_nsfw=False
    )
    assert dto.target == "webscraping"
    assert "Turnstile" in dto.title


def test_comment_hierarchy_dto() -> None:
    child_comment = RedditCommentNodeDTO(
        comment_id="t1_child",
        author="user_b",
        score=5,
        body="Great architecture!",
        depth=1,
        parent_id="t1_parent"
    )
    parent_comment = RedditCommentNodeDTO(
        comment_id="t1_parent",
        author="user_a",
        score=12,
        body="How do you handle asset abortion?",
        depth=0,
        replies=[child_comment]
    )

    thread = RedditThreadDTO(
        post_id="t3_123",
        title="Discussion on Stealth",
        author="sadik",
        subreddit="webscraping",
        permalink="https://reddit.com/r/webscraping/comments/123/",
        comments=[parent_comment]
    )

    assert len(thread.comments) == 1
    assert thread.comments[0].replies[0].author == "user_b"


def test_lead_and_pitch_dto() -> None:
    lead = RedditLeadDTO(
        post_id="t3_lead1",
        title="Scraping script getting 403 Forbidden on target site",
        author="client_dev",
        subreddit="webscraping",
        url="https://reddit.com/r/webscraping/comments/lead1",
        urgency_score=8,
        budget_intent="High",
        pain_points=["Cloudflare 403 Forbidden"]
    )
    assert lead.urgency_score == 8
    assert lead.budget_intent == "High"
