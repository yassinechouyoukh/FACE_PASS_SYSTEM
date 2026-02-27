"""
ai/recognizer/embedding_cache.py
---------------------------------
In-process LRU cache for face embeddings keyed by track ID.

Reduces redundant recognition calls for already-identified tracks.
In a multi-worker deployment consider replacing this with a shared
Redis cache (e.g., redis-py + pickle serialisation).
"""

import logging
from collections import OrderedDict

import numpy as np

logger = logging.getLogger(__name__)

_DEFAULT_MAX_SIZE = 256


class EmbeddingCache:
    """Thread-unsafe LRU embedding cache (single-process use only).

    Args:
        max_size: Maximum number of track embeddings to retain.
                  Oldest entries are evicted when the limit is reached.
    """

    def __init__(self, max_size: int = _DEFAULT_MAX_SIZE) -> None:
        self._cache: OrderedDict[int, np.ndarray] = OrderedDict()
        self._max_size = max_size

    def set(self, track_id: int, embedding: np.ndarray) -> None:
        """Store (or refresh) an embedding for *track_id*."""
        if track_id in self._cache:
            self._cache.move_to_end(track_id)
        self._cache[track_id] = embedding
        if len(self._cache) > self._max_size:
            evicted, _ = self._cache.popitem(last=False)
            logger.debug("Cache evicted track_id=%d (max_size=%d)", evicted, self._max_size)

    def get(self, track_id: int) -> "np.ndarray | None":
        """Return the cached embedding for *track_id*, or ``None``."""
        emb = self._cache.get(track_id)
        if emb is not None:
            self._cache.move_to_end(track_id)  # refresh LRU order
        return emb

    def remove(self, track_id: int) -> None:
        """Explicitly remove a track's cache entry."""
        self._cache.pop(track_id, None)

    def __len__(self) -> int:
        return len(self._cache)
