"""
storage/vector_search.py
-------------------------
Cosine similarity search over stored face embeddings.

Primary backend: **pgvector** (PostgreSQL extension).
Fallback:        Pure NumPy brute-force search — used automatically when
                 the database is unavailable (development, CI, unit tests).

pgvector SQL note
-~~~~~~~~~~~~~~~~
``<=>`` is the pgvector cosine-distance operator.  Distance 0 = identical,
distance 2 = opposite direction.  We keep results where distance ≤
``settings.sim_threshold``.
"""

from __future__ import annotations

import logging
import time
from typing import Any, NamedTuple

import numpy as np
from sqlalchemy import text

from configs.settings import settings
from storage.database import SessionLocal

logger = logging.getLogger(__name__)


class SearchResult(NamedTuple):
    """Result of a nearest-neighbour search."""

    student_id: int
    d: float          # cosine distance (0 = identical, lower = better)


# ── pgvector search ───────────────────────────────────────────────────────────

_COSINE_SQL = text(
    """
    SELECT student_id,
           embedding <=> CAST(:v AS vector) AS distance
    FROM   face_embedding
    ORDER  BY distance
    LIMIT  1
    """
)


def cosine_search(vector: np.ndarray) -> SearchResult | None:
    """Find the closest stored embedding to *vector* using cosine distance.

    Tries pgvector first; falls back to NumPy brute-force if the query
    fails (e.g., no database connection or pgvector not installed).

    Args:
        vector: 512-D float32 query embedding.

    Returns:
        A :class:`SearchResult` with the nearest ``student_id`` and its
        cosine distance, or ``None`` if no embeddings are stored.
    """
    t0 = time.perf_counter()
    result = _pgvector_search(vector) or _numpy_fallback_search(vector)
    elapsed = (time.perf_counter() - t0) * 1000
    if result:
        logger.debug(
            "cosine_search → student_id=%s d=%.4f in %.1fms",
            result.student_id, result.d, elapsed,
        )
    else:
        logger.debug("cosine_search → no match found (%.1fms)", elapsed)
    return result


def _pgvector_search(vector: np.ndarray) -> SearchResult | None:
    """Run the pgvector SQL search. Returns None on any DB error."""
    db = SessionLocal()
    try:
        row = db.execute(_COSINE_SQL, {"v": vector.tolist()}).fetchone()
        if row is None:
            return None
        return SearchResult(student_id=int(row[0]), d=float(row[1]))
    except Exception:
        logger.warning("pgvector search failed — falling back to NumPy", exc_info=True)
        return None
    finally:
        db.close()


def _numpy_fallback_search(vector: np.ndarray) -> SearchResult | None:
    """Brute-force cosine search over all stored embeddings using NumPy.

    O(n) — acceptable for small datasets (<10 k embeddings).
    For large datasets consider FAISS (see note below).

    .. note::
        **FAISS upgrade path**: replace this function body with:

        .. code-block:: python

            import faiss
            index = faiss.IndexFlatIP(512)   # inner product on L2-norm vecs
            # index.add(all_embeddings)       # rebuild at startup
            q = vector / np.linalg.norm(vector)
            D, I = index.search(q[None], k=1)
            return SearchResult(student_id=ids[I[0][0]], d=1.0 - D[0][0])
    """
    from storage.repositories import EmbeddingRepository  # avoid circular at top

    records = EmbeddingRepository.get_all()
    if not records:
        return None

    query = vector / (np.linalg.norm(vector) + 1e-8)
    best_d = float("inf")
    best_sid: int | None = None

    for rec in records:
        emb = np.array(rec.embedding, dtype=np.float32)
        emb = emb / (np.linalg.norm(emb) + 1e-8)
        d = float(1.0 - np.dot(query, emb))
        if d < best_d:
            best_d = d
            best_sid = rec.student_id

    if best_sid is None:
        return None
    return SearchResult(student_id=best_sid, d=best_d)
