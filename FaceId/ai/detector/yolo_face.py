"""
ai/detector/yolo_face.py
------------------------
YOLO-based face detector wrapping a custom-trained YOLO model.

Loads the model using the native ultralytics API, with
automatic CPU fallback if CUDA is unavailable.
"""

import logging
import time

import torch
from ultralytics import YOLO  # <-- We import the modern API here

from configs.settings import settings

logger = logging.getLogger(__name__)


class YOLOFaceDetector:
    """Detect faces in an image frame using a custom YOLO model.

    Args:
        model_path: Optional path override. Defaults to the versioned
                    path from ``settings.model_path``.
    """

    def __init__(self, model_path: str | None = None):
        t0 = time.perf_counter()

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🔥 YOLO running on device: {self.device}")

        model_path = model_path or "models/v1/yolo_face.pt"

        self.model = YOLO(model_path)

        # Force model to GPU
        self.model.to(self.device)

        self.conf_threshold = settings.detection_conf_threshold
        self.input_size = settings.detection_input_size

        elapsed = time.perf_counter() - t0
        logger.info("YOLO model loaded in %.2fs", elapsed)

    # ── Public API ──────────────────────────────────────────────────────────

    def detect(self, frame) -> list[list[int]]:
        """Run inference on *frame* and return bounding boxes.

        Args:
            frame: BGR numpy array (H × W × 3).

        Returns:
            List of ``[x1, y1, x2, y2]`` integer bounding boxes for
            detections above the confidence threshold.
        """
        t0 = time.perf_counter()
        try:
            # <-- Updated inference logic to match the new API -->
            results = self.model(
                frame,
                imgsz=self.input_size,
                conf=self.conf_threshold,
                device=self.device,   # 🔥 IMPORTANT
                verbose=False
            )
            
            boxes: list[list[int]] = []
            if len(results) > 0:
                for box in results[0].boxes:
                    boxes.append(list(map(int, box.xyxy[0].tolist())))

            logger.debug(
                "detect() → %d faces in %.1fms",
                len(boxes),
                (time.perf_counter() - t0) * 1000,
            )
            return boxes
        except Exception:
            logger.exception("Error during face detection")
            return []

    # ── Helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _resolve_device(requested: str) -> str:
        """Return *requested* device if available, else fall back to CPU."""
        if requested == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA not available — falling back to CPU")
            return "cpu"
        return requested