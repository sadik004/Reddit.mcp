"""
Stealth Browser Context Pool Manager.
Powered directly by behavioral_playwright framework for process pooling,
route-level asset abortion, and authentic biometric fingerprint evasion.
"""

from __future__ import annotations
import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Optional
from playwright.async_api import Page, Route

from behavioral_playwright.browser.pool import BrowserPoolManager as BPBrowserPoolManager
from behavioral_playwright.config.settings import BrowserConfig as BPBrowserConfig
from behavioral_playwright.fingerprint.generator import FingerprintGenerator
from reddit_mcp.config import RedditConfig

logger = logging.getLogger("reddit_mcp.browser")

# Reddit-specific telemetry and tracking domains blocked on route level
REDDIT_BLOCKED_DOMAINS = (
    "google-analytics.com",
    "googletagmanager.com",
    "branch.io",
    "redditstatic.com/ads",
    "redditmedia.com/ads",
    "stats.redditmedia.com",
    "events.reddit.com",
)


class BrowserPoolManager:
    """
    Adapter around behavioral_playwright's BrowserPoolManager.
    Enforces process pooling, Reddit session persistence, and anti-bot evasion.
    """

    _instance: Optional[BrowserPoolManager] = None
    _lock = asyncio.Lock()

    def __init__(self, config: Optional[RedditConfig] = None):
        self.config = config or RedditConfig()
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu",
            "--hide-scrollbars",
            "--mute-audio",
        ]

        self._bp_config = BPBrowserConfig(
            headless=self.config.headless,
            width=self.config.viewport_width,
            height=self.config.viewport_height,
            timeout_ms=self.config.navigation_timeout_ms,
            allow_media=False,
            args=launch_args,
        )
        self._pool = BPBrowserPoolManager(config=self._bp_config)
        self._fingerprint_gen = FingerprintGenerator()
        self._evasion_script: Optional[str] = None

    @classmethod
    async def get_instance(cls, config: Optional[RedditConfig] = None) -> BrowserPoolManager:
        """Thread-safe singleton accessor."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(config)
        return cls._instance

    @property
    def active_contexts(self) -> int:
        return self._pool.active_contexts

    def _get_evasion_script(self) -> str:
        if self._evasion_script is None:
            profile = self._fingerprint_gen.generate()
            self._evasion_script = self._fingerprint_gen.generate_evasion_script(profile)
        return self._evasion_script

    @asynccontextmanager
    async def get_page(self) -> AsyncGenerator[Page, None]:
        """Provides an isolated, stealth-configured browser page with automatic resource cleanup."""
        context_kwargs: dict = {
            "user_agent": self.config.user_agent,
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "color_scheme": "dark",
        }

        # Configure proxy with credentials if specified
        if self.config.proxy_server:
            proxy_dict: dict = {"server": self.config.proxy_server}
            if self.config.proxy_username:
                proxy_dict["username"] = self.config.proxy_username
            if self.config.proxy_password:
                proxy_dict["password"] = self.config.proxy_password
            context_kwargs["proxy"] = proxy_dict

        # Load authenticated session if available
        storage_path = Path(self.config.storage_state) if self.config.storage_state else None
        if storage_path and storage_path.exists():
            context_kwargs["storage_state"] = str(storage_path)
            logger.info(f"Loaded storage_state from {storage_path}")

        if not self._pool.is_initialized:
            await self._pool.initialize()

        viewport = {
            "width": self.config.viewport_width,
            "height": self.config.viewport_height,
        }

        async with self._pool.get_context(allow_media=False, viewport=viewport, **context_kwargs) as context:
            # Inject behavioral_playwright fingerprint evasion script
            evasion = self._get_evasion_script()
            await context.add_init_script(evasion)

            # Reddit-specific ad/telemetry abort route
            async def _abort_reddit_telemetry(route: Route) -> None:
                url = route.request.url.lower()
                if any(domain in url for domain in REDDIT_BLOCKED_DOMAINS):
                    await route.abort()
                    return
                try:
                    await route.continue_()
                except Exception:
                    pass

            await context.route("**/*", _abort_reddit_telemetry)

            page = await context.new_page()
            page.set_default_navigation_timeout(self.config.navigation_timeout_ms)
            page.set_default_timeout(self.config.navigation_timeout_ms)

            try:
                yield page
            finally:
                if not page.is_closed():
                    try:
                        await page.close()
                    except Exception:
                        pass

    async def close(self) -> None:
        """Gracefully terminates master browser and playwright process."""
        await self._pool.shutdown()
        logger.info("Closed behavioral_playwright browser pool cleanly.")

