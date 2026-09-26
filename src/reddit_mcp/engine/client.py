"""
Comprehensive Human-Mimetic Reddit Automation Client.
Executes standard and advanced human workflows on Reddit:
- Profile branding, bio updates, and social link management
- Post publishing (markdown text, links) to subreddits and user profiles
- Commenting, nested replies, editing, deleting, voting, and saving
- Hierarchical thread extraction with full recursive comment trees
- Subreddit browsing, search, user activity auditing
- Direct messaging and inbox processing
- High-intent freelance lead discovery and technical solution pitch generation
"""

from __future__ import annotations
import json
import logging
import re
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus, urljoin

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from reddit_mcp.config import RedditConfig
from reddit_mcp.engine.browser import BrowserPoolManager
from reddit_mcp.engine.mouse import MouseController
from reddit_mcp.engine.keyboard import KeyboardController
from reddit_mcp.engine.locators import RedditLocators
from reddit_mcp.models.dtos import (
    RedditAuthStatusDTO,
    RedditProfileDTO,
    RedditProfileUpdateDTO,
    RedditProfileUpdateResultDTO,
    RedditSocialLinkDTO,
    RedditPostSubmissionDTO,
    RedditPostResultDTO,
    RedditCommentSubmissionDTO,
    RedditCommentResultDTO,
    RedditActionResultDTO,
    RedditThreadDTO,
    RedditCommentNodeDTO,
    RedditPostSummaryDTO,
    RedditSubredditBrowseDTO,
    RedditSearchDTO,
    RedditUserHistoryDTO,
    RedditSendMessageDTO,
    RedditInboxItemDTO,
    RedditLeadDTO,
    RedditPitchDTO,
)

logger = logging.getLogger("reddit_mcp.client")


class RedditAutomationClient:
    """Production-grade human-mimetic Reddit client."""

    def __init__(self, config: Optional[RedditConfig] = None):
        self.config = config or RedditConfig()
        self.pool = BrowserPoolManager(self.config)

    # =========================================================================
    # 1. Authentication & Session Auditing
    # =========================================================================

    async def check_auth(self) -> RedditAuthStatusDTO:
        """Verifies session validity and extracts account credentials."""
        async with self.pool.get_page() as page:
            try:
                await page.goto("https://www.reddit.com/", wait_until="domcontentloaded")
            except Exception as exc:
                return RedditAuthStatusDTO(
                    authenticated=False,
                    status_message=f"Network navigation failure: {exc}"
                )

            # Inspect DOM for user elements
            user_menu = page.locator(RedditLocators.AUTH_USER_MENU).first
            avatar = page.locator(RedditLocators.AUTH_AVATAR).first

            is_logged_in = False
            try:
                await avatar.wait_for(state="visible", timeout=4000)
                is_logged_in = True
            except PlaywrightTimeoutError:
                try:
                    await user_menu.wait_for(state="visible", timeout=2000)
                    is_logged_in = True
                except PlaywrightTimeoutError:
                    is_logged_in = False

            if not is_logged_in:
                return RedditAuthStatusDTO(
                    authenticated=False,
                    status_message="No active session found. Please export session using scripts/login.py."
                )

            # Extract username and metrics
            username = None
            try:
                user_elem = page.locator(RedditLocators.AUTH_USERNAME).first
                if await user_elem.count() > 0:
                    username = (await user_elem.inner_text()).strip().replace("u/", "")
            except Exception:
                pass

            total_karma = 0
            try:
                karma_elem = page.locator(RedditLocators.AUTH_KARMA).first
                if await karma_elem.count() > 0:
                    text = await karma_elem.inner_text()
                    digits = re.sub(r"[^\d]", "", text)
                    if digits:
                        total_karma = int(digits)
            except Exception:
                pass

            return RedditAuthStatusDTO(
                authenticated=True,
                username=username or "authenticated_user",
                total_karma=total_karma,
                status_message="Successfully validated active human session."
            )

    # =========================================================================
    # 2. Profile Management & Personal Branding
    # =========================================================================

    async def get_profile(self, username: Optional[str] = None) -> RedditProfileDTO:
        """Extracts complete profile data for a given user or current authenticated user."""
        target_user = username if username and username != "me" else None

        async with self.pool.get_page() as page:
            if not target_user:
                # Query own profile
                await page.goto("https://www.reddit.com/settings/profile", wait_until="domcontentloaded")
                disp_input = page.locator(RedditLocators.PROFILE_DISPLAY_NAME_INPUT).first
                about_input = page.locator(RedditLocators.PROFILE_ABOUT_TEXTAREA).first

                display_name = None
                bio = None
                if await disp_input.count() > 0:
                    display_name = await disp_input.input_value()
                if await about_input.count() > 0:
                    bio = await about_input.input_value()

                return RedditProfileDTO(
                    username="me",
                    display_name=display_name,
                    bio=bio,
                    social_links=[]
                )

            # Query public user profile
            profile_url = f"https://www.reddit.com/user/{target_user}/about.json"
            response = await page.request.get(profile_url)
            if response.status == 200:
                data = await response.json()
                user_data = data.get("data", {})
                return RedditProfileDTO(
                    username=user_data.get("name", target_user),
                    display_name=user_data.get("subreddit", {}).get("title"),
                    bio=user_data.get("subreddit", {}).get("public_description"),
                    total_karma=user_data.get("total_karma", 0),
                    post_karma=user_data.get("link_karma", 0),
                    comment_karma=user_data.get("comment_karma", 0),
                    avatar_url=user_data.get("icon_img"),
                    is_nsfw=user_data.get("subreddit", {}).get("over_18", False)
                )

            # Fallback to HTML DOM parsing
            await page.goto(f"https://www.reddit.com/user/{target_user}/", wait_until="domcontentloaded")
            h1 = page.locator("h1").first
            name = (await h1.inner_text()).strip() if await h1.count() > 0 else target_user
            return RedditProfileDTO(
                username=target_user,
                display_name=name
            )

    async def update_profile(self, payload: RedditProfileUpdateDTO) -> RedditProfileUpdateResultDTO:
        """Updates profile settings with human-mimetic input dynamics."""
        async with self.pool.get_page() as page:
            await page.goto("https://www.reddit.com/settings/profile", wait_until="domcontentloaded")
            updated: List[str] = []

            # 1. Update Display Name
            if payload.display_name is not None:
                disp_elem = page.locator(RedditLocators.PROFILE_DISPLAY_NAME_INPUT).first
                await disp_elem.wait_for(state="visible", timeout=6000)
                box = await disp_elem.bounding_box()
                if box:
                    await MouseController.human_move_and_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                await disp_elem.fill("")
                await KeyboardController.human_type(disp_elem, payload.display_name)
                updated.append("display_name")

            # 2. Update Bio / About Text
            if payload.bio is not None:
                bio_elem = page.locator(RedditLocators.PROFILE_ABOUT_TEXTAREA).first
                await bio_elem.wait_for(state="visible", timeout=6000)
                box = await bio_elem.bounding_box()
                if box:
                    await MouseController.human_move_and_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                await bio_elem.fill("")
                await KeyboardController.human_type(bio_elem, payload.bio)
                updated.append("bio")

            # 3. Handle NSFW Switch
            if payload.is_nsfw is not None:
                nsfw_switch = page.locator(RedditLocators.PROFILE_NSFW_SWITCH).first
                if await nsfw_switch.count() > 0:
                    await nsfw_switch.click()
                    updated.append("is_nsfw")

            # 4. Save Changes
            save_button = page.locator(RedditLocators.PROFILE_SAVE_BUTTON).first
            if await save_button.count() > 0 and await save_button.is_enabled():
                box = await save_button.bounding_box()
                if box:
                    await MouseController.human_move_and_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                else:
                    await save_button.click()

            return RedditProfileUpdateResultDTO(
                success=True,
                updated_fields=updated,
                message=f"Successfully updated profile fields: {', '.join(updated) if updated else 'none'}"
            )

    # =========================================================================
    # 3. Post & Comment Publishing
    # =========================================================================

    async def submit_post(self, payload: RedditPostSubmissionDTO) -> RedditPostResultDTO:
        """Publishes a text or link post to a subreddit or own profile."""
        target_clean = payload.target.strip().lower()
        if target_clean in ("u/me", "me", "profile"):
            submit_url = "https://www.reddit.com/user/me/submit"
        elif target_clean.startswith("r/"):
            submit_url = f"https://www.reddit.com/{target_clean}/submit"
        else:
            submit_url = f"https://www.reddit.com/r/{target_clean}/submit"

        async with self.pool.get_page() as page:
            await page.goto(submit_url, wait_until="domcontentloaded")

            # Fill Post Title
            title_input = page.locator(RedditLocators.POST_TITLE_INPUT).first
            await title_input.wait_for(state="visible", timeout=8000)
            box = await title_input.bounding_box()
            if box:
                await MouseController.human_move_and_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
            await KeyboardController.human_type(title_input, payload.title)

            # Fill Content
            if payload.url:
                # Switch to Link tab
                link_tab = page.locator(RedditLocators.POST_LINK_TAB).first
                if await link_tab.count() > 0:
                    await link_tab.click()
                    url_input = page.locator(RedditLocators.POST_LINK_URL_INPUT).first
                    await url_input.wait_for(state="visible", timeout=4000)
                    await url_input.fill(payload.url)
            elif payload.body:
                # Fill markdown / text body
                body_elem = page.locator(RedditLocators.POST_MARKDOWN_BODY).first
                if await body_elem.count() > 0:
                    box = await body_elem.bounding_box()
                    if box:
                        await MouseController.human_move_and_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                    await KeyboardController.human_type(body_elem, payload.body)

            # Submit
            submit_btn = page.locator(RedditLocators.POST_SUBMIT_BUTTON).first
            await submit_btn.wait_for(state="visible", timeout=5000)
            box = await submit_btn.bounding_box()
            if box:
                await MouseController.human_move_and_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
            else:
                await submit_btn.click()

            # Wait for navigation to the published post
            await page.wait_for_url(re.compile(r"/comments/"), timeout=15000)
            final_url = page.url

            match = re.search(r"/comments/([a-z0-9]+)/", final_url)
            post_id = f"t3_{match.group(1)}" if match else None

            return RedditPostResultDTO(
                success=True,
                post_id=post_id,
                permalink=final_url,
                title=payload.title,
                target=payload.target,
                message="Post successfully published to Reddit."
            )

    async def submit_comment(self, payload: RedditCommentSubmissionDTO) -> RedditCommentResultDTO:
        """Publishes a top-level comment or replies to an existing comment."""
        target_url = payload.post_id_or_url
        if not target_url.startswith("http"):
            # Assume post ID
            clean_id = re.sub(r"^t3_", "", target_url)
            target_url = f"https://www.reddit.com/comments/{clean_id}/"

        async with self.pool.get_page() as page:
            await page.goto(target_url, wait_until="domcontentloaded")

            if payload.parent_comment_id:
                # Nested reply
                clean_comment_id = re.sub(r"^t1_", "", payload.parent_comment_id)
                reply_trigger = page.locator(
                    f'shreddit-comment[thingid*="{clean_comment_id}"] button[aria-label*="reply"], button[data-testid="reply-button"]'
                ).first
                await reply_trigger.wait_for(state="visible", timeout=6000)
                await reply_trigger.click()

            # Focus comment input
            comment_input = page.locator(RedditLocators.COMMENT_BOX).first
            await comment_input.wait_for(state="visible", timeout=6000)
            box = await comment_input.bounding_box()
            if box:
                await MouseController.human_move_and_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
            await KeyboardController.human_type(comment_input, payload.body)

            # Submit
            submit_btn = page.locator(RedditLocators.COMMENT_SUBMIT_BUTTON).first
            await submit_btn.wait_for(state="visible", timeout=5000)
            box = await submit_btn.bounding_box()
            if box:
                await MouseController.human_move_and_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
            else:
                await submit_btn.click()

            return RedditCommentResultDTO(
                success=True,
                post_id=payload.post_id_or_url,
                permalink=target_url,
                body=payload.body,
                message="Comment submitted successfully with human cadence."
            )

    # =========================================================================
    # 4. Engagement: Voting & Saving
    # =========================================================================

    async def vote(self, target_id_or_url: str, direction: int) -> RedditActionResultDTO:
        """Upvotes (1), downvotes (-1), or removes vote (0) on a post or comment."""
        async with self.pool.get_page() as page:
            if target_id_or_url.startswith("http"):
                await page.goto(target_id_or_url, wait_until="domcontentloaded")
                target_locator = page
            else:
                clean_id = re.sub(r"^t[13]_", "", target_id_or_url)
                await page.goto(f"https://www.reddit.com/comments/{clean_id}/", wait_until="domcontentloaded")
                target_locator = page

            if direction == 1:
                btn = target_locator.locator(RedditLocators.UPVOTE_BUTTON).first
            elif direction == -1:
                btn = target_locator.locator(RedditLocators.DOWNVOTE_BUTTON).first
            else:
                # Re-click active button to clear
                btn = target_locator.locator(RedditLocators.UPVOTE_BUTTON).first

            await btn.wait_for(state="visible", timeout=6000)
            box = await btn.bounding_box()
            if box:
                await MouseController.human_move_and_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
            else:
                await btn.click()

            action_name = "upvote" if direction == 1 else ("downvote" if direction == -1 else "clear_vote")
            return RedditActionResultDTO(
                success=True,
                action=action_name,
                target_id=target_id_or_url,
                message=f"Successfully executed {action_name} on target."
            )

    async def save_post(self, target_id_or_url: str, unsave: bool = False) -> RedditActionResultDTO:
        """Saves or unsaves a post or comment."""
        async with self.pool.get_page() as page:
            url = target_id_or_url if target_id_or_url.startswith("http") else f"https://www.reddit.com/comments/{re.sub(r'^t[13]_', '', target_id_or_url)}/"
            await page.goto(url, wait_until="domcontentloaded")

            btn = page.locator(RedditLocators.SAVE_BUTTON).first
            await btn.wait_for(state="visible", timeout=6000)
            await btn.click()

            action = "unsave" if unsave else "save"
            return RedditActionResultDTO(
                success=True,
                action=action,
                target_id=target_id_or_url,
                message=f"Successfully executed {action} on {target_id_or_url}."
            )

    # =========================================================================
    # 5. Thread & Nested Discussion Tree Reading
    # =========================================================================

    def _parse_comment_node(self, comment_raw: Dict[str, Any], depth: int = 0) -> Optional[RedditCommentNodeDTO]:
        """Recursively parses a comment node from Reddit JSON structure."""
        if comment_raw.get("kind") != "t1":
            return None

        data = comment_raw.get("data", {})
        node = RedditCommentNodeDTO(
            comment_id=data.get("name", data.get("id", "")),
            author=data.get("author", "[deleted]"),
            score=data.get("score", 0),
            body=data.get("body", ""),
            depth=depth,
            parent_id=data.get("parent_id")
        )

        replies_raw = data.get("replies")
        if isinstance(replies_raw, dict):
            children = replies_raw.get("data", {}).get("children", [])
            for child in children:
                child_node = self._parse_comment_node(child, depth=depth + 1)
                if child_node:
                    node.replies.append(child_node)

        return node

    async def read_thread(self, thread_url_or_id: str, max_depth: int = 5) -> RedditThreadDTO:
        """Extracts complete thread and parses full hierarchical comment tree."""
        if thread_url_or_id.startswith("http"):
            json_url = thread_url_or_id.rstrip("/") + ".json"
        else:
            clean_id = re.sub(r"^t3_", "", thread_url_or_id)
            json_url = f"https://www.reddit.com/comments/{clean_id}.json"

        async with self.pool.get_page() as page:
            response = await page.request.get(json_url)
            if response.status == 200:
                payload = await response.json()
                if isinstance(payload, list) and len(payload) >= 2:
                    post_data = payload[0]["data"]["children"][0]["data"]
                    comments_data = payload[1]["data"]["children"]

                    comment_nodes: List[RedditCommentNodeDTO] = []
                    for raw_child in comments_data:
                        parsed = self._parse_comment_node(raw_child, depth=0)
                        if parsed:
                            comment_nodes.append(parsed)

                    return RedditThreadDTO(
                        post_id=post_data.get("name", ""),
                        title=post_data.get("title", ""),
                        author=post_data.get("author", ""),
                        subreddit=post_data.get("subreddit", ""),
                        score=post_data.get("score", 0),
                        upvote_ratio=post_data.get("upvote_ratio"),
                        url=post_data.get("url"),
                        permalink=f"https://www.reddit.com{post_data.get('permalink')}",
                        flair=post_data.get("link_flair_text"),
                        body=post_data.get("selftext"),
                        total_comments=post_data.get("num_comments", 0),
                        comments=comment_nodes
                    )

            # Fallback to DOM rendering
            direct_url = thread_url_or_id if thread_url_or_id.startswith("http") else f"https://www.reddit.com/comments/{thread_url_or_id}/"
            await page.goto(direct_url, wait_until="domcontentloaded")

            title_elem = page.locator("h1").first
            title = (await title_elem.inner_text()).strip() if await title_elem.count() > 0 else "Reddit Post"

            return RedditThreadDTO(
                post_id=thread_url_or_id,
                title=title,
                author="unknown",
                subreddit="unknown",
                permalink=direct_url,
                comments=[]
            )

    # =========================================================================
    # 6. Discovery: Subreddit Browsing, Search & User Audit
    # =========================================================================

    async def browse_subreddit(
        self,
        subreddit: str,
        sort: str = "hot",
        time_filter: Optional[str] = None,
        limit: int = 25
    ) -> RedditSubredditBrowseDTO:
        """Browses posts from a subreddit using structured listings."""
        sub = subreddit.replace("r/", "").strip()
        sort_clean = sort.lower()
        json_url = f"https://www.reddit.com/r/{sub}/{sort_clean}.json?limit={limit}"
        if time_filter:
            json_url += f"&t={time_filter}"

        async with self.pool.get_page() as page:
            response = await page.request.get(json_url)
            posts: List[RedditPostSummaryDTO] = []
            if response.status == 200:
                data = await response.json()
                children = data.get("data", {}).get("children", [])
                for child in children:
                    cd = child.get("data", {})
                    posts.append(
                        RedditPostSummaryDTO(
                            post_id=cd.get("name", cd.get("id", "")),
                            title=cd.get("title", ""),
                            author=cd.get("author", "[deleted]"),
                            subreddit=cd.get("subreddit", sub),
                            score=cd.get("score", 0),
                            comments_count=cd.get("num_comments", 0),
                            url=cd.get("url"),
                            permalink=f"https://www.reddit.com{cd.get('permalink')}",
                            flair=cd.get("link_flair_text"),
                            body_preview=cd.get("selftext", "")[:250] if cd.get("selftext") else None
                        )
                    )

            return RedditSubredditBrowseDTO(
                subreddit=sub,
                sort=sort_clean,
                time_filter=time_filter,
                count=len(posts),
                posts=posts
            )

    async def search(
        self,
        query: str,
        subreddit: Optional[str] = None,
        sort: str = "relevance",
        time_filter: str = "all",
        limit: int = 25
    ) -> RedditSearchDTO:
        """Performs advanced search across Reddit or scoped to a subreddit."""
        q_enc = quote_plus(query)
        if subreddit:
            sub = subreddit.replace("r/", "").strip()
            json_url = f"https://www.reddit.com/r/{sub}/search.json?q={q_enc}&restrict_sr=1&sort={sort}&t={time_filter}&limit={limit}"
        else:
            json_url = f"https://www.reddit.com/search.json?q={q_enc}&sort={sort}&t={time_filter}&limit={limit}"

        async with self.pool.get_page() as page:
            response = await page.request.get(json_url)
            results: List[RedditPostSummaryDTO] = []
            if response.status == 200:
                data = await response.json()
                children = data.get("data", {}).get("children", [])
                for child in children:
                    cd = child.get("data", {})
                    results.append(
                        RedditPostSummaryDTO(
                            post_id=cd.get("name", cd.get("id", "")),
                            title=cd.get("title", ""),
                            author=cd.get("author", "[deleted]"),
                            subreddit=cd.get("subreddit", subreddit or ""),
                            score=cd.get("score", 0),
                            comments_count=cd.get("num_comments", 0),
                            url=cd.get("url"),
                            permalink=f"https://www.reddit.com{cd.get('permalink')}",
                            flair=cd.get("link_flair_text"),
                            body_preview=cd.get("selftext", "")[:250] if cd.get("selftext") else None
                        )
                    )

            return RedditSearchDTO(
                query=query,
                subreddit=subreddit,
                sort=sort,
                time_filter=time_filter,
                total_found=len(results),
                results=results
            )

    async def browse_user(self, username: str, limit: int = 20) -> RedditUserHistoryDTO:
        """Audits a user's submitted posts, comments, and public activity."""
        clean_user = username.replace("u/", "").strip()
        json_url = f"https://www.reddit.com/user/{clean_user}/submitted.json?limit={limit}"

        async with self.pool.get_page() as page:
            response = await page.request.get(json_url)
            posts: List[RedditPostSummaryDTO] = []
            if response.status == 200:
                data = await response.json()
                children = data.get("data", {}).get("children", [])
                for child in children:
                    cd = child.get("data", {})
                    posts.append(
                        RedditPostSummaryDTO(
                            post_id=cd.get("name", cd.get("id", "")),
                            title=cd.get("title", ""),
                            author=clean_user,
                            subreddit=cd.get("subreddit", ""),
                            score=cd.get("score", 0),
                            comments_count=cd.get("num_comments", 0),
                            permalink=f"https://www.reddit.com{cd.get('permalink')}",
                            created_utc=str(cd.get("created_utc"))
                        )
                    )

            return RedditUserHistoryDTO(
                username=clean_user,
                recent_posts=posts
            )

    # =========================================================================
    # 7. Direct Messaging & Inbox Processing
    # =========================================================================

    async def send_message(self, payload: RedditSendMessageDTO) -> RedditActionResultDTO:
        """Sends a private direct message to a user."""
        async with self.pool.get_page() as page:
            await page.goto("https://www.reddit.com/message/compose/", wait_until="domcontentloaded")

            rec_input = page.locator(RedditLocators.MESSAGE_RECIPIENT_INPUT).first
            subj_input = page.locator(RedditLocators.MESSAGE_SUBJECT_INPUT).first
            body_input = page.locator(RedditLocators.MESSAGE_BODY_TEXTAREA).first
            send_btn = page.locator(RedditLocators.MESSAGE_SEND_BUTTON).first

            await rec_input.wait_for(state="visible", timeout=6000)
            await rec_input.fill(payload.recipient)

            await subj_input.wait_for(state="visible", timeout=4000)
            await KeyboardController.human_type(subj_input, payload.subject)

            await body_input.wait_for(state="visible", timeout=4000)
            await KeyboardController.human_type(body_input, payload.body)

            box = await send_btn.bounding_box()
            if box:
                await MouseController.human_move_and_click(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2)
            else:
                await send_btn.click()

            return RedditActionResultDTO(
                success=True,
                action="send_message",
                target_id=payload.recipient,
                message=f"Private message successfully sent to u/{payload.recipient}."
            )

    async def check_inbox(self, limit: int = 15) -> List[RedditInboxItemDTO]:
        """Reads recent inbox messages and notifications."""
        async with self.pool.get_page() as page:
            json_url = f"https://www.reddit.com/message/inbox.json?limit={limit}"
            response = await page.request.get(json_url)
            items: List[RedditInboxItemDTO] = []
            if response.status == 200:
                data = await response.json()
                children = data.get("data", {}).get("children", [])
                for child in children:
                    cd = child.get("data", {})
                    items.append(
                        RedditInboxItemDTO(
                            item_id=cd.get("name", cd.get("id", "")),
                            type=cd.get("was_comment", False) and "comment_reply" or "message",
                            author=cd.get("author", "[deleted]"),
                            subject=cd.get("subject"),
                            body=cd.get("body", ""),
                            context_url=cd.get("context"),
                            unread=cd.get("new", False)
                        )
                    )
            return items

    # =========================================================================
    # 8. Lead Generation & Value-First Technical Pitching
    # =========================================================================

    async def hunt_leads(
        self,
        subreddits: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        min_urgency: int = 5
    ) -> List[RedditLeadDTO]:
        """Discovers high-intent technical hurdles and client acquisition opportunities."""
        target_subs = subreddits or ["webscraping", "Python", "freelance", "datascience"]
        search_terms = keywords or ["scraping blocked", "cloudflare 403", "playwright turnstile", "hire scraper"]

        leads: List[RedditLeadDTO] = []

        for sub in target_subs:
            for kw in search_terms:
                search_res = await self.search(query=kw, subreddit=sub, sort="new", limit=10)
                for item in search_res.results:
                    title_lower = item.title.lower()
                    body_lower = (item.body_preview or "").lower()

                    urgency = 5
                    pain_points: List[str] = []

                    if any(term in title_lower or term in body_lower for term in ["blocked", "turnstile", "cloudflare", "403 forbidden", "ip ban"]):
                        urgency += 3
                        pain_points.append("Anti-bot detection / TLS / Cloudflare Turnstile block")

                    if any(term in title_lower or term in body_lower for term in ["hire", "budget", "paid", "need dev", "contract"]):
                        urgency += 2
                        pain_points.append("Commercial hiring or outsourcing intent")

                    if urgency >= min_urgency:
                        leads.append(
                            RedditLeadDTO(
                                post_id=item.post_id,
                                title=item.title,
                                author=item.author,
                                subreddit=item.subreddit,
                                url=item.permalink,
                                urgency_score=min(urgency, 10),
                                budget_intent="High" if "hire" in title_lower or "budget" in title_lower else "Medium",
                                pain_points=pain_points,
                                recommended_strategy="Provide root cause analysis of anti-bot challenge and offer open-source behavioral proof."
                            )
                        )

        # De-duplicate by post_id
        unique_leads = {lead.post_id: lead for lead in leads}.values()
        return list(unique_leads)

    def generate_pitch(self, lead: RedditLeadDTO) -> RedditPitchDTO:
        """Constructs an authoritative, non-salesy technical solution pitch."""
        technical_breakdown = (
            f"The issue encountered in '{lead.title}' stems from behavioral heuristics and anti-bot profiling: "
            "headless browser fingerprint leaks (e.g. navigator.webdriver, CDP artifacts), linear synthetic mouse trajectories, "
            "and unhedged request concurrency triggering rate limits."
        )

        proposed_architecture = (
            "Deploy a 3-tier clean architecture solution using Playwright with:\n"
            "1. Multi-context browser pooling to eliminate redundant process overhead.\n"
            "2. Cubic Bézier mouse movement with Weibull-distributed typing latency.\n"
            "3. Route-level asset abortion (blocking heavy images/fonts) to preserve bandwidth.\n"
            "4. Full-jitter exponential backoff retry policies for HTTP 429/503."
        )

        ready_pitch = (
            f"Hey u/{lead.author},\n\n"
            f"Regarding your issue with: \"{lead.title}\"\n\n"
            "This typically happens because modern bot mitigations detect headless automation via TLS fingerprints, "
            "rigid linear mouse coordinates, and lack of realistic keystroke intervals. Standard headless browsers leave obvious CDP artifacts.\n\n"
            "A battle-tested architectural fix is to enforce:\n"
            "• Single browser multi-context pooling (`BrowserPoolManager`)\n"
            "• Human-mimetic cubic Bézier curve mouse paths with sub-pixel micro-jitter\n"
            "• Weibull distributed keystroke delays\n"
            "• Route-level asset abortion to prevent heavy network locks\n\n"
            "I recently implemented this entire architecture in Python in an open-source engine:\n"
            "https://github.com/sadik004/behavioral-playwright\n\n"
            "Feel free to check out the repo or let me know if you want me to share the exact routing snippet for your stack!"
        )

        return RedditPitchDTO(
            post_id=lead.post_id,
            recipient=lead.author,
            title=lead.title,
            technical_breakdown=technical_breakdown,
            proposed_architecture=proposed_architecture,
            code_proof_link="https://github.com/sadik004/behavioral-playwright",
            ready_to_send_pitch=ready_pitch
        )
