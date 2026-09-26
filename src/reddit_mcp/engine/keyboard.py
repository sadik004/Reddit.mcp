"""
Human-mimetic keyboard controller powered by behavioral_playwright.
Uses Dhakal keyboard kinematics, Euclidean key distance modulation,
and Weibull latency distributions from LinguisticKeystrokeDynamicsEngine.
"""

from __future__ import annotations
import asyncio
import random
from typing import Optional
from playwright.async_api import Locator

from behavioral_playwright.powerplay.keystrokes import LinguisticKeystrokeDynamicsEngine


class KeyboardController:
    """Human-mimetic keyboard controller delegating to behavioral_playwright."""

    _engine: Optional[LinguisticKeystrokeDynamicsEngine] = None

    @classmethod
    def _get_engine(cls) -> LinguisticKeystrokeDynamicsEngine:
        if cls._engine is None:
            cls._engine = LinguisticKeystrokeDynamicsEngine()
        return cls._engine

    @classmethod
    async def human_type(
        cls,
        locator: Locator,
        text: str,
        min_ms: float = 25.0,
        max_ms: float = 85.0
    ) -> None:
        """
        Types text with authentic human cadence using behavioral_playwright's
        LinguisticKeystrokeDynamicsEngine, supporting newlines and burst typing for long inputs.
        """
        await locator.focus()
        engine = cls._get_engine()

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
                        seq = engine.generate_typing_sequence(word)
                        for ev in seq:
                            if ev.get("event") == "keydown":
                                key = ev.get("key", "")
                                await locator.press_sequentially(key, delay=0)
                                # Micro flight delay clamped between 8ms and 35ms
                                await asyncio.sleep(random.uniform(0.008, 0.035))

                    if word.endswith((".", "!", "?", ":")):
                        await asyncio.sleep(random.uniform(0.10, 0.22))
                    elif word.endswith((",", ";")):
                        await asyncio.sleep(random.uniform(0.05, 0.10))
            return

        # Short / medium text: authentic character-by-character typing with Dhakal kinematics
        for line_idx, line in enumerate(text.split("\n")):
            if line_idx > 0:
                await locator.press("Enter")
                await asyncio.sleep(random.uniform(0.12, 0.25))

            seq = engine.generate_typing_sequence(line)
            last_ts = 0
            for ev in seq:
                if ev.get("event") == "keydown":
                    key = ev.get("key", "")
                    await locator.press_sequentially(key, delay=0)
                    current_ts = ev.get("timestamp_ms", 0)
                    delta_ms = current_ts - last_ts if last_ts > 0 else 30
                    last_ts = current_ts

                    # Clamp delay between min_ms and max_ms
                    flight_sec = min(max_ms / 1000.0, max(min_ms / 1000.0, delta_ms / 1000.0))

                    if key in ".!?:":
                        flight_sec += random.uniform(0.10, 0.20)
                    elif key in ",;":
                        flight_sec += random.uniform(0.05, 0.10)
                    elif key == " ":
                        flight_sec += random.uniform(0.02, 0.05)

                    await asyncio.sleep(flight_sec)

