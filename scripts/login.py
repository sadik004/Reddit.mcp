"""
Interactive Reddit Session Exporter.
Launches a headed Chromium browser to let you log in manually, bypass CAPTCHA/2FA,
and exports your session cookies and tokens to storage_state.json.
"""

import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Set UTF-8 encoding on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


async def export_reddit_session(output_path: str = "storage_state.json") -> None:
    """Launches interactive browser for manual login and exports session state."""
    print("=" * 70)
    print(" 🛡️  Reddit MCP - Interactive Session Exporter")
    print("=" * 70)
    print("1. A real Chromium browser window will now open.")
    print("2. Log into your Reddit account manually.")
    print("3. Solve any 2FA or CAPTCHA prompts.")
    print("4. Once you reach the Reddit home feed, press ENTER in this terminal.")
    print("=" * 70)

    proxy_server = os.getenv("REDDIT_PROXY_SERVER")
    proxy_user = os.getenv("REDDIT_PROXY_USERNAME")
    proxy_pass = os.getenv("REDDIT_PROXY_PASSWORD")

    proxy_dict = None
    if proxy_server:
        proxy_dict = {"server": proxy_server}
        if proxy_user and proxy_pass:
            proxy_dict["username"] = proxy_user
            proxy_dict["password"] = proxy_pass
        print(f"🔒 Using Proxy: {proxy_server}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--start-maximized"
            ],
            proxy=proxy_dict
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        # Anti-detection stealth scripts via behavioral_playwright FingerprintGenerator
        from behavioral_playwright.fingerprint.generator import FingerprintGenerator
        fg = FingerprintGenerator()
        profile = fg.generate()
        evasion_script = fg.generate_evasion_script(profile)
        await context.add_init_script(evasion_script)

        page = await context.new_page()
        print("Navigating to https://www.reddit.com/login ...")
        await page.goto("https://www.reddit.com/login")

        loop = asyncio.get_running_loop()
        print("\n⏳ Complete login in the browser, then press [ENTER] here to save session...")
        await loop.run_in_executor(None, sys.stdin.readline)

        target = Path(output_path)
        await context.storage_state(path=str(target))
        print(f"\n✅ Session successfully exported to: {target.resolve()}")
        print("You can now run Reddit MCP in headless mode with full authentication!")

        await browser.close()


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "storage_state.json"
    asyncio.run(export_reddit_session(out_file))
