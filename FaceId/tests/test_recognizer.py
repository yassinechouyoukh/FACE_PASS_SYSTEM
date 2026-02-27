"""
tests/test_recognizer.py
-------------------------
Unit tests for ArcFaceRecognizer and EmbeddingCache.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


# ── ArcFaceRecognizer ─────────────────────────────────────────────────────────

@patch("ai.recognizer.arcface.insightface")
def test_embed_returns_array(mock_insightface, face_frame):
    """embed() should return a numpy array when a face is detected."""
    dummy_emb = np.random.rand(512).astype(np.float32)
    face_mock = MagicMock()
    face_mock.embedding = dummy_emb

    app_mock = MagicMock()
    app_mock.get.return_value = [face_mock]
    mock_insightface.app.FaceAnalysis.return_value = app_mock

    from ai.recognizer.arcface import ArcFaceRecognizer

    rec = ArcFaceRecognizer()
    result = rec.embed(face_frame)

    assert result is not None
    assert result.shape == (512,)
    assert np.allclose(result, dummy_emb)


@patch("ai.recognizer.arcface.insightface")
def test_embed_returns_none_when_no_face(mock_insightface, blank_frame):
    """embed() should return None if InsightFace finds no faces."""
    app_mock = MagicMock()
    app_mock.get.return_value = []
    mock_insightface.app.FaceAnalysis.return_value = app_mock

    from ai.recognizer.arcface import ArcFaceRecognizer

    rec = ArcFaceRecognizer()
    result = rec.embed(blank_frame)

    assert result is None


@patch("ai.recognizer.arcface.insightface")
def test_embed_handles_empty_crop(mock_insightface):
    """embed() with an empty array should return None without crashing."""
    from ai.recognizer.arcface import ArcFaceRecognizer

    mock_insightface.app.FaceAnalysis.return_value = MagicMock()
    rec = ArcFaceRecognizer()
    result = rec.embed(np.array([]))

    assert result is None


# ── EmbeddingCache ────────────────────────────────────────────────────────────

def test_cache_set_and_get(dummy_embedding):
    from ai.recognizer.embedding_cache import EmbeddingCache

    cache = EmbeddingCache()
    cache.set(1, dummy_embedding)
    result = cache.get(1)

    assert result is not None
    assert np.allclose(result, dummy_embedding)


def test_cache_get_missing_returns_none():
    from ai.recognizer.embedding_cache import EmbeddingCache

    cache = EmbeddingCache()
    assert cache.get(999) is None


def test_cache_lru_eviction(dummy_embedding):
    """Oldest entries should be evicted when max_size is exceeded."""
    from ai.recognizer.embedding_cache import EmbeddingCache

    cache = EmbeddingCache(max_size=2)
    cache.set(1, dummy_embedding)
    cache.set(2, dummy_embedding)
    cache.set(3, dummy_embedding)  # evicts track_id=1

    assert cache.get(1) is None   # evicted
    assert cache.get(2) is not None
    assert cache.get(3) is not None
    assert len(cache) == 2
