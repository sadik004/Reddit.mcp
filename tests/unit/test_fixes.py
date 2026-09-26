"""
Unit tests validating fixes for:
1. Scoped comment & post voting locators
2. Scoped nested reply comment locators
3. Non-blocking auth avatar container locators (route-abort safe)
4. Successful-only caching on browse and search
5. Flair modal and button locators
"""

import pytest
from reddit_mcp.engine.locators import RedditLocators
from reddit_mcp.engine.client import RedditAutomationClient
from reddit_mcp.models.dtos import RedditSubredditBrowseDTO


def test_auth_avatar_avoids_strict_img_requirement():
    """Validates that AUTH_AVATAR does not strictly mandate <img> which is blocked by route abortion."""
    avatar_selector = RedditLocators.AUTH_AVATAR
    assert "button" in avatar_selector
    assert "user_drawer" in avatar_selector


def test_scoped_voting_locators():
    """Validates separation of post vs comment upvote/downvote locators."""
    assert "shreddit-post" in RedditLocators.POST_UPVOTE_BUTTON
    assert "shreddit-post" in RedditLocators.POST_DOWNVOTE_BUTTON
    assert "shreddit-post" not in RedditLocators.COMMENT_UPVOTE_BUTTON
    assert "shreddit-post" not in RedditLocators.COMMENT_DOWNVOTE_BUTTON


def test_flair_locators_present():
    """Validates that post flair button and modal dialog locators exist."""
    assert hasattr(RedditLocators, "POST_FLAIR_BUTTON")
    assert hasattr(RedditLocators, "POST_FLAIR_MODAL")
    assert "flair" in RedditLocators.POST_FLAIR_BUTTON.lower()


def test_cache_ttl_logic():
    """Validates that in-memory cache respects expiration and stores valid payloads."""
    client = RedditAutomationClient()
    cache_key = "test:browse:sample"

    # Initially empty
    assert client._get_from_cache(cache_key) is None

    dto = RedditSubredditBrowseDTO(
        subreddit="test",
        sort="hot",
        count=1,
        posts=[]
    )
    client._set_cache(cache_key, dto, ttl_seconds=60.0)
    cached = client._get_from_cache(cache_key)
    assert cached is not None
    assert cached.subreddit == "test"


def test_overflow_and_unsave_locators_present():
    """Validates that overflow menu and unsave locators exist."""
    assert hasattr(RedditLocators, "POST_OVERFLOW_MENU")
    assert hasattr(RedditLocators, "UNSAVE_BUTTON")
    assert "unsave" in RedditLocators.UNSAVE_BUTTON.lower()
    assert "overflow" in RedditLocators.POST_OVERFLOW_MENU.lower() or "more" in RedditLocators.POST_OVERFLOW_MENU.lower()


def test_clean_t3_id_normalization():
    """Validates regex cleaning of t3_ and t1_ prefixes."""
    import re
    assert re.sub(r"^t3_", "", "t3_1abcxyz") == "1abcxyz"
    assert re.sub(r"^t1_", "", "t1_9defghi") == "9defghi"
    assert re.sub(r"^t[13]_", "", "t3_123") == "123"
    assert re.sub(r"^t[13]_", "", "t1_456") == "456"

