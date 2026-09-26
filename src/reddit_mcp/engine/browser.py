"""
Stealth Browser Context Pool Manager.
Enforces single browser multi-context pooling, route-level asset abortion,
dynamic DOM waiting, and residential proxy integration.
"""

from __future__ import annotations
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    BrowserContext,
    Page,
    Route,
)
from reddit_mcp.config import RedditConfig

logger = logging.getLogger("reddit_mcp.browser")


class BrowserPoolManager:
    """Manages browser lifecycle, connection pooling, and stealth configuration."""

    _instance: Optional[BrowserPoolManager] = None
    _lock = asyncio.Lock()

    def __init__(self, config: Optional[RedditConfig] = None):
        self.config = config or RedditConfig()
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._active_contexts: int = 0

    @classmethod
    async def get_instance(cls, config: Optional[RedditConfig] = None) -> BrowserPoolManager:
        """Thread-safe singleton accessor."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(config)
        return cls._instance

    async def _ensure_browser(self) -> Browser:
        """Launches the shared browser instance if not already running."""
        if self._browser is None or not self._browser.is_connected():
            if self._playwright is None:
                self._playwright = await async_playwright().start()

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

            proxy_dict = None
            if self.config.proxy_server:
                proxy_dict = {"server": self.config.proxy_server}
                if self.config.proxy_username and self.config.proxy_password:
                    proxy_dict["username"] = self.config.proxy_username
                    proxy_dict["password"] = self.config.proxy_password

            self._browser = await self._playwright.chromium.launch(
                headless=self.config.headless,
                args=launch_args,
                proxy=proxy_dict,
            )
            logger.info("Initialized shared Chromium browser process.")
        return self._browser

    @staticmethod
    async def _route_abort_heavy_assets(route: Route) -> None:
        """Aborts images, fonts, media, and analytics to preserve bandwidth and accelerate DOM execution."""
        request = route.request
        resource_type = request.resource_type

        # Block heavy or tracking resources
        if resource_type in ("image", "font", "media"):
            await route.abort()
            return

        # Block third-party tracking beacons
        url = request.url.lower()
        blocked_domains = [
            "google-analytics.com",
            "googletagmanager.com",
            "branch.io",
            "redditstatic.com/ads",
            "redditmedia.com/ads",
            "stats.redditmedia.com",
            "events.reddit.com",
        ]
        if any(domain in url for domain in blocked_domains):
            await route.abort()
            return

        await route.continue_()

    @asynccontextmanager
    async def get_page(self) -> AsyncGenerator[Page, None]:
        """Provides an isolated, stealth-configured browser page with automatic resource cleanup."""
        browser = await self._ensure_browser()

        context_kwargs: dict = {
            "user_agent": self.config.user_agent,
            "viewport": {
                "width": self.config.viewport_width,
                "height": self.config.viewport_height
            },
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "color_scheme": "dark",
        }

        # Load authenticated session if available
        if self.config.storage_state and self.config.storage_state.exists():
            context_kwargs["storage_state"] = str(self.config.storage_state)
            logger.info(f"Loaded storage_state from {self.config.storage_state}")

        context: BrowserContext = await browser.new_context(**context_kwargs)
        self._active_contexts += 1

        # Anti-detection stealth scripts
        await context.add_init_script("""
            // Mask webdriver flag
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Spoof plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Spoof languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // Spoof Chrome runtime object
            window.chrome = {
                runtime: {}
            };
        """)

        page: Page = await context.new_page()
        page.set_default_navigation_timeout(self.config.navigation_timeout_ms)
        page.set_default_timeout(self.config.navigation_timeout_ms)

        # Route-level asset abortion
        await page.route("**/*", self._route_abort_heavy_assets)

        try:
            yield page
        finally:
            await page.close()
            await context.close()
            self._active_contexts -= 1

    async def close(self) -> None:
        """Gracefully closes all browser contexts and playwright processes."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("Closed browser pool and terminated playwright.")
