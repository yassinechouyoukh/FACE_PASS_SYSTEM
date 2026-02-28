"""
storage/repositories.py
------------------------
Data-access layer for face embeddings.

All methods use the ``get_db()`` context manager so sessions are
properly committed or rolled back and always closed.
"""

from __future__ import annotations

import logging

import numpy as np

from storage.database import get_db
from storage.models import FaceEmbedding

logger = logging.getLogger(__name__)


class EmbeddingRepository:
    """CRUD operations for :class:`~storage.models.FaceEmbedding` records.

    All methods are *static* — no instance state is needed.  Call them
    directly: ``EmbeddingRepository.save(student_id, embedding)``.
    """

    @staticmethod
    def save(student_id: int, embedding: "np.ndarray") -> int:
        logger.debug("Saving embedding for student_id=%d", student_id)

        with get_db() as db:
            record = FaceEmbedding(
                student_id=student_id,
                embedding=embedding.tolist(),
            )
            db.add(record)
            db.flush()  # get auto-generated id

            saved_id = record.face_id  # ← store it before session closes

            logger.info(
                "Saved embedding id=%d for student_id=%d",
                saved_id,
                student_id,
            )

            return saved_id   # ✅ return only the id

    @staticmethod
    def get_all() -> list[dict]:
        with get_db() as db:
            records = db.query(FaceEmbedding).all()

            # Convert BEFORE session closes
            return [
                {
                    "student_id": r.student_id,
                    "embedding": r.embedding,
                }
                for r in records
            ]

    @staticmethod
    def get_by_student(student_id: int) -> list[dict]:
        with get_db() as db:
            records = (
                db.query(FaceEmbedding)
                .filter(FaceEmbedding.student_id == student_id)
                .all()
            )

            # Convert to simple dict BEFORE session closes
            return [
                {
                    "face_id": r.face_id,
                    "student_id": r.student_id
                }
                for r in records
            ]

    @staticmethod
    def delete_by_student(student_id: int) -> int:
        """Delete all embeddings for *student_id*.

        Args:
            student_id: Student whose embeddings should be removed.

        Returns:
            Number of rows deleted.
        """
        with get_db() as db:
            count: int = (
                db.query(FaceEmbedding)
                .filter(FaceEmbedding.student_id == student_id)
                .delete(synchronize_session=False)
            )
        logger.info("Deleted %d embeddings for student_id=%d", count, student_id)
        return count
