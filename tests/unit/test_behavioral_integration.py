"""
Unit tests validating direct behavioral_playwright framework integration in Reddit MCP.
"""

import pytest
from reddit_mcp.engine.browser import BrowserPoolManager
from reddit_mcp.engine.mouse import MouseController
from reddit_mcp.engine.keyboard import KeyboardController
from behavioral_playwright.powerplay.biomechanics import BiomechanicalTremorEngine
from behavioral_playwright.powerplay.keystrokes import LinguisticKeystrokeDynamicsEngine


def test_mouse_controller_delegates_to_biomechanical_engine():
    """Validates that MouseController uses behavioral_playwright's BiomechanicalTremorEngine."""
    engine = MouseController._get_engine()
    assert isinstance(engine, BiomechanicalTremorEngine)

    # Generate path and verify points
    path = MouseController.generate_human_path(
        start_x=50.0,
        start_y=50.0,
        dest_x=500.0,
        dest_y=400.0,
        steps=20
    )
    assert len(path) == 20
    for pt in path:
        assert isinstance(pt, tuple)
        assert len(pt) == 2
        assert isinstance(pt[0], float)
        assert isinstance(pt[1], float)


def test_keyboard_controller_delegates_to_linguistic_dynamics():
    """Validates that KeyboardController uses behavioral_playwright's LinguisticKeystrokeDynamicsEngine."""
    engine = KeyboardController._get_engine()
    assert isinstance(engine, LinguisticKeystrokeDynamicsEngine)

    # Generate sequence and verify Dhakal kinematics
    seq = engine.generate_typing_sequence("Playwright")
    assert len(seq) == 20  # 10 down + 10 up
    events = [e["event"] for e in seq]
    assert "keydown" in events
    assert "keyup" in events
    timestamps = [e["timestamp_ms"] for e in seq]
    # Timestamps must be strictly non-decreasing
    for i in range(1, len(timestamps)):
        assert timestamps[i] >= timestamps[i - 1]


def test_browser_pool_manager_uses_bp_pool():
    """Validates that BrowserPoolManager wraps behavioral_playwright's BrowserPoolManager."""
    pool_mgr = BrowserPoolManager()
    assert hasattr(pool_mgr, "_pool")
    assert pool_mgr._bp_config.width == 1920
    assert pool_mgr._bp_config.height == 1080
    assert pool_mgr._bp_config.allow_media is False
    assert pool_mgr.active_contexts == 0

    # Verify evasion script generation
    script = pool_mgr._get_evasion_script()
    assert isinstance(script, str)
    assert len(script) > 500
    assert "navigator" in script or "chrome" in script
