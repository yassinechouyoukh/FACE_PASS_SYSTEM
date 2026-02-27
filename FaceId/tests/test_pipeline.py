"""
tests/test_pipeline.py
-----------------------
Integration-style tests for FacePipeline.

All heavy models are mocked so the pipeline logic — stage chaining,
error handling, and output structure — is tested without GPU.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


def _build_mock_pipeline():
    """Return a FacePipeline with all sub-components mocked."""
    from ai.pipeline import FacePipeline

    p = FacePipeline.__new__(FacePipeline)
    p.frame_id = 0

    # Mock detector: always returns one box
    p.detector = MagicMock()
    p.detector.detect.return_value = [[50, 60, 200, 250]]

    # Mock tracker: wraps box in a Track-like object
    from ai.types import Track

    track = Track(track_id=1, bbox=np.array([50, 60, 200, 250]), last_seen=0.0)
    p.tracker = MagicMock()
    p.tracker.update.return_value = [track]

    # Mock recognizer: returns a dummy embedding
    dummy_emb = np.random.rand(512).astype(np.float32)
    p.recognizer = MagicMock()
    p.recognizer.embed.return_value = dummy_emb

    # Mock cache
    p.cache = MagicMock()
    p.cache.get.return_value = dummy_emb

    return p


@patch("ai.pipeline.cosine_search", return_value=None)
@patch("ai.pipeline.estimate_pose", return_value=(5.0, 3.0, 1.0))
@patch("ai.pipeline.compute_engagement", return_value="high")
def test_process_returns_list(mock_eng, mock_pose, mock_search, blank_frame):
    """process() should return a non-empty list for a frame with a face."""
    p = _build_mock_pipeline()
    results = p.process(blank_frame)

    assert isinstance(results, list)
    assert len(results) == 1


@patch("ai.pipeline.cosine_search", return_value=None)
@patch("ai.pipeline.estimate_pose", return_value=(5.0, 3.0, 1.0))
@patch("ai.pipeline.compute_engagement", return_value="high")
def test_process_output_has_required_keys(mock_eng, mock_pose, mock_search, blank_frame):
    """Each result dict must contain all required keys."""
    p = _build_mock_pipeline()
    results = p.process(blank_frame)
    required = {"track_id", "bbox", "student_id", "confidence", "pitch", "yaw", "roll", "engagement"}
    assert required.issubset(set(results[0].keys()))


@patch("ai.pipeline.cosine_search", return_value=None)
@patch("ai.pipeline.estimate_pose", return_value=(0.0, 0.0, 0.0))
@patch("ai.pipeline.compute_engagement", return_value="high")
def test_process_returns_empty_on_no_detections(mock_eng, mock_pose, mock_search, blank_frame):
    """process() should return [] when detector finds no faces."""
    p = _build_mock_pipeline()
    p.detector.detect.return_value = []
    p.tracker.update.return_value = []

    results = p.process(blank_frame)
    assert results == []


@patch("ai.pipeline.cosine_search", side_effect=Exception("DB error"))
@patch("ai.pipeline.estimate_pose", return_value=(0.0, 0.0, 0.0))
@patch("ai.pipeline.compute_engagement", return_value="low")
def test_process_is_resilient_to_search_errors(mock_eng, mock_pose, mock_search, blank_frame):
    """process() should return [] (not raise) when downstream errors occur."""
    p = _build_mock_pipeline()
    results = p.process(blank_frame)
    # Any exception inside process() is caught and logged; returns []
    assert isinstance(results, list)
