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
        min_ms: float = 35.0,
        max_ms: float = 120.0
    ) -> None:
        """Types text character by character into a locator with natural human cadence."""
        await locator.focus()

        for char in text:
            await locator.press_sequentially(char, delay=0)
            
            base_delay = cls._sample_weibull_delay(min_ms, max_ms)

            # Extended pause after sentence boundaries or commas
            if char in ".!?:":
                base_delay += random.uniform(0.12, 0.28)
            elif char in ",;":
                base_delay += random.uniform(0.06, 0.14)
            elif char == " ":
                base_delay += random.uniform(0.03, 0.08)

            # Fast micro-burst for regular characters (2-5% chance of short hesitate)
            if random.random() < 0.03:
                base_delay += random.uniform(0.15, 0.35)

            await asyncio.sleep(base_delay)
