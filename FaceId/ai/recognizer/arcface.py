"""
ai/recognizer/arcface.py
------------------------
Face embedding extractor using InsightFace's ArcFace (buffalo_l model).

Produces 512-dimensional L2-normalised embeddings suitable for cosine
similarity search.
"""

import logging
import time

import insightface

from configs.settings import settings

logger = logging.getLogger(__name__)


class ArcFaceRecognizer:
    """Extract ArcFace embeddings from a cropped face image.

    Uses InsightFace ``FaceAnalysis`` pipeline with the buffalo_l pack,
    which bundles detection + landmark + recognition models.
    """

    def __init__(self) -> None:
        providers = self._build_providers(settings.device)
        logger.info(
            "Initialising ArcFace (model=%s, providers=%s)",
            settings.arcface_model,
            providers,
        )
        t0 = time.perf_counter()

        self.app = insightface.app.FaceAnalysis(
            name=settings.arcface_model,
            providers=providers,
        )
        self.app.prepare(ctx_id=0 if "CUDA" in providers[0] else -1)

        logger.info("ArcFace ready in %.2fs", time.perf_counter() - t0)

    # ── Public API ──────────────────────────────────────────────────────────

    def embed(self, face_crop) -> "np.ndarray | None":
        """Return a 512-D embedding for the largest face in *face_crop*.

        Args:
            face_crop: BGR numpy array of a cropped face region.

        Returns:
            A ``(512,)`` float32 numpy array, or ``None`` if no face
            is detected inside the crop.
        """
        import numpy as np  # local import to keep module lightweight in tests

        if face_crop is None or face_crop.size == 0:
            logger.debug("embed() received empty crop — skipping")
            return None

        t0 = time.perf_counter()
        try:
            faces = self.app.get(face_crop)
            if not faces:
                logger.debug("No faces detected in crop")
                return None
            emb: np.ndarray = faces[0].embedding
            logger.debug("embed() done in %.1fms", (time.perf_counter() - t0) * 1000)
            return emb
        except Exception:
            logger.exception("Error generating face embedding")
            return None

    # ── Helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _build_providers(device: str) -> list[str]:
        """Map the global device setting to ONNX Runtime providers."""
        if device == "cuda":
            return ["CUDAExecutionProvider", "CPUExecutionProvider"]
        return ["CPUExecutionProvider"]
