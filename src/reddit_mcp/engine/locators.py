"""
Scoped Semantic Locators for Reddit Automation.
Combines semantic ARIA roles, modern Shreddit web components, and data-testid selectors.
"""

class RedditLocators:
    """Central repository of robust, scoped DOM locators for Reddit."""

    # Navigation & Authentication
    AUTH_USER_MENU = 'button#USER_DROPDOWN_ID, button[aria-label*="User menu"], [data-testid="user-dropdown"]'
    AUTH_AVATAR = 'reddit-header-action-items button img, [data-testid="user-avatar"]'
    AUTH_USERNAME = '[data-testid="user-name"], shreddit-header-action-items [data-username]'
    AUTH_KARMA = '[data-testid="karma-count"], [id*="karma"]'
    AUTH_NOTIFICATION_BADGE = 'a[href*="/notifications"] [data-testid="notification-indicator"], a[href*="/message/inbox"]'

    # Profile Settings (https://www.reddit.com/settings/profile)
    PROFILE_DISPLAY_NAME_INPUT = 'input[name="displayName"], input[id="displayName"], [data-testid="display-name-input"]'
    PROFILE_ABOUT_TEXTAREA = 'textarea[name="about"], textarea[id="about"], [data-testid="about-input"]'
    PROFILE_NSFW_SWITCH = 'button[role="switch"][aria-label*="NSFW"], [data-testid="profile-nsfw-switch"]'
    PROFILE_SAVE_BUTTON = 'button[type="submit"]:has-text("Save"), button:has-text("Save changes")'
    PROFILE_ADD_SOCIAL_LINK = 'button:has-text("Add social link"), [data-testid="add-social-link"]'
    PROFILE_SOCIAL_URL_INPUT = 'input[placeholder*="URL"], input[type="url"]'
    PROFILE_SOCIAL_TITLE_INPUT = 'input[placeholder*="Title"], input[placeholder*="Display name"]'

    # Submit Post (https://www.reddit.com/r/.../submit or /submit)
    POST_COMMUNITY_SELECTOR = 'button[aria-label*="Choose a community"], [data-testid="subreddit-selector"]'
    POST_TITLE_INPUT = 'textarea[placeholder*="Title"], input[placeholder*="Title"], [data-testid="post-title-input"]'
    POST_TEXT_TAB = 'button:has-text("Post"), button:has-text("Text"), [role="tab"]:has-text("Post")'
    POST_MARKDOWN_BODY = 'div[contenteditable="true"][role="textbox"], textarea[placeholder*="Text"], [data-testid="post-body-input"]'
    POST_LINK_TAB = 'button:has-text("Link"), [role="tab"]:has-text("Link")'
    POST_LINK_URL_INPUT = 'textarea[placeholder*="Url"], input[placeholder*="Url"]'
    POST_FLAIR_BUTTON = 'button:has-text("Add flair"), button:has-text("Flair")'
    POST_SUBMIT_BUTTON = 'button:has-text("Post"), button:has-text("Submit"), button[type="submit"]'

    # Comments
    COMMENT_BOX = 'div[contenteditable="true"][role="textbox"], shreddit-comment-composer textarea, [data-testid="comment-box"]'
    COMMENT_SUBMIT_BUTTON = 'button:has-text("Comment"), shreddit-comment-composer button[type="submit"]'
    COMMENT_REPLY_BUTTON = 'button:has-text("Reply"), shreddit-comment button[aria-label*="reply"]'

    # Voting & Engagement
    UPVOTE_BUTTON = 'shreddit-post button[aria-label*="upvote"], button[data-click-id="upvote"], [data-testid="upvote-button"]'
    DOWNVOTE_BUTTON = 'shreddit-post button[aria-label*="downvote"], button[data-click-id="downvote"], [data-testid="downvote-button"]'
    SAVE_BUTTON = 'button:has-text("Save"), [data-testid="save-button"]'

    # Feeds, Search & Listings
    POST_CARD = 'shreddit-post, article, div[data-testid="post-container"]'
    POST_CARD_TITLE = 'a[slot="title"], [data-testid="post-title-text"], h2'
    POST_CARD_AUTHOR = 'a[slot="authorName"], [data-testid="post_author_link"]'
    POST_CARD_SCORE = 'shreddit-post[score], [data-testid="post-score"]'
    POST_CARD_COMMENTS = 'a[data-testid="comments-page-link-num-comments"], a[slot="comments-page-link"]'

    # Direct Messaging (https://www.reddit.com/message/compose)
    MESSAGE_RECIPIENT_INPUT = 'input[name="to"], input#to'
    MESSAGE_SUBJECT_INPUT = 'input[name="subject"], input#subject'
    MESSAGE_BODY_TEXTAREA = 'textarea[name="message"], textarea#message'
    MESSAGE_SEND_BUTTON = 'input[type="submit"][value="send"], button:has-text("Send")'
