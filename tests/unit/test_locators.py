"""
Unit tests for Reddit DOM locators.
"""

from reddit_mcp.engine.locators import RedditLocators


def test_locators_non_empty() -> None:
    assert RedditLocators.AUTH_USER_MENU
    assert RedditLocators.AUTH_AVATAR
    assert RedditLocators.PROFILE_DISPLAY_NAME_INPUT
    assert RedditLocators.PROFILE_ABOUT_TEXTAREA
    assert RedditLocators.POST_TITLE_INPUT
    assert RedditLocators.COMMENT_BOX
    assert RedditLocators.UPVOTE_BUTTON
    assert RedditLocators.MESSAGE_RECIPIENT_INPUT
