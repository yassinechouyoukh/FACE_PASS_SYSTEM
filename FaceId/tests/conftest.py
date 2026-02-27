"""
tests/conftest.py
-----------------
Shared pytest fixtures for FacePass AiService test suite.

Heavy dependencies (YOLO, InsightFace, MediaPipe) are mocked out so
tests run on any machine without a GPU or large model files.
"""

import numpy as np
import pytest


# ── Frame fixtures ────────────────────────────────────────────────────────────

@pytest.fixture()
def blank_frame() -> np.ndarray:
    """Return a black 480×640 BGR frame (no faces)."""
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture()
def face_frame() -> np.ndarray:
    """Return a randomly-coloured 480×640 BGR frame (simulated face content)."""
    rng = np.random.default_rng(seed=42)
    return rng.integers(0, 255, (480, 640, 3), dtype=np.uint8)


@pytest.fixture()
def dummy_embedding() -> np.ndarray:
    """Return a normalised 512-D float32 embedding vector."""
    rng = np.random.default_rng(seed=0)
    v = rng.random(512).astype(np.float32)
    return v / np.linalg.norm(v)


@pytest.fixture()
def fake_detection() -> list[int]:
    """Return a plausible bounding box [x1, y1, x2, y2]."""
    return [50, 60, 200, 250]
