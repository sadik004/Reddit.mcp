"""
Human-mimetic keyboard controller using Weibull distributed typing cadences.
Simulates natural pauses after punctuation, spaces, and keystroke variations.
"""

import asyncio
import random
from playwright.async_api import Locator


class KeyboardController:
    """Human-mimetic keyboard typing simulator."""

    @staticmethod
    def _sample_weibull_delay(min_ms: float = 35.0, max_ms: float = 120.0) -> float:
        """Samples a keystroke latency using Weibull distribution for realistic typing dynamics."""
        # Shape parameter k ~ 2.0 (Rayleigh-like distribution), scale parameter lambda ~ 50ms
        delay = random.weibullvariate(50.0, 2.0)
        return max(min_ms, min(delay, max_ms)) / 1000.0

    @classmethod
    async def human_type(
        cls,
        locator: Locator,
        text: str,
        min_ms: float = 25.0,
        max_ms: float = 85.0
    ) -> None:
        """Types text with natural human cadence, supporting newlines and burst typing for long inputs."""
        await locator.focus()

        # For long inputs (> 150 chars), use human burst typing to prevent MCP client timeout
        if len(text) > 150:
            lines = text.split("\n")
            for line_idx, line in enumerate(lines):
                if line_idx > 0:
                    await locator.press("Enter")
                    await asyncio.sleep(random.uniform(0.10, 0.22))

                words = line.split(" ")
                for word_idx, word in enumerate(words):
                    if word_idx > 0:
                        await locator.press_sequentially(" ", delay=0)
                        await asyncio.sleep(random.uniform(0.02, 0.05))

                    if word:
                        chunk_delay = cls._sample_weibull_delay(min_ms=10.0, max_ms=35.0)
                        await locator.press_sequentially(word, delay=int(chunk_delay * 1000))

                    if word.endswith((".", "!", "?", ":")):
                        await asyncio.sleep(random.uniform(0.10, 0.22))
                    elif word.endswith((",", ";")):
                        await asyncio.sleep(random.uniform(0.05, 0.10))
            return

        # Short text: authentic character-by-character typing
        for char in text:
            if char == "\n":
                await locator.press("Enter")
                await asyncio.sleep(random.uniform(0.12, 0.25))
                continue

            await locator.press_sequentially(char, delay=0)
            base_delay = cls._sample_weibull_delay(min_ms, max_ms)

            # Extended pause after sentence boundaries or commas
            if char in ".!?:":
                base_delay += random.uniform(0.12, 0.25)
            elif char in ",;":
                base_delay += random.uniform(0.06, 0.12)
            elif char == " ":
                base_delay += random.uniform(0.03, 0.07)

            # Fast micro-burst for regular characters (2-5% chance of short hesitation)
            if random.random() < 0.03:
                base_delay += random.uniform(0.15, 0.30)

            await asyncio.sleep(base_delay)
