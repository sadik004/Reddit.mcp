"""
Human-mimetic mouse trajectory generator using cubic Bézier curves.
Generates organic acceleration, decelerations, and sub-pixel micro-jitters.
"""

import math
import random
from typing import List, Tuple
from playwright.async_api import Page


class MouseController:
    """Human-mimetic mouse controller generating organic trajectories."""

    @staticmethod
    def _calculate_bezier_point(
        p0: Tuple[float, float],
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        p3: Tuple[float, float],
        t: float
    ) -> Tuple[float, float]:
        """Calculates a point on a cubic Bézier curve at parameter t in [0, 1]."""
        u = 1.0 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t

        x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
        y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
        return (x, y)

    @classmethod
    def generate_human_path(
        cls,
        start_x: float,
        start_y: float,
        dest_x: float,
        dest_y: float,
        steps: int = 25
    ) -> List[Tuple[float, float]]:
        """Generates a natural mouse curve with randomized control points and micro-jitters."""
        dx = dest_x - start_x
        dy = dest_y - start_y
        dist = math.hypot(dx, dy)

        if dist < 5.0:
            return [(dest_x, dest_y)]

        # Determine perpendicular offset for curve deflection
        normal_x = -dy / dist
        normal_y = dx / dist
        spread = dist * random.uniform(0.15, 0.35)
        direction = 1 if random.random() < 0.5 else -1

        # Control point 1 (close to start)
        cp1_x = start_x + dx * random.uniform(0.2, 0.4) + normal_x * spread * direction
        cp1_y = start_y + dy * random.uniform(0.2, 0.4) + normal_y * spread * direction

        # Control point 2 (close to destination, smaller perturbation)
        cp2_x = start_x + dx * random.uniform(0.6, 0.8) + normal_x * spread * direction * 0.5
        cp2_y = start_y + dy * random.uniform(0.6, 0.8) + normal_y * spread * direction * 0.5

        path: List[Tuple[float, float]] = []
        p0 = (start_x, start_y)
        p1 = (cp1_x, cp1_y)
        p2 = (cp2_x, cp2_y)
        p3 = (dest_x, dest_y)

        for i in range(1, steps + 1):
            # Sigmoid / Ease-in-out time warp
            linear_t = i / steps
            # Smoothstep easing
            t = linear_t * linear_t * (3.0 - 2.0 * linear_t)
            bx, by = cls._calculate_bezier_point(p0, p1, p2, p3, t)
            
            # Subtle micro-jitter (less jitter near destination)
            damping = 1.0 - linear_t
            jitter_x = random.uniform(-0.8, 0.8) * damping
            jitter_y = random.uniform(-0.8, 0.8) * damping
            path.append((bx + jitter_x, by + jitter_y))

        return path

    @classmethod
    async def human_move_and_click(
        cls,
        page: Page,
        target_x: float,
        target_y: float,
        button: str = "left"
    ) -> None:
        """Moves mouse across an organic curve to the target and clicks."""
        # Add random landing offset within clickable area
        final_x = target_x + random.uniform(-2.0, 2.0)
        final_y = target_y + random.uniform(-2.0, 2.0)

        # Approximate current position or start from viewport margin
        path = cls.generate_human_path(
            start_x=random.uniform(100.0, 400.0),
            start_y=random.uniform(100.0, 300.0),
            dest_x=final_x,
            dest_y=final_y,
            steps=random.randint(20, 32)
        )

        for px, py in path:
            await page.mouse.move(px, py)

        await page.mouse.click(final_x, final_y, button=button)
