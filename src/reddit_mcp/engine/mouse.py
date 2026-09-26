"""
Human-mimetic mouse trajectory and input controller.
Powered directly by behavioral_playwright's BiomechanicalTremorEngine and MouseController.
"""

from __future__ import annotations
import asyncio
import random
from typing import List, Tuple, Optional, Any
from playwright.async_api import Page

from behavioral_playwright.automation.mouse import MouseController as BPMouseController
from behavioral_playwright.powerplay.biomechanics import BiomechanicalTremorEngine


class MouseController:
    """Human-mimetic mouse controller delegating to behavioral_playwright."""

    _last_position: Optional[Tuple[float, float]] = None
    _engine: Optional[BiomechanicalTremorEngine] = None

    @classmethod
    def _get_engine(cls) -> BiomechanicalTremorEngine:
        if cls._engine is None:
            cls._engine = BiomechanicalTremorEngine()
        return cls._engine

    @classmethod
    def generate_human_path(
        cls,
        start_x: float,
        start_y: float,
        dest_x: float,
        dest_y: float,
        steps: int = 25
    ) -> List[Tuple[float, float]]:
        """
        Generates a natural biometric mouse curve with Costello saccadic search,
        quadratic Bezier curvature, and Harris-Wolpert SDN noise via behavioral_playwright.
        """
        engine = cls._get_engine()
        raw_path = engine.generate_bezier_trajectory(
            start_pos=(float(start_x), float(start_y)),
            target_pos=(float(dest_x), float(dest_y)),
            steps=steps
        )
        return [(float(pt[0]), float(pt[1])) for pt in raw_path]

    @classmethod
    async def human_move_and_click(
        cls,
        page: Page,
        target_x: float,
        target_y: float,
        button: str = "left"
    ) -> None:
        """
        Moves mouse across a Costello saccadic curve to target and clicks
        using behavioral_playwright's MouseController with subpixel synthesis.
        """
        start_pos = cls._last_position or (
            random.uniform(100.0, 400.0),
            random.uniform(100.0, 300.0)
        )
        
        engine = cls._get_engine()
        bp_mouse = BPMouseController(
            page=page,
            biomechanics=engine,
            initial_pos=start_pos
        )
        
        # Biomechanical click micro-slip and humanized ballistic movement
        mousedown_pos, mouseup_pos, dwell_time = engine.simulate_click_micro_slip((float(target_x), float(target_y)))
        await bp_mouse.move(mousedown_pos[0], mousedown_pos[1], humanize=True)
        if hasattr(page, "mouse") and hasattr(page.mouse, "down") and hasattr(page.mouse, "up"):
            await page.mouse.down(button=button)
            await asyncio.sleep(dwell_time)
            if hasattr(page.mouse, "move"):
                await page.mouse.move(mouseup_pos[0], mouseup_pos[1])
            await page.mouse.up(button=button)
        elif hasattr(page, "mouse") and hasattr(page.mouse, "click"):
            await page.mouse.click(mousedown_pos[0], mousedown_pos[1], button=button)
        cls._last_position = (mouseup_pos[0], mouseup_pos[1])

