"""
tests/test_behavior.py
-----------------------
Unit tests for head_pose estimation and engagement classification.
"""

import numpy as np
import pytest


# ── compute_engagement ─────────────────────────────────────────────────────────

def test_engagement_high():
    from behavior.engagement import compute_engagement
    assert compute_engagement(pitch=2.0, yaw=5.0) == "high"


def test_engagement_medium_yaw():
    from behavior.engagement import compute_engagement
    # yaw > 20° but < 30° → medium
    assert compute_engagement(pitch=0.0, yaw=25.0) == "medium"


def test_engagement_low_yaw():
    from behavior.engagement import compute_engagement
    # yaw > 30° → low
    assert compute_engagement(pitch=0.0, yaw=35.0) == "low"


def test_engagement_low_pitch():
    from behavior.engagement import compute_engagement
    # pitch < -15° → low
    assert compute_engagement(pitch=-20.0, yaw=0.0) == "low"


def test_engagement_backwards_alias():
    """Legacy engagement() function should behave identically."""
    from behavior.engagement import engagement
    assert engagement(pitch=0.0, yaw=5.0) == "high"


# ── estimate_pose ──────────────────────────────────────────────────────────────

def test_estimate_pose_returns_tuple(blank_frame):
    """estimate_pose() should always return a (pitch, yaw, roll) tuple."""
    from behavior.head_pose import estimate_pose

    result = estimate_pose(blank_frame)
    assert isinstance(result, tuple)
    assert len(result) == 3
    # All values should be floats
    for v in result:
        assert isinstance(v, float)


def test_estimate_pose_with_none():
    """Passing None should return (0, 0, 0) without crashing."""
    from behavior.head_pose import estimate_pose

    result = estimate_pose(None)
    assert result == (0.0, 0.0, 0.0)


def test_estimate_pose_with_empty_array():
    """Passing an empty array should return (0, 0, 0) without crashing."""
    from behavior.head_pose import estimate_pose

    result = estimate_pose(np.array([]))
    assert result == (0.0, 0.0, 0.0)
