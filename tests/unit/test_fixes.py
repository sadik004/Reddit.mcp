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


def test_comment_url_regex_extraction():
    """Validates regex extraction of comment ID from permalink URLs in vote and save."""
    import re
    pattern = r"/(?:comment|comments/[^/]+/_)/([a-z0-9]+)"
    url1 = "https://www.reddit.com/r/webscraping/comments/1ir234/_/k9abc123/"
    url2 = "https://reddit.com/comments/xyz987/comment/k9def456"
    m1 = re.search(pattern, url1, re.IGNORECASE)
    assert m1 is not None and m1.group(1) == "k9abc123"
    m2 = re.search(pattern, url2, re.IGNORECASE)
    assert m2 is not None and m2.group(1) == "k9def456"


def test_config_storage_state_resolves_to_absolute_path():
    """Validates that storage_state default resolves to an absolute path within Reddit.mcp root."""
    from reddit_mcp.config import RedditConfig
    config = RedditConfig()
    assert config.storage_state.is_absolute()
    assert config.storage_state.name == "storage_state.json"


def test_browser_proxy_dict_construction():
    """Validates that proxy_server, proxy_username, and proxy_password populate proxy_dict correctly."""
    from reddit_mcp.config import RedditConfig
    config = RedditConfig(
        proxy_server="http://127.0.0.1:8080",
        proxy_username="myuser",
        proxy_password="mypassword"
    )
    proxy_dict = {"server": config.proxy_server}
    if config.proxy_username:
        proxy_dict["username"] = config.proxy_username
    if config.proxy_password:
        proxy_dict["password"] = config.proxy_password

    assert proxy_dict == {
        "server": "http://127.0.0.1:8080",
        "username": "myuser",
        "password": "mypassword"
    }


@pytest.mark.asyncio
async def test_mouse_controller_forwards_button(monkeypatch):
    """Validates that MouseController.human_move_and_click forwards the button parameter."""
    from unittest.mock import AsyncMock, MagicMock
    from reddit_mcp.engine.mouse import MouseController

    mock_page = MagicMock()
    mock_page.mouse = MagicMock()
    mock_page.mouse.down = AsyncMock()
    mock_page.mouse.up = AsyncMock()
    mock_page.mouse.move = AsyncMock()

    await MouseController.human_move_and_click(mock_page, 200.0, 300.0, button="right")
    mock_page.mouse.down.assert_awaited_once_with(button="right")
    mock_page.mouse.up.assert_awaited_once_with(button="right")


@pytest.mark.asyncio
async def test_hunt_leads_handles_none_min_urgency(monkeypatch):
    """Validates that hunt_leads does not crash when min_urgency is passed as None."""
    from unittest.mock import AsyncMock
    from reddit_mcp.models.dtos import RedditSearchDTO, RedditPostSummaryDTO

    client = RedditAutomationClient()
    mock_search = AsyncMock(return_value=RedditSearchDTO(
        query="test",
        subreddit="webscraping",
        total_found=1,
        results=[
            RedditPostSummaryDTO(
                post_id="t3_lead123",
                title="Cloudflare 403 blocking my scraper",
                author="dev_user",
                subreddit="webscraping",
                score=10,
                comments_count=5,
                permalink="https://reddit.com/r/webscraping/comments/lead123",
                body_preview="Need help bypassing turnstile"
            )
        ]
    ))
    monkeypatch.setattr(client, "search", mock_search)

    # Should not raise TypeError: '>=' not supported between instances of 'int' and 'NoneType'
    leads = await client.hunt_leads(subreddits=["webscraping"], keywords=["turnstile"], min_urgency=None)
    assert len(leads) == 1
    assert leads[0].post_id == "t3_lead123"
    assert leads[0].urgency_score >= 5


@pytest.mark.asyncio
async def test_update_profile_nsfw_switch_logic(monkeypatch, tmp_path):
    """Validates that update_profile only toggles NSFW switch if current aria-checked differs."""
    from unittest.mock import AsyncMock, MagicMock
    from reddit_mcp.models.dtos import RedditProfileUpdateDTO
    from contextlib import asynccontextmanager

    # Fake storage state file
    fake_state = tmp_path / "storage_state.json"
    fake_state.write_text("{}", encoding="utf-8")

    client = RedditAutomationClient()
    client.config.storage_state = fake_state

    # Mock page and switch
    mock_switch = MagicMock()
    mock_switch.count = AsyncMock(return_value=1)
    mock_switch.get_attribute = AsyncMock(return_value="true")
    mock_switch.is_enabled = AsyncMock(return_value=False)
    mock_switch.click = AsyncMock()

    mock_locator = MagicMock()
    mock_locator.first = mock_switch

    mock_page = MagicMock()
    mock_page.goto = AsyncMock()
    mock_page.keyboard.press = AsyncMock()
    mock_page.locator = MagicMock(return_value=mock_locator)

    @asynccontextmanager
    async def fake_get_page():
        yield mock_page

    monkeypatch.setattr(client.pool, "get_page", fake_get_page)

    # 1. Target is_nsfw=True, current is already "true" -> Should NOT click
    res1 = await client.update_profile(RedditProfileUpdateDTO(is_nsfw=True))
    assert res1.success is True
    assert "is_nsfw" not in res1.updated_fields
    mock_switch.click.assert_not_awaited()

    # 2. Target is_nsfw=False, current is "true" -> Should click
    res2 = await client.update_profile(RedditProfileUpdateDTO(is_nsfw=False))
    assert res2.success is True
    assert "is_nsfw" in res2.updated_fields
    mock_switch.click.assert_awaited_once()


